"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
import os
import random
import threading
from time import sleep
from tkinter import *
from tkinter.ttk import *

from get_keyimformation_paddle import ReadDocument
from utils import selectPath, showHelp

class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_label_luunb0ue = self.__tk_label_luunb0ue(self)
        self.tk_label_luunc6xs = self.__tk_label_luunc6xs(self)
        self.tk_input_pdfs_dir = self.__tk_input_pdfs_dir(self)
        self.tk_input_save_csv_dir = self.__tk_input_save_csv_dir(self)
        self.tk_button_pdfs_dir = self.__tk_button_pdfs_dir(self)
        self.tk_button_save_csv_dir = self.__tk_button_save_csv_dir(self)
        self.tk_progressbar_luuo1leo = self.__tk_progressbar_luuo1leo(self)
        self.tk_label_show_log = self.__tk_label_show_log(self)
        self.tk_button_run = self.__tk_button_run(self)
        self.tk_button_stop = self.__tk_button_stop(self)
        self.tk_label_luuo4czu = self.__tk_label_luuo4czu(self)
        self.tk_input_schema = self.__tk_input_schema(self)
        self.tk_button_initAI = self.__tk_button_initAI(self)
        self.tk_check_button_is_draw = self.__tk_check_button_is_draw(self)
        self.tk_check_button_is_filter = self.__tk_check_button_is_filter(self)
        self.tk_label_check_env = self.__tk_label_check_env(self)
        self.tk_label_init_ai = self.__tk_label_init_ai(self)

    def __win(self):
        self.title("合同关键性信息提取助手")
        # 设置窗口大小、居中
        width = 616
        height = 444
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)
        self.event = threading.Event()
        self.rd=ReadDocument(self)
        self.env=self.rd.check_env()
        
    def scrollbar_autohide(self,vbar, hbar, widget):
        """自动隐藏滚动条"""
        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)
        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)
        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())
    
    def v_scrollbar(self,vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')
    def h_scrollbar(self,hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')
    def create_bar(self,master, widget,is_vbar,is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)
    def __tk_label_luunb0ue(self,parent):
        label = Label(parent,text="合同文件夹地址",anchor="center", )
        label.place(x=48, y=102, width=96, height=30)
        return label
    def __tk_label_luunc6xs(self,parent):
        label = Label(parent,text="关键信息保存位置",anchor="center", )
        label.place(x=28, y=156, width=113, height=30)
        return label
    def __tk_input_pdfs_dir(self,parent):
        self.pdfs_dir = StringVar()
        self.pdfs_dir.set(os.path.abspath("."))
        ipt = Entry(parent,textvariable=self.pdfs_dir)
        ipt.place(x=155, y=102, width=346, height=30)
        return ipt
    def __tk_input_save_csv_dir(self,parent):
        self.save_csv_dir = StringVar()
        self.save_csv_dir.set(os.path.abspath("."))
        ipt = Entry(parent,textvariable=self.save_csv_dir)
        ipt.place(x=153, y=160, width=346, height=30)
        return ipt
    def __tk_button_pdfs_dir(self,parent):
        btn = Button(parent, text="选择路径", command=lambda:selectPath(self.pdfs_dir), takefocus=False,)
        btn.place(x=529, y=103, width=60, height=30)
        return btn
    def __tk_button_save_csv_dir(self,parent):
        btn = Button(parent, text="选择路径", command=lambda:selectPath(self.save_csv_dir), takefocus=False,)
        btn.place(x=529, y=160, width=60, height=30)
        return btn
    def __tk_progressbar_luuo1leo(self,parent):
        self.now_progress = IntVar()
        self.now_progress.set(0)
        progressbar = Progressbar(parent, orient=HORIZONTAL,variable=self.now_progress)
        progressbar.place(x=23, y=253, width=557, height=30)
        return progressbar
    def __tk_label_show_log(self,parent):
        self.show_log=StringVar();
        label = Label(parent,text="",anchor="center",textvariable=self.show_log )
        label.place(x=28, y=301, width=152, height=119)
        return label 
    
    def __tk_label_check_env(self,parent):
        self.check_env_str=StringVar()
        if self.rd.check_env():
            self.check_env_str.set("GPU")
            label = Label(parent,foreground="#1e1e1e",background='#b2f2bb',relief='groove',
                      font=('Arial',15,'bold'),anchor="center",textvariable=self.check_env_str,state='disable' )
        else:
            self.check_env_str.set("CPU")
            label = Label(parent,foreground="#1e1e1e",background='#e9ecef',relief='groove',
                      font=('Arial',15,'bold'),anchor="center",textvariable=self.check_env_str,state='disable' )
        
        label.place(x=550, y=410, width=70, height=30)
        return label
    
    def analyzePdfs(self):
        # Call work function
        self.event.clear()
        t=threading.Thread(target=self.rd.analyze_pdfs, args=(self.pdfs_dir.get(),self.save_csv_dir.get(),
                                                              self.is_draw.get(),self.is_filter.get()))
        t.start()

    def __tk_button_run(self,parent):
        btn = Button(parent, text="开始识别",command=lambda:[self.analyzePdfs()], takefocus=False,)
        btn.place(x=200, y=340, width=87, height=47)
        return btn
    
    def stop_task(self):
        self.event.set()
    def __tk_button_stop(self,parent):
        btn = Button(parent, text="停止识别",command=self.stop_task, takefocus=False,state='disable')
        btn.place(x=350, y=340, width=87, height=47)
        return btn
    
    def enable_gui(self):
        # 恢复界面
        self.tk_button_pdfs_dir['state']="enable"
        self.tk_button_save_csv_dir['state']='enable'
        self.tk_button_initAI['state']="enable"
        self.tk_input_pdfs_dir['state']="enable"
        self.tk_input_save_csv_dir['state']="enable"
        self.tk_label_show_log['state']="enable"
        self.tk_button_run['state']="enable"
        self.tk_button_stop['state']="disable"
        self.tk_input_schema['state']="enable"
        self.tk_check_button_is_draw['state']="enable"
        self.tk_check_button_is_filter['state']="enable"

    def disabled_gui(self):
        # 每次点击转换，界面禁止操作
        self.show_log.set("")
        self.tk_button_pdfs_dir['state']="disable"
        self.tk_button_save_csv_dir['state']='disable'
        self.tk_button_initAI['state']="disable"
        self.tk_input_pdfs_dir['state']="disable"
        self.tk_input_save_csv_dir['state']="disable"
        # self.tk_label_show_log['state']="disable"
        self.tk_button_run['state']="disable"
        self.tk_input_schema['state']="disable"
        self.tk_check_button_is_draw['state']="disable"
        self.tk_check_button_is_filter['state']="disable"

    def __tk_label_luuo4czu(self,parent):
        label = Label(parent,text="需要提取的关键字",anchor="center", )
        label.place(x=24, y=36, width=118, height=30)
        return label
    def __tk_input_schema(self,parent):
        self.schema = StringVar()
        self.schema.set("甲方,乙方,金额")
        ipt = Entry(parent,textvariable=self.schema)
        ipt.place(x=154, y=35, width=345, height=30)
        return ipt
    
    def __tk_label_init_ai(self,parent):
        self.init_ai_str=StringVar(value="请点击初始化AI")
        label = Label(parent,foreground="#1e1e1e",background='#e9ecef',relief='groove',
                      font=('Arial',15,'bold'),anchor="center",textvariable=self.init_ai_str)
        label.place(x=400, y=410, width=150, height=30)
        return label   
    
    def initAI(self):
        if self.schema.get()!="":
            self.rd.load(self.schema.get())
        else:
            self.show_log.set(">>>请填写要提取的关键词")

    def __tk_button_initAI(self,parent):
        btn = Button(parent, text="初始化AI",command=lambda:[self.initAI()], takefocus=False,)
        btn.place(x=529, y=38, width=60, height=30)
        return btn
    
    def __tk_check_button_is_filter(self,parent):
        self.is_filter = BooleanVar(value=True)
        cb = Checkbutton(parent,text="是否过滤AI结果", variable=self.is_filter)
        cb.place(x=300, y=210, width=144, height=30)
        return cb
    
    def __tk_check_button_is_draw(self,parent):
        self.is_draw = BooleanVar()
        cb = Checkbutton(parent,text="是否保存文本提取结果", variable=self.is_draw)
        cb.place(x=151, y=210, width=144, height=30)
        return cb
    
class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)
    def __event_bind(self):
        pass
    def __style_config(self):
        pass
if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()