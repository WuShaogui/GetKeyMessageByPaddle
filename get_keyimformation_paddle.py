import os.path as osp
from time import sleep
import time
from PIL import Image
import numpy as np
import cv2
import datetime
import glob
import csv
import os

import paddle
from paddleocr import PaddleOCR,draw_ocr
from paddlenlp import Taskflow

from pdf2image import convert_from_path

from utils import openPath

class ReadDocument:
    def __init__(self,tkroot):
        self.tkroot=tkroot
        self.schema=""
        self.ocr_client=None
        self.nlp_client=None
    
    def check_env(self):
       return paddle.device.is_compiled_with_cuda()

    def load(self,schema):
        self.tkroot.disabled_gui()
        self.tkroot.init_ai_str.set("正在初始化AI...")
        self.tkroot.update()
    
        # 使用新的schema初始化
        if self.schema=="" or schema!=self.schema:

            if self.ocr_client!=None:del self.ocr_client
            if self.nlp_client!=None:del self.nlp_client

            self.schema=schema
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
                home_path='./models/nlp',
                show_log=False)
            self.nlp_client.set_schema(self.schema.split(','))
        else:
            print("该schema的AI环境已经被初始化，可点击识别处理文件")
        
        self.tkroot.enable_gui()
        self.tkroot.init_ai_str.set("AI环境已加载")
        self.tkroot.tk_label_init_ai['background']="#b2f2bb"
        self.tkroot.update()
        
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

        images = convert_from_path(osp.abspath(pdf_path),poppler_path=r'./poppler-24.02.0/Library/bin')
        images=list(map(lambda image:np.array(image)[...,::-1],images))

        return images
    
    def analyze_pdfs(self,
                     pdfs_dir:str,
                     save_csv_dir,
                     is_draw:bool=False,                # 是否将OCR结果绘制出来
                     is_filter:bool=True                # 是否过滤结果 
                     ):
        '''从一批pdf文件中提取关键信息

        Parameters
        ----------
        pdfs_dir : list(str)
            psf文件夹路径
        save_csv_dir : str, optional
            所有pdf的关键信息保存的csv路径, by default 'output.csv'
        '''
        print("开始识别pdf......")
        print(f'pdfs_dir:{pdfs_dir}\nsave_csv_dir:{save_csv_dir}\nis_draw:{is_draw}\nis_filter:{is_filter}')

        self.tkroot.disabled_gui()
        self.tkroot.now_progress.set(0)
        self.tkroot.tk_button_stop['state']="enable"
        self.tkroot.update()

        if self.ocr_client==None or self.nlp_client==None:
            print('AI环境未初始化')
            self.tkroot.enable_gui()
            self.tkroot.tk_button_stop['state']="disable"
            self.tkroot.update()
            return

        self.is_draw=is_draw
        if self.is_draw:
            self.save_ocr_dir=osp.join(save_csv_dir,str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
            # os.mkdir(f'./{self.save_ocr_dir}')
            os.mkdir(self.save_ocr_dir)
        self.is_filter=is_filter

        # 遍历所有pdf，提取关键信息
        self.pdfs_path=glob.glob(osp.join(pdfs_dir,'*.pdf'))
        pdfs_num=len(self.pdfs_path)
        if pdfs_num==0:
            print("未找到pdf文件")
        
        num_success=0
        error_list=[]
        self.pdfs_all_key_imformation={}
        for pdfId,pdf_path in enumerate(self.pdfs_path):
            # 判断是否有停止操作
            if not self.tkroot.event.is_set():
                try:
                    start=time.time()
                    
                    images=self.convert_pdf_to_images(pdf_path)
                    all_key_imformation=self.analyze_images(images,osp.splitext(osp.basename(pdf_path))[0])
                    # 是否过滤结果
                    if self.is_filter:
                        self.pdfs_all_key_imformation[pdfId]=self.filter_key_imformation(all_key_imformation)
                    else:
                        self.pdfs_all_key_imformation[pdfId]=all_key_imformation
                    
                    end=time.time()
                    cost=end-start
                    print('进度{}/{} 图片:{} 耗时:{:.1f}s'.format(pdfId+1,pdfs_num,pdf_path,cost))
                    num_success+=1

                except Exception as e:
                    self.tkroot.show_log.set(">>>提取失败！")
                    error_list.append(pdf_path)
                
                run_process=int(pdfId/pdfs_num*100)
                self.tkroot.show_log.set("发现tif：{}\n展平成功：{}\n展平失败：{}\n展平进度：{}%".format(pdfs_num,num_success,len(error_list),run_process))
                self.tkroot.now_progress.set(run_process)
                self.tkroot.update()
            else:
                break

        self.save_result_to_csv(save_csv_dir)

        if self.tkroot.event.is_set():
            print('>>>手动终止')
        else:
            self.tkroot.show_log.set("发现pdf：{}\n提取成功：{}\n提取失败：{}\n提取进度：{}%".format(pdfs_num,num_success,len(error_list),100))
            self.tkroot.now_progress.set(100)

            # 打开输出目录
            if(num_success>0):
                openPath(save_csv_dir)
            print('>>>处理完成！')
            if(len(error_list)>0):
                print('以下文件转换失败，请确认：\n{}'.format('\n'.join(error_list)))
        
        self.tkroot.enable_gui()
        self.tkroot.tk_button_stop['state']="disable"
        self.tkroot.update()

    
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
    
    def save_result_to_csv(self,csv_save_dir):
        '''将AI识别结果汇总到csv

        Parameters
        ----------
        csv_save_dir : str
            csv保存路径
        '''
        # 构造csv的表头及内容
        csv_header = ['文件名']+self.schema.split(',')
        csv_content =[]
        for pdfId in self.pdfs_all_key_imformation:
            all_key_imformation=self.filter_key_imformation(self.pdfs_all_key_imformation[pdfId])
            pdf_content=[self.pdfs_path[pdfId]]
            for se in self.schema.split(','):
                se_text=[]
                if se in all_key_imformation[0]:
                    for ki in all_key_imformation[0][se]:
                        se_text.append(ki['text'])
                pdf_content.append('\n'.join(se_text))
            csv_content.append(pdf_content)

        # 打开文件并写入数据
        csv_save_path=osp.join(csv_save_dir,'output.csv')
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
    pdfs_dir='.\\test_pdf'
    pdfs_path=glob.glob(osp.join(pdfs_dir,'*.pdf'))
    print('pdf count:',len(pdfs_path))
    print(pdfs_path)

    rd.analyze_pdfs(pdfs_path)
    
    

