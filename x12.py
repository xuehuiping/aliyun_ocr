# -*- encoding: utf-8 -*-
"""
@date: 2021/1/13 11:18 上午
@author: xuehuiping
"""
'''
我们在阿里云上买了一个ocr的产品，用于研究阿里云的ocr功能
这是代码和code，你试试能否连上
我的python程序有些问题，还需要安装一些东西
'''

import sys, os
import base64
import time
import json

# from urlparse import urlparse
import urlparse
from com.aliyun.api.gateway.sdk import client
from com.aliyun.api.gateway.sdk.http import request
from com.aliyun.api.gateway.sdk.common import constant
import traceback
import urllib2
import base64


def get_img_base64(img_file):
    with open(img_file, 'rb') as infile:
        s = infile.read()
        return base64.b64encode(s)


def predict(url, appcode, img_base64, kv_config, old_format):
    if not old_format:
        param = {}
        param['image'] = img_base64
        if kv_config is not None:
            param['configure'] = json.dumps(kv_config)
        body = json.dumps(param)
    else:
        param = {}
        pic = {}
        pic['dataType'] = 50
        pic['dataValue'] = img_base64
        param['image'] = pic

        if kv_config is not None:
            conf = {}
            conf['dataType'] = 50
            conf['dataValue'] = json.dumps(kv_config)
            param['configure'] = conf

        inputs = {"inputs": [param]}
        body = json.dumps(inputs)

    headers = {'Authorization': 'APPCODE %s' % appcode}
    request = urllib2.Request(url=url, headers=headers, data=body)
    try:
        response = urllib2.urlopen(request, timeout=10)
        return response.code, response.headers, response.read()
    except urllib2.HTTPError as e:
        return e.code, e.headers, e.read()


def demo(appcode, img_file, result_path):
    url = 'https://form.market.alicloudapi.com/api/predict/ocr_table_parse'

    # 如果输入带有inputs, 设置为True，否则设为False
    is_old_format = False
    config = {'format': 'html', 'finance': False, 'dir_assure': False}
    # 如果没有configure字段，config设为None
    # config = None

    img_base64data = get_img_base64(img_file)
    stat, header, content = predict(url, appcode, img_base64data, config, is_old_format)
    if stat != 200:
        print('Http status code: {}'.format(stat))
        if 'x-ca-error-message' in header:
            print('Error msg in header: {}'.format(header['x-ca-error-message']))
        else:
            print('')
        print('Error msg in body: {}'.format(content))
        exit()
    if is_old_format:
        result_str = json.loads(content)['outputs'][0]['outputValue']['dataValue']
    else:
        result_str = content

    print(result_str)
    with open(os.path.join(result_path, img_file) + '.json', 'w') as f:
        f.write(result_str)

    result = json.loads(result_str)
    tables = result['tables']
    with open(os.path.join(result_path, img_file) + '.html', 'w') as f:
        f.write(tables)


if __name__ == '__main__':
    appcode = 'XXX'
    img_file = 'WechatIMG38.png'
    demo(appcode, img_file, result_path='result')
