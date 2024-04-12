'''
Author: Shaogui
Date: 2023-06-01 11:15:27
Description: 
'''
import os
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox

def selectPath(choice_path):
    '''selectPath 弹窗选择文件目录
    '''
    path_ = askdirectory() #使用askdirectory()方法返回文件夹的路径
    if path_ == "":
        choice_path.get() #当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
    else:
        path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
        choice_path.set(path_)

def openPath(choice_path):
    '''openPath 使用文件管理器打开目录
    '''
    dir = os.path.dirname(choice_path+"\\")
    os.system('start ' + dir)
    #print(dir)

def showHelp():
    messagebox.showinfo('提示',
                        '窗口宽/高：表示展平时处理的窗口大小，稍微比缺陷size大一点即可\n\n窗口阈值：表示缺陷与周围的高度差值，和实际缺陷与周围高度差接近即可\n\n以上两个值越大运行速度越慢，设置的参数要求让缺陷可见、明显')