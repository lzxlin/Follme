# -*- coding: utf-8 -*-

import sys,os
import time
from StringIO import StringIO
from PIL import Image
from settings import *

#上传头像
def upload_face(data):

    _state = {
        'success' : False,
        'message' : '',
    }
    
    if data.size > 0:
        # try:
        base_im = Image.open(data)                 #用图片生成Image对象

        size16 = (16,16)                          #4种头像大小
        size24 = (24,24)
        size32 = (32,32)
        size100 = (75,75)

        size_array = (size100,size32,size24,size16)

        # generate file name and the file path
        file_name = time.strftime('%H%M%S') + '.png'             #用时间戳生成头像的文件名
        file_root_path = '%sface/' % (MEDIA_ROOT)
        file_sub_path = '%s' % (str(time.strftime("%Y/%m/%d/")))

        # 将每种大小的文件保存到各自的路径中
        for size in size_array:
            file_middle_path = '%d/' % size[0]

            file_path = os.path.abspath(file_root_path + file_middle_path + file_sub_path)

            im = base_im
            im = make_thumb(im,size[0])             #生成指定大小的头像文件

            # check path exist
            if not os.path.exists(file_path):   # 如果保存不存在则新建
                os.makedirs(file_path)

            im.save('%s/%s' % (file_path,file_name),'PNG')   #保存文件


        _state['success'] = True
        _state['message'] = file_sub_path + file_name
        #except:
        #    _state['success'] = False
        #    _state['message'] = '上传头像时出错。'
    else:
        _state['success'] = False
        _state['message'] = '还未选择要上传的文件。'
        
    return _state

def make_thumb(im, size=75):
    u"""
    summary:
        缩略图生成程序
    params:
        sizes   参数传递要生成的尺寸，可以生成多种尺寸
    """
            
    width, height = im.size
    if width == height:
        region = im
    else:
        if width > height:
            delta = (width - height)/2
            box = (delta, 0, delta+height, height)
        else:
            delta = (height - width)/2
            box = (0, delta, width, delta+width)            
        region = im.crop(box)

    thumb = region.resize((size,size), Image.ANTIALIAS)
    return thumb