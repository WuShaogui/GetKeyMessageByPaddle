# -*- encoding: utf-8 -*-
"""
@File    :   my_read_code_tools.py
@Time    :   2022/07/14 14:55:09
@Author  :   Wu Shaogui
@Version :   1.0
@Contact :   wshglearn@163.com
@Desc    :   个人常用工具
"""
# --------------------------------------------------------
# 忽略警告
import warnings

warnings.simplefilter("ignore")

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import math
import numpy as np
import imgviz


def show_images(
    images,
    nrows: int = None,
    ncols: int = None,
    figsize: tuple = None,
    imsize: int = 5,
    set_locator: bool = False,
    titles: list = [],
    is_grid: bool = False,
):
    """show_images 按网格显示任意张图片

    Args:
        images:list(uint8), 图片列表
        nrows:int=None, 网格行数(height)
        ncols:int=None, 网格列数(width)
        figsize:tuple=None, 图片宽高
        imsize:int=3, 返回图形中显示的图像大小（英寸）
        set_locator:bool=False, 是否设置刻度
        titles:list=[], 图片的标题
        is_grid:bool=False, 是否给每个像素位置添加文字

    """

    n = len(images)
    if nrows:
        ncols = ncols or int(np.ceil(n / nrows))  # 如果ncols==None，取int(np.ceil(n/nrows))
    elif ncols:
        nrows = nrows or int(np.ceil(n / ncols))
    else:
        nrows = int(math.sqrt(n))
        ncols = int(np.ceil(n / nrows))

    if figsize is None:
        h = (
            nrows * imsize if imsize > 2 else nrows * imsize + 0.6
        )  # https://github.com/matplotlib/matplotlib/issues/5355
        figsize = (ncols * imsize, h)

    fig = plt.figure(figsize=figsize)

    xmajorLocator = MultipleLocator(2)  # 将x主刻度标签设置为50的倍数
    xminorLocator = MultipleLocator(1)  # 将x轴次刻度标签设置为5的倍数

    ymajorLocator = MultipleLocator(2)
    yminorLocator = MultipleLocator(1)  # 将x轴次刻度标签设置为5的倍数

    for find, image in enumerate(images):
        image = image.astype(np.uint8)

        ax = fig.add_subplot(nrows, ncols, find + 1)
        ax.imshow(image)

        if len(titles) == 0:
            plt.title("{}-({})".format(find, image.shape))  # 图片大小作为标题
        else:
            plt.title("{}-({})".format(titles[find], image.shape))  # 自定义标题

        if set_locator:
            # 主刻度
            ax.xaxis.set_major_locator(xmajorLocator)
            ax.yaxis.set_major_locator(ymajorLocator)

            # 次刻度
            ax.xaxis.set_minor_locator(xminorLocator)
            ax.yaxis.set_minor_locator(yminorLocator)

            ax.xaxis.grid(True, which="major", linestyle="-.")  # x坐标轴的网格使用主刻度
            ax.yaxis.grid(True, which="major", linestyle="-.")  # x坐标轴的网格使用主刻度
        else:
            ax.set_axis_off()

        if is_grid:
            # 每个像素格子位置加文字
            for row_ind in range(len(image)):
                for clo_ind in range(len(image[row_ind])):
                    plt.text(row_ind, clo_ind, image[clo_ind][row_ind])
    plt.show()


def RGB_to_Hex(rgb):
    """RGB_to_Hex RGB颜色由10进制转为16进制

    Args:
        rgb (list/tlupe): RGB颜色值

    Returns:
        string: RGB的16进制表示 如:#FF00FF
    """
    color = "#"
    for i in rgb:
        num = int(i)
        color += str(hex(num))[-2:].replace("x", "0").upper()
    return color


LABEL_COLORMAP = imgviz.label_colormap(value=200)


def show_count(lists_count: list = [], color: list = [], figsize: tuple = (10, 8)):
    """show_count 统计2D list中的均值和方差，并绘制每个list

    Args:
        lists_count (list, optional): 2D list. Defaults to [].
        color (list, optional): 每个list的绘制颜色. Defaults to [].
        figsize (tuple, optional): 画布大小. Defaults to (10,8).
    """

    maxcount = max([len(list_count) for list_count in lists_count])

    # _=plt.figure(figsize=figsize)
    _, ax = plt.subplots()  # 创建图实例
    for idx, list_count in enumerate(lists_count):
        mean = np.mean(list_count)
        std = np.std(list_count)
        print("idx:{} mean:{:.2f} std:{:.2f}".format(idx, mean, std))
        if len(color) == 0:
            ax.plot(
                list_count,
                color=RGB_to_Hex(LABEL_COLORMAP[idx % len(LABEL_COLORMAP) + 1]),
                label="idx:{} mean:{:.2f} std:{:.2f}".format(idx, mean, std),
            )
        else:
            ax.plot(
                list_count,
                color=RGB_to_Hex(color),
                label="idx:{} mean:{:.2f} std:{:.2f}".format(idx, mean, std),
            )
    plt.xlim([0, maxcount])
    plt.show()