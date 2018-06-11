import hashlib
import requests
import urllib
import base64
import string
import random
import json
import time
from app import utils

url_preffix='https://api.ai.qq.com/fcgi-bin/'

filter_api = 'ptu/ptu_imgfilter'
translate_api = 'nlp/nlp_texttrans'

def setParams(array, key, value):
    array[key] = value

def genRandomStr(n=32):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def genSignString(parser):
    uri_str = ''
    for key in sorted(parser.keys()):
        if key == 'app_key':
            continue
        if key == 'image':
            uri_str += "{}={}&".format(key, urllib.parse.quote(str(parser[key].decode()), safe = ''))
        else:
            uri_str += "{}={}&".format(key, urllib.parse.quote(str(parser[key]), safe = ''))
    sign_str = uri_str + 'app_key=' + parser['app_key']
    hash_md5 = hashlib.md5(sign_str.encode()).hexdigest()
    return hash_md5.upper()

class TCAI(object):
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
        self.data = {}

    def invoke(self, params):
        print('start invoke filter api at : {} with class id :{}'.format(utils.getTextTime(),self.data.get('filter','null')))
        self.url_data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(self.url, self.url_data)
        try:
            rsp = urllib.request.urlopen(req)
            str_rsp = rsp.read()
            dict_rsp = json.loads(str_rsp)
            print('invoke filter api end at : {}'.format(utils.getTextTime()))
            return dict_rsp
        except urllib.error.URLError as e:
            dict_error = {}
            if hasattr(e, "code"):
                dict_error = {}
                dict_error['ret'] = -1
                dict_error['httpcode'] = e.code
                dict_error['msg'] = "sdk http post err"
                return dict_error
            if hasattr(e,"reason"):
                dict_error['msg'] = e.reason
                dict_error['httpcode'] = -1
                dict_error['ret'] = -1
                return dict_error
        else:
            dict_error = {}
            dict_error['ret'] = -1
            dict_error['httpcode'] = -1
            dict_error['msg'] = "system error"
            return dict_error

    def getImageFilter(self,image,ft):
        self.url = url_preffix + filter_api
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', genRandomStr())
        setParams(self.data, 'filter', int(ft))
        image_data = base64.b64encode(image)
        setParams(self.data, 'image', image_data)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    def getNlpTextTrans(self, text, type):
        self.url = url_preffix + translate_api
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', genRandomStr())
        setParams(self.data, 'text', text)
        setParams(self.data, 'type', type)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)
