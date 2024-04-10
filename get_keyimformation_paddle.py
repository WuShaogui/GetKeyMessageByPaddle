import os.path as osp
from PIL import Image
import numpy as np
import cv2
import datetime

from paddleocr import PaddleOCR,draw_ocr
from paddlenlp import Taskflow

from pdf2image import convert_from_path

class ReadDocument:
    def __init__(self,schema:list=["甲方","乙方","总价","金额"]):
        self.schema=schema
        self.ocr_client=None
        self.nlp_client=None

        self.load()
    
    def load(self):
        self.ocr_client = PaddleOCR(use_angle_cls=False, lang="ch", det_db_box_thresh=0.3, use_dilation=True,show_log=False)
        self.nlp_client = Taskflow('information_extraction', schema=self.schema)
        self.nlp_client .set_schema(self.schema)
    
    def read_context_from_image(self,image:np.array,is_draw:bool=False,save_path='./'):
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

        if is_draw:
            im_show = draw_ocr(image, boxes, txts, scores, font_path='./simfang.ttf')
            im_show = Image.fromarray(im_show)
            vis = np.array(im_show)
            cv2.imwrite(osp.join(save_path,str(datetime.datetime.now())+'.png'),vis.astype(np.uint8))         

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

    def analyze_images(self,images,is_draw:bool=False,save_path='./'):
        # 1.从所有图片读取文本
        all_context=[]
        for i,image in enumerate(images):
            context=self.read_context_from_image(image,is_draw,save_path)
            all_context.append(context)

        # 2.从所有文本识别关键信息
        all_context='\n'.join(all_context)
        all_key_imformation = self.get_keyinformation_from_context(all_context)

        return all_key_imformation

    def convert_pdf_to_images(self,pdf_path:str):
        assert osp.exists(pdf_path),print(f'{pdf_path} is not found')

        images = convert_from_path(pdf_path)
        images=list(map(lambda image:np.array(image)[...,::-1],images))

        return images
        
    def analyze_pdf(self,pdf_path:str,is_draw:bool=False,save_path='./'):
        images=self.convert_pdf_to_images(pdf_path)
        all_key_imformation=self.analyze_images(images,is_draw,save_path)

        return all_key_imformation
    
    def filter_key_imformation(self,all_key_imformation):
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
        






if __name__ == '__main__':
    rd=ReadDocument()

    # 识别多张图片
    # images_path=['test_img/hetong1.jpeg','test_img/hetong2.jpg','test_img/hetong3.jpg','test_img/homework.png']
    # images=list(map(lambda image_path:cv2.imread(image_path,cv2.IMREAD_COLOR), images_path))
    # all_key_imformation=rd.analyze_images(images)

    # 识别pdf
    pdf_path='test_pdf/hetong1.pdf'
    all_key_imformation=rd.analyze_pdf(pdf_path,is_draw=False)

    print(all_key_imformation)
    all_key_imformation=rd.filter_key_imformation(all_key_imformation)
    print(all_key_imformation)

    for i,se in enumerate(all_key_imformation[0]):
        print(se)
        for ki in all_key_imformation[0][se]:
            print(ki)
        print('---------'*5)




