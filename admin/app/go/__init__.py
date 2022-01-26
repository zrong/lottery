# -*- coding: utf-8 -*-
"""
app.go
~~~~~~~~~~~~~~~~~~~

go = 开始执行
"""

from pathlib import Path
from datetime import datetime
import random
import math
from openpyxl import Workbook
from flask import (Blueprint)

from pyape import gconfig

go = Blueprint('go', __name__)


def shift(t: int, limit: int) -> list[int]:
    """ 抽出对应数量的随机数
    :param t: 抽几个数字
    :param limit: 最大数字
    """
    lucky_list = []
    for i in range(t):
        lucky_list.append(math.floor(random.random() * limit))
    return lucky_list


def shuffle(arr):
    """ 打乱顺序
    """
    i = len(arr)
    while i:
        j = math.floor(random.random() * i)
        i -= 1
        temp = arr[j]
        arr[j] = arr[i]
        arr[i] = temp


def write_xlsx(first_row: list[str], rows) -> str:
    """ 写入一个 xlsx 并返回文件名
    :param first_row: 标题行
    :param rows: 内容
    """
    static_folder = gconfig.getcfg('PATH', 'STATIC_FOLDER')
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    file: Path = gconfig.getdir(static_folder, f'lottery-result-{now}.xlsx')
    wb = Workbook()
    ws = wb.active
    ws.title = '抽奖结果'
    ws.append(first_row)
    for row in rows:
        ws.append(row)
    wb.save(file)
    return file.name
    

from . import view
