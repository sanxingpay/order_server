

from requests import request
import json
from urllib.parse import urlencode
from collections import OrderedDict
import hashlib
from libs.utils.mytime import UtilTime
import time,random
import demjson
import os

import base64
# from Cryptodome.PublicKey import RSA
# from Cryptodome.Hash import SHA1
# from Cryptodome.Signature import pkcs1_15
from Crypto.Cipher import AES,DES,DES3
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
import urllib

from binascii import b2a_hex, a2b_hex

from libs.utils.string_extension import hexStringTobytes

# from apps.lastpass.models import JdBusiList

class LastPassBase(object):

    def __init__(self,**kwargs):
        self.secret = kwargs.get('secret')
        self.data = kwargs.get('data',{})

    def _sign(self):
        pass

class TestDf(object):

    def __init__(self):
        self.secret = "4S4G7CBWJHYAD5ZE"

        self.data={
            "businessid" : "5"
        }

    def _request(self,url):

        print(self.data)
        print(url)
        result = request('POST', url=url,
                         json=self.data, verify=False)

        res = json.loads(result.content.decode('utf-8'))

        print(res)

        if res['rescode'] != '10000':
            print("错误!",res['msg'])
            return None
        else:
            return res


    def BalQuery(self):

        self.data.setdefault("nonceStr",str(UtilTime().timestamp))

        md5params = "{}{}{}{}".format(
            self.secret,
            str(self.data.get("businessid")),
            self.data.get("nonceStr"),
            self.secret)
        md5params = md5params.encode("utf-8")
        self.data.setdefault("sign", hashlib.md5(md5params).hexdigest())
        return self._request("http://allwin6666.com/api_new/business/BalQuery")

    def dfQuery(self):

        self.data.setdefault("nonceStr",str(UtilTime().timestamp))
        self.data.setdefault('down_ordercode','20537015002737810915')

        md5params = "{}{}{}{}{}".format(
            self.secret,
            str(self.data.get("down_ordercode")),
            str(self.data.get("businessid")),
            self.data.get("nonceStr"),
            self.secret)
        md5params = md5params.encode("utf-8")
        self.data.setdefault("sign", hashlib.md5(md5params).hexdigest())
        return self._request("http://allwin6666.com/api_new/business/dfQuery")


    def df(self):

        self.data.setdefault("nonceStr",str(UtilTime().timestamp))
        self.data.setdefault('down_ordercode',str(UtilTime().timestamp))
        self.data.setdefault('amount',1.0)
        # self.data.setdefault('accountNo','6226621704181682')
        self.data.setdefault('memo','test')
        self.data.setdefault('accountNo','111')
        self.data.setdefault('bankName','中国光大银行'.encode('utf-8').hex())
        self.data.setdefault('accountName','陈丽红'.encode('utf-8').hex())

        md5params = "{}{}{}{}{}{}{}{}{}{}".format(
            self.secret,
            str(self.data.get("down_ordercode")),
            str(self.data.get("businessid")),
            self.secret,
            self.data.get("nonceStr"),
            str(self.data.get("amount")),
            str(self.data.get("accountNo")),
            str(self.data.get("bankName")),
            str(self.data.get("accountName")),
            self.secret)
        md5params = md5params.encode("utf-8")
        self.data.setdefault("sign", hashlib.md5(md5params).hexdigest())
        return self._request("http://allwin6666.com/api_new/business/df")


class LastPass_WEIFU(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.secret = "8a40d47c8218481a9cdf540a46a8c1cc"
        self.businessId = "JXM000000000000107"
        self.token= None

        self.response = None

    def get_token(self):
        t = UtilTime().timestamp
        data=dict(
            merchantNo = self.businessId,
            key =self.secret,
            nonce = str(t),
            timestamp = t
        )
        s = "merchantNo={}&nonce={}&timestamp={}&key={}".format(
            data['merchantNo'],
            data['nonce'],
            str(data['timestamp']),
            data['key'],
        )
        print(s)
        data['sign']=md5pass(s).upper()
        print(data)
        result = request(method='POST', url="http://api.jinxiangweb.cn:8888/api/v1/getAccessToken/merchant", data=data, verify=False)
        print(result.text)
        response = json.loads(result.content.decode('utf-8'))
        if response['success']:
            self.token = response['value']['accessToken']


    # def run(self):
    #     self.data.setdefault('mchId',self.businessId)
    #     self.data.setdefault('appId',self.appId)
    #
    #
    #     self.data.setdefault('currency','cny')
    #
    #     # self.data.setdefault('productId', self.productId)
    #     self.data.setdefault('subject','商品P')
    #     self.data.setdefault('body', '商品P6666')
    #
    #     # self.data.setdefault('pay_bankcode',"904")
    #     self._sign()
    #
    #     try:
    #         self._request()
    #         print(self.response)
    #         return (False, self.response['retMsg']) if self.response['retCode']!='SUCCESS' else (True,self.response['payParams']['payUrl'])
    #     except Exception as e:
    #         return (False,str(e))

if __name__ == '__main__':

    testDfClass = TestDf()
    print(testDfClass.dfQuery())