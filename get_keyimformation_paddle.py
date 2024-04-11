import os.path as osp
from PIL import Image
import numpy as np
import cv2
import datetime
import glob
import csv
import os

from paddleocr import PaddleOCR,draw_ocr
from paddlenlp import Taskflow

from pdf2image import convert_from_path

class ReadDocument:
    def __init__(self,
                 schema:list=["甲方","乙方","总价","金额","总计"],  # 待搜索的关键信息
                 is_draw:bool=False,                             # 是否将OCR结果绘制出来
                ):
        self.schema=schema
        self.is_draw=is_draw
        if self.is_draw:
            self.save_ocr_dir=str(datetime.datetime.now())
            os.mkdir(f'./{self.save_ocr_dir}')           

        self.ocr_client=None
        self.nlp_client=None

        self.load()
    
    def load(self):
        self.ocr_client = PaddleOCR(
            use_angle_cls=False, 
            lang="ch", 
            det_db_box_thresh=0.3, 
            det_model_dir='./models/ocr/det',
            rec_model_dir='./models/ocr/rec',
            cls_model_dir='./models/ocr/cls',
            use_dilation=True,
            show_log=False)
        self.nlp_client = Taskflow(
            task='information_extraction', 
            schema=self.schema,
            home_path='./models/nlp')
        self.nlp_client.set_schema(self.schema)
    
    def read_context_from_image(self,image:np.array,image_name:str=''):
        '''用cor模型识别出其中的文字

        Parameters
        ----------
        image : np.array
            图片
        is_draw : bool, optional
            是否绘制识别结果, by default False
        save_path : str, optional
            识别结果保存位置, by default './'

        Returns
        -------
        str
            所有识别到的文本
        '''
        if(image.shape[-1]==3):
            image=image[...,-1] # 拿到红色通道图片
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        result= self.ocr_client.ocr(image, cls=False)
        if result==None or len(result[0])==0:
            print('not found context in images')
            return
        
        boxes = [line[0] for line in result[0]]
        txts = [line[1][0] for line in result[0]]
        scores = [line[1][1] for line in result[0]]

        if self.is_draw:
            im_show = draw_ocr(image, boxes, txts, scores, font_path='./simfang.ttf')
            im_show = Image.fromarray(im_show)
            vis = np.array(im_show)

            # 保存ocr结果
            cv2.imwrite(osp.join(self.save_ocr_dir,image_name+'.png'),vis.astype(np.uint8))         

        context = "\n".join(txts)
        return context

    def get_keyinformation_from_context(self,context:str):
        '''基于ocr提取的文本进行关键字提取

        Parameters
        ----------
        context : str
            ocr提取的文本

        Returns
        -------
        list
            提取的关键信息
        '''
        assert context!="",print('context is null')
        result=self.nlp_client(context)

        return result

    def analyze_images(self,images,pdf_name=''):
        '''从一批图像提取关键信息

        Parameters
        ----------
        images : list(np.array)
            一批图像
        pdf_name:pdf文件名称

        Returns
        -------
        _type_
            关键信息
        '''
        # 1.从所有图片读取文本
        all_context=[]
        for i,image in enumerate(images):
            image_name=f'{pdf_name}-{i}'
            context=self.read_context_from_image(image,image_name)
            all_context.append(context)

        # 2.从所有文本识别关键信息
        all_context='\n'.join(all_context)
        all_key_imformation = self.get_keyinformation_from_context(all_context)

        return all_key_imformation

    def convert_pdf_to_images(self,pdf_path:str):
        '''从pdf文件读取出图片

        Parameters
        ----------
        pdf_path : str
            pdf文件位置

        Returns
        -------
        np.array
            图片
        '''
        assert osp.exists(pdf_path),print(f'{pdf_path} is not found')

        images = convert_from_path(pdf_path)
        images=list(map(lambda image:np.array(image)[...,::-1],images))

        return images
        
    def analyze_pdfs(self,pdfs_path:str,csv_save_path='output.csv'):
        '''从一批pdf文件中提取关键信息

        Parameters
        ----------
        pdfs_path : list(str)
            所有psf文件路径
        csv_save_path : str, optional
            所有pdf的关键信息保存的csv路径, by default 'output.csv'
        '''
        # 遍历所有pdf，提取关键信息
        self.pdfs_all_key_imformation={}
        for pdfId,pdf_path in enumerate(pdfs_path):
            images=self.convert_pdf_to_images(pdf_path)
            all_key_imformation=self.analyze_images(images,osp.splitext(osp.basename(pdf_path))[0])
            self.pdfs_all_key_imformation[pdfId]=all_key_imformation
        
        self.save_result_to_csv(csv_save_path)
    
    def filter_key_imformation(self,all_key_imformation):
        '''预测结果有比较多重复的，执行两个过滤，相当于目标检测的nms

        Parameters
        ----------
        all_key_imformation : list
            AI提取的关键信息

        Returns
        -------
        list
            过滤后的结果
        '''
        # 同一se内，如果存在同一text结果，保留概率高的
        for i,se in enumerate(all_key_imformation[0]):
            new_se_key_imformation=[]
            for ki in all_key_imformation[0][se]:
                for ki2 in all_key_imformation[0][se]:
                    # 排除已经添加的
                    is_add=False
                    new_se_key_imformation_text=list(map(lambda kk:kk['text'],new_se_key_imformation))
                    if ki['text'] in new_se_key_imformation_text:is_add=True
                    # 选择概率最大的
                    if ki['text']==ki2['text'] and not is_add:
                        if ki['probability']>ki2['probability']:
                            new_se_key_imformation.append(ki)
                        else:
                            new_se_key_imformation.append(ki2)
            all_key_imformation[0][se]=new_se_key_imformation
        
        # 不同的se内，如果存在同一text结果，保留概率高的
        for i,se in enumerate(all_key_imformation[0]):
            new_se_key_imformation=[]
            for ki in all_key_imformation[0][se]:
                is_only=True
                for i,se2 in enumerate(all_key_imformation[0]):
                    if se==se2:continue
                    for ki2 in all_key_imformation[0][se2]:
                        # 排除已经添加的
                        is_add=False
                        new_se_key_imformation_text=list(map(lambda kk:kk['text'],new_se_key_imformation))
                        if ki['text'] in new_se_key_imformation_text:is_add=True
                        # 选择概率最大的
                        if ki['text']==ki2['text'] and not is_add:
                            is_only=False
                            if ki['probability']>ki2['probability']:
                                new_se_key_imformation.append(ki)
                            else:
                                continue
                if is_only:
                    new_se_key_imformation.append(ki)
            all_key_imformation[0][se]=new_se_key_imformation
        
        return all_key_imformation
    
    def save_result_to_csv(self,csv_save_path):
        '''将AI识别结果汇总到csv

        Parameters
        ----------
        csv_save_path : str
            csv保存路径
        '''
        # 构造csv的表头及内容
        csv_header = ['文件名']+self.schema
        csv_content =[]
        for pdfId in self.pdfs_all_key_imformation:
            all_key_imformation=rd.filter_key_imformation(self.pdfs_all_key_imformation[pdfId])
            pdf_content=[pdfs_path[pdfId]]
            for se in schema:
                se_text=[]
                if se in all_key_imformation[0]:
                    for ki in all_key_imformation[0][se]:
                        se_text.append(ki['text'])
                pdf_content.append('\n'.join(se_text))
            csv_content.append(pdf_content)

        # 打开文件并写入数据
        with open(csv_save_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)  # 写入表头
            for row in csv_content:
                writer.writerow(row)  # 写入数据


if __name__ == '__main__':
    schema=["甲方","乙方","总价","金额","总计"]
    rd=ReadDocument(schema,is_draw=True)

    # 识别多张图片
    # images_path=['test_img/hetong1.jpeg','test_img/hetong2.jpg','test_img/hetong3.jpg','test_img/homework.png']
    # images=list(map(lambda image_path:cv2.imread(image_path,cv2.IMREAD_COLOR), images_path))
    # all_key_imformation=rd.analyze_images(images)

    # 识别1份pdf
    # pdf_path='test_pdf/hetong9.pdf'
    # all_key_imformation=rd.analyze_pdf(pdf_path,is_draw=False)

    # print(all_key_imformation)
    # all_key_imformation=rd.filter_key_imformation(all_key_imformation)
    # print(all_key_imformation)

    # for i,se in enumerate(all_key_imformation[0]):
    #     print(se)
    #     for ki in all_key_imformation[0][se]:
    #         print(ki)
    #     print('---------'*5)

    # 识别1批pdf
    pdfs_dir='/home/wushaogui/MyCodes/GetKeyMessageByPaddle/test_pdf'
    pdfs_path=glob.glob(osp.join(pdfs_dir,'*.pdf'))
    print('pdf count:',len(pdfs_path))

    rd.analyze_pdfs(pdfs_path)
    
    

