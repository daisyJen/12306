# -*- coding:utf-8 -*-
import numpy
import requests

# 由于12306官方验证码是验证正确验证码的坐标范围,我们取每个验证码中点的坐标(大约值)
yanSol = ['35,35', '105,35', '175,35', '245,35', '35,105', '105,105', '175,105', '245,105']
allPicture ={
        1: '35,35',
        2: '105,35',
        3: '175,35',
        4: '245,35',
        5: '35,105',
        6: '105,105',
        7: '175,105',
        8: '245,105'
}

def checkPicture(pic_name):
    body_list = []
    url = '''http://littlebigluo.qicp.net:47720/'''
    files = {'file': (pic_name, open(pic_name, 'rb'))}
    res = requests.post(url, files=files)  # post pic

    if res.status_code == 200:  # return ok
        try:
            # print(res.text)
            if u"文字应该" in res.text:  # 识别验证码成功
                body_str_1 = res.text.split(u'''<B>''')
                body_str = body_str_1[2].split(u'<')[0].split()
                for index in body_str:
                    body_list.append(int(index))
                #return 0, numpy.array(body_list)
            code = ''
            if(len(body_list) > 0):
                for body in body_list:
                    if allPicture.has_key(body):
                        code += ',' + allPicture[body]
            if(code != ''):
                code = code.strip(',')
            return code
        except:
            print("验证码解析失败")
            return ''

    return ''  # 验证码解析失败