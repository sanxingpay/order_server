

from requests import request
import json
from urllib.parse import urlencode
from collections import OrderedDict
import hashlib
from libs.utils.mytime import UtilTime
import time,random
import demjson
import os
# from apps.utils import url_join

from pyDes import *

import base64
# from Cryptodome.PublicKey import RSA
# from Cryptodome.Hash import SHA1
# from Cryptodome.Signature import pkcs1_15
from Crypto.Cipher import AES,DES,DES3
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1,SHA256

from binascii import b2a_hex, a2b_hex

class LastPassBase(object):

    def __init__(self,**kwargs):
        self.secret = kwargs.get('secret')
        self.data = kwargs.get('data',{})

    def _sign(self):
        pass

class LastPass_BAOYANGHUI(LastPassBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.appId = "rogerxpp"
        self.appSecret = 'rogerxpp'
        self.token = None
        self.goods = None

        self.server = "http://www.baoyanghui.com/Car_2_0"

    def run_api(self,func):
        try:
            res = func()
            return (False, res['msg']) if str(res['code'])!='0' else (True,res['resultData']['accessToken'])
        except Exception as e:
            return (False,str(e))

    def get_token(self):

        try:
            api_server = "/api/open/token"
            result = request(method='GET', url=self.server+api_server,params={
                "appId" : self.appId,
                "appSecret" : self.appSecret
            })
            res = json.loads(result.content.decode('utf-8'))
            return (False, res['msg']) if str(res['code']) != '0' else (True, res['resultData']['accessToken'])
        except Exception as e:
            return (False, str(e))


    def get_goodsList(self):

        try:
            api_server = "/api/open/merchantPlace/list"
            result = request(method='GET', url=self.server+api_server,params={
                "accessToken": self.token
            })
            res = json.loads(result.content.decode('utf-8'))
            print(res)
            return (False, res['msg']) if str(res['code']) != '0' else (True, res['resultData'])
        except Exception as e:
            return (False, str(e))

    def run(self):


        res = self.get_token()
        if not res[0]:
            return res
        else:
            self.token = res[1]

        res = self.get_goodsList()
        if not res[0]:
            return res
        else:
            self.goods = res[1]

        print(self.goods)

import urllib
class LastPass_BAWANGKUAIJIE(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #订单生成地址
        self.create_order_url="http://orderpay.xincheng-sh.com:8088/webwt/unionH5Pay/orderreturnPay.do"


        #代付地址
        self.daifu_url = "http://orderpay.xincheng-sh.com:8088/webwt/pay/gateway.do"


        self.bal_query_url="http://orderpay.xincheng-sh.com:8088/agentPayment/payBalanceQuery"

        self.secret = "fcdd45eba6164b9cb2affed11b205d50"

        #私钥
        self.si_secret = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCN1aC9bqGq8jv/zLmuU06UMxE1oSaI3OcgKFDNgpNpGtMgmA/xz0Loshd/EMx9LKCtmxnRJPwHfa4weV8ttYzxyvZn2ZMPm92mZY/SPQrbcZ9xqlPDqT4G1fzXQg+45JCBS0+e6aSdW2ohcLw9EAzHf5LMI8d78t4rW7rvZTplQ8Jz37Tuixt0K58/k426cnjtrHWmYBBWbagWrFPbkvFL73+Pqb7ssRocMiWvZIRneEH9kHpRPwmou7nyN9LvhJ5jnRH9lk+4o3YFVOh8thU3RvKWw5K4EdHZUguMj8I6i2n1IbKlQcVMuyqjh44y9tj0ZwJUK4bqdoUO8JVEpW+NAgMBAAECggEAB6wLktOeKRoLRs3zKUvWT0vn3WfHJtYUJngnzsYGZUQPMY8oJaNZci7X+IaXGRpF4r4mClseyuTwfCzEijts0VNyOrHZM5nxxmNuAShOIwqlXkehWk8YTNRcZeRr50ttyaCiQO1QezaLqh1oAUGR/2SWMzaoPrsna1794J8wJnQMPbeI3XkM7tZx7nHetHiAuWqt38qaSRhpd+TYewkz5e1XpGLSoypqM/jDrCdnQ2uYgQhR3/60RT+2hf2t8ffZth4QbkNoxnA1n2cKFzAF9SOhXAP72g9cWpk5mweoh02jrKct0+qN7/RTRtkbvvvqlYgiSXoSHA+ftiYfKV/NAQKBgQDBZ4bgg52QgN6E/k7r8n4KbLjdd6xdgPSranyjOY9Q0DMg7OEjX5/uy9u2GYuImfeU3mcBSyfAffwVcxmk9xpxfMTug4ls8ZuXmutqhci11dLjnMiSe41Yp8UdzKtvc+KZxOEhO2hRWgHTJdfqKMkAZfVX4BKVpoRQg1jy5q3lwQKBgQC7vUnW31f1HRYFCCkt/y8OP2yIVV/aI+tVeWWbaQ9Uk58U7LKUnooHii8IUx2zmeEo/woQ8Kx2KPHGmmZ4hWRZY1uscZzg6TBy6p300CPPzobe1ca6L25rCt++bkVEVf4sGKYRFOXP6Zsjs2LDA1fVazlHjENvMqJHxU28i4l0zQKBgQClxIJKdQTcElinTQGAInv9m2poCGboTdtoAQGLNY6tCYaJNf9SPmfqWTicQBDkqHMYWfeXmD8eMd2a1OiqCFHV68cvV/a2Ne/SZapZxwldMURsarlPNC7WShYdkItwH7edbK45uZ2T/L2LqOgDf6moebtr8lZ7hhnqmGno5+ctAQKBgHatyUDI/VxY37OcnhOSrlduZpikh6xpanok/MNKncNUcosSui1TL2RmySaVDECd9QUqfF2LFyq25Wgr8L0dbftH4QrY41gWcWcjw2igLxNNtlqlfzPxifam8Bv8r1LsnXmYt1ozALf3L/hYjQVEVsD2QEZnd7WSp52BL4wSFXm9AoGAPxmXGft3umFh3Gg1j0iMXqOm1VxPnlelx5KY+HbUISkld71NbiLGqnL3k/h5j2CiVnw7AOWOM1wupYlIIr3jbxToem2eEEJNtzxIBCDklNvnaoGHdg5u7ra5IWJy4yJEYwINZdyUFbY3cOZGDSZqEHp4ziDUkRxWX5vvBEnn8/s="
        # self.si_secret = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC5RpKJOSIBdozaSQZJXQRA5PbbGXxOlB4J5z7JvRm2qUC/4QzKch13pTnc+ln13wDYN0fVgAjQHF+NX5M6Eyc3sGxS0inWtGY40eZW+SaJpdjRCfUDnG2mygqZgiP/4CR2GbL9MJCTLRNv+x26SlCWi5Ss1xfseJVSU6244yECgp/KWgBKRcZiFEacBX0W4jrhSEricjagxg91pL86M/lHdO3WVtHV45ix6/nOg41dMLQ2+Ml3he581mEd6GiCXPO4KAfu641YiEoquG8+GDmvOuasyE2fUjqU6N0XZPHVPlMmb+364vgglWc6/hYirm/LwzNbWj5gbTSeROQe+cFTAgMBAAECggEAD8zh8EvsB33psy/pFlaVZ0dfef3paPYeva933lJ/H+G9QN/bbGRg+PQhRCQhieNTuhy0xpNdrQnOaEsPTjOV85zbEBEWOlY2JYBZCW/EBpcbL3CO8ZjkjQXL851ynn6p/VxhtE/w9GwyrSkYNuvhhYUvz7GkO6lo6pVySkMsbH87w8HwVqQkxrJd5mwEg1Kv0AVZ9F7YJcQ4wDdr/XtPhETay9vOgUegj/AfsrpvSTa1VBTEXCLPDpGybxliLlFHR7Gl0xkbRxggvHxmIscr9gXxhQRVU8euGFJ9Um0LFfvJ4Edcpt1OgfZ3xybs1YrhrTC2ySICMsARzD1r7EQ/0QKBgQD7Z8blcM3DSVeeI8Tz3RASPG11ZrhLei6XT/ngmPCfSYFZnP2MAOgdwi8m3x51ogK50w7Kl0665Dylpb13WNA06sJ2ab26vpetX9E6JcWNp6AlukuRFSXsDabvmYlIX1/E0ato4GZUZjajcwndURScBfNxUIIo4mqrqU2oDlmqaQKBgQC8qWbOybCnIQVeL1XiQPUOLrfXMNhyPs4iyzI2NkvfBt3F700p7ubIr6v8EvqNJMI4vVHQTB9rmO6y9YrX5F1DxfrSHaoeQsF81sKgiy+ZDszWtL/2HEnPd5yLeXGxeZXTQ3FXs3mZdJyFUkvkVZNzTj6a+nSgs9FQ7JLTARb+WwKBgQCzso3cWjD5MWdLRc31cUGXh1HF5NI+QOskhKna+/aiJGwsnaYteEhxXOdPJZQkCNVh9ZZRAK3psFIZJMq0j+riqBqvgQ14edr4tdBbe7wlcHdsACkbXr5oZ6m3AUu7S1Cs4iFfKWZ7VUQguI2If/f3PdmwWRdwGcadRLqZMQiuYQKBgAO5nIwMs245Wq/HY3y6J5yGE58uGbf3wX4yYOVtIQZgTlSwKuffDbN8tHqfrU7IIQWZx1nDhwNK27uw2XL10VmbOR6Y81jxnHxoiSM+XEw7XJQIsZmcaWCtTev7E+GbMvge5sgChS4gfU6sl08E2Yp3SwkoVNEve7yLT0LXTKrtAoGABHxlIahSKDOqLedbTBthscr1bkbnRm7L5g7a2Z1hUeuUNPIcamRyqmE5yqAQCKFjIcxL5VKTDgthg/5V8CqJCBvJ318kbLPdRjcPAhxdxQiecn6z6X1yWLIJVi+eakZW/gW4vvITWR9uLRQlflXaQOgwOuulL9z05hBjzn/uPHE="
        #self.secret = "MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBALwNXPM8FUpJR2taYG8ctrQFxckYfPdWPFfCqb7a2SIJ8O/tqk16SqfyvJeQUy9dzkd5AWfE933Bn7sgNBsfNc6b0PXQ0cyyhYvNRhegN3ZDZO/i+pKjblCpFZCkYGAEGwy05ubV8sEViQqT1st1geaZ48ugzyfWM9+6hp1oMfipAgMBAAECgYEAoDC19FFDRZOkrhM/wIbyL+oW8NXWZg9kudGOLZFZk8BqKMgI4ZUCEY0aD/YWlmvPM10l0FKeDNcqjQnCuTPd7ZqVKGzKYPljn3tEafv7/LLyRSsUFyS3CKDMVb+pVGtmAePInx7SxosaxY8Xa//e21Y0Job0ecyVGvgku3nyEwECQQDpPYmp0KeiUMSkY/HxP90cEcA2OANMRuhyFq6056KtUQEml5Q/j2fNduZ0z3PB84RfKc9p2Gr0Q4Y+KYFBOC2JAkEAzmcAdI/A1kc3nNzb3giq06kxcE6SJKSOOcByel1GrvRa5+7WaX7erCU7g1DTieM2MGbvzjvAjQAVtHlzYFbKIQJBAKxCKLPkSIpWgISw0/VLJ3AdpAnnIHhrPi1Ulz9AfCLo2qK3/GNc9FsI33eR53ps8WyfInKXxZYVcMXkPXP/m5ECQDHtbonDoET1EznJnxHVjOUIX2IoT2e3uoOzzr1UxN1bVIYYGxuHyftgQkYgjhsjsB8DN2zuvUQeSiHO4x7hv6ECQQCRxh9YVwzyPXkl5NJGDAQWuLf5EtSrB9gW7nLIJL8Geoww/yNi0YmmP4xFX7qJI6/eENGFI/6EKcLV9v/2VdZp"
        self.si_secret = "-----BEGIN RSA PRIVATE KEY-----\n" + self.si_secret + "\n-----END RSA PRIVATE KEY-----"
        #公钥
        self.public_secret = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7wGnoHC8BrqoppkvjshSi2gtJhp3ogy7nLsnNhqiCi3P3ZVmHYehcqbPmJuyIWQ+ILAIDfCcObSYqYZW6ozEJ3UrrghyszaWpD4YM8j3+5i+HMNqHt9tDzKigsaCPw1KKZKrNvXkMZ0ydmsEZ1zdJvE7whA3cAsjA62CNl3Aii25d1SjJisOVg20XcKHPLZKSUVScFdJ/tG19bpe8V3poq85087sVz3rniisjdKTbXTbxM2Nkpkt1IjmRfXrHpW/805L/uPpCVqo125on4yY2nIFY42e0GmS/LG6YM55QZ+9CvC1P8PEoNv0cArbdqpmBBfGGxyT2LfkZM7DvrTQIwIDAQAB"
        # self.public_secret = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjdWgvW6hqvI7/8y5rlNOlDMRNaEmiNznIChQzYKTaRrTIJgP8c9C6LIXfxDMfSygrZsZ0ST8B32uMHlfLbWM8cr2Z9mTD5vdpmWP0j0K23GfcapTw6k+BtX810IPuOSQgUtPnumknVtqIXC8PRAMx3+SzCPHe/LeK1u672U6ZUPCc9+07osbdCufP5ONunJ47ax1pmAQVm2oFqxT25LxS+9/j6m+7LEaHDIlr2SEZ3hB/ZB6UT8JqLu58jfS74SeY50R/ZZPuKN2BVTofLYVN0bylsOSuBHR2VILjI/COotp9SGypUHFTLsqo4eOMvbY9GcCVCuG6naFDvCVRKVvjQIDAQAB"
        self.public_secret = "-----BEGIN PUBLIC KEY-----\n" + self.public_secret + "\n-----END PUBLIC KEY-----"

        self.data.setdefault('agtId', "19101009")
        self.data.setdefault('merId', "1910100909")

    def rsa_sign(self,message):

        encrypted = message.encode("utf-8")
        private_key = RSA.importKey(self.si_secret)

        h = SHA256.new(encrypted)

        signature = PKCS1_v1_5.new(private_key).sign(h)
        return base64.b64encode(signature)

    def rsa_design(self,signature,msg):

        msg = msg.encode("utf-8")
        public_key = RSA.importKey(self.public_secret)

        hash_obj = SHA256.new(msg)

        try:
            PKCS1_v1_5.new(public_key).verify(hash_obj, base64.b64decode(signature))
            return True
        except (ValueError, TypeError):
            return False

    def _sign(self,data=None):

        valid_data = {}
        # 去掉value为空的值
        for item in data:
            valid_data[item] = data[item]

        # 排序固定位置
        valid_data_keys = sorted(valid_data)
        valid_orders_data = OrderedDict()
        for key in valid_data_keys:
            valid_orders_data[key] = valid_data[key]

        valid_orders_data['key'] = self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = (encrypted[:-1]).encode("utf-8")

        return hashlib.md5(encrypted).hexdigest().upper()

    def rsa2_sign(self,sign):
        return self.rsa_sign(sign)

    def check_sign(self,sign,md5sign):
        if not self.rsa_design(sign,md5sign):
            return False


    def _request(self):
        print(self.data)
        result = request(method='POST', url=self.create_order_url, data=self.data,verify=True)
        return result.content.decode('utf-8')

    def _request_daifu(self,url,data):

        result = request(method='POST', url=url, json=data,verify=True,headers={
            "Content-Type":'application/json'
        })
        return json.loads(result.content.decode('utf-8'))

    def df_bal_query(self):
        self.data.setdefault("tranCode","2103")
        self.data.setdefault("nonceStr",str(UtilTime().timestamp))
        sign = self._sign(self.data)

        data = {
            "REQ_HEAD" : {
                "sign" : self.rsa2_sign(sign).decode('utf-8')
            },
            "REQ_BODY" : self.data.copy()
        }

        res = self._request_daifu(self.daifu_url,data)

        sign = res['REP_HEAD']['sign']

        if not self.check_sign(sign,self._sign(res['REP_BODY'])):
            PubErrorCustom("验签失败!")


    def run(self):
        # self.data.setdefault('agtId',self.agtId)
        # self.data.setdefault('merId',self.businessId)
        # self.data.setdefault("memberId","1")

        self.data.setdefault("orderTime",str(UtilTime().arrow_to_string(format_v="YYYYMMDD")))

        self.data.setdefault("pageReturnUrl","http://www.baidu.com")

        self.data.setdefault('goodsName',"goodsName")
        self.data.setdefault('bankCardNo', '1')
        self.data.setdefault('sign',self.rsa2_sign(self._sign(self.data)))

        return self._request()

    def call_run(self):

        print(self.data)
        sign = self.data.pop('sign')
        if not self.check_sign(sign,self._sign(self.data)):
            raise PubErrorCustom("验签失败!")

        if self.data.get('orderState') and str(self.data.get('orderState')) == '01':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("orderId"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)
        else:
            raise  PubErrorCustom("支付状态有误!")


    def df_return_content(self):


        cardno = "6226000000000000"
        name = "小明"
        bankname = "中国工商银行"
        type = "私"
        amount = 0.08
        bizhong = 'CNY'
        ordercode = "10000001"
        remark = "备注"

        content = "{},{},{},{},{},{},{},{},{}".format(
            cardno,
            name,
            bankname,
            type,
            amount,
            bizhong,
            '',
            ordercode,
            remark
        )
        print(content)
        return content


    def df_api(self):
        self.data.setdefault('customerNo', self.businessId)
        self.data.setdefault('inputCharset', "utf8")
        self.data.setdefault('payDate', UtilTime().arrow_to_string(format_v="YYYYMMDD"))
        self.data.setdefault('inputCharset', "00")

        self.data.setdefault('content',self.df_return_content())

        self._sign()

        self.data.setdefault('signType', "MD5")


class LastPass_KUAIJIE(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #订单生成地址
        self.create_order_url="http://epay.hyhope.top/portal"

        #代付提交地址
        self.df_url = "http://api.hyhope.top/agentPayment/paySingle"

        #代付余额查询
        self.df_bal_query_url = "http://api.hyhope.top/agentPayment/payBalanceQuery"

        #代付订单查询
        self.df_order_query_url = "http://api.hyhope.top/agentPayment/paySingleQuery"

        self.secret = "a1a05672g9b7825872235f2ba350b75d8f430c31655g67a4156g3718186g2580"
        self.businessId = "100000000064907"

        self.response = None

    def _sign(self):

        valid_data = {}
        # 去掉value为空的值
        for item in self.data:
            valid_data[item] = self.data[item]

        # 排序固定位置
        valid_data_keys = sorted(valid_data)
        valid_orders_data = OrderedDict()
        for key in valid_data_keys:
            valid_orders_data[key] = valid_data[key]

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = (encrypted[:-1]+self.secret).encode("utf-8")
        print(encrypted)
        self.data['sign'] = hashlib.md5(encrypted).hexdigest()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        signtype = self.data.pop('sign_type',False)
        self._sign()
        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        print(json.dumps(self.data))
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        # print(result.content)
        # self.response=json.loads(result.content.decode('utf-8'))
        # print(self.response)
        self.response = result.content

    def _request_df(self):
        print(json.dumps(self.data))
        # print(self.data)
        result = request(method='POST', url=self.df_url, data=self.data, verify=True)
        # print(result.content)
        # self.response=json.loads(result.content.decode('utf-8'))
        # print(self.response)
        res = json.loads(result.content.decode('utf-8'))
        if res['status'] != 'succ':
            raise PubErrorCustom(res['errMsg'])


    def run(self):
        self.data.setdefault('service',"online_pay")
        self.data.setdefault('customer_no' , self.businessId)
        # self.data.setdefault('return_url',url_join("/pay/#/juli"))
        self.data.setdefault('return_url',url_join("/pay/juli"))

        self.data.setdefault('charset',"utf-8")
        self.data.setdefault('title',"title")
        self.data.setdefault('body', "body")

        self.data.setdefault('payment_type', "1")
        self.data.setdefault('paymethod', "bankPay")
        self.data.setdefault('defaultbank', "QUICKPAY")
        self.data.setdefault('access_mode', "1")
        self.data.setdefault('seller_email', "1018125792@qq.com")

        self._sign()

        self.data.setdefault('sign_type',"MD5")

        self.data.setdefault('create_order_url',self.create_order_url)

        return self.data

    def call_run(self):
        self.check_sign()

        if  self.data.get('trade_status')=='TRADE_FINISHED':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("order_no"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)


    def encrypt(self,content, key):

        k = des(key=key,
                pad=None,
                padmode=PAD_PKCS5)
        # return base64.b64encode(k.encrypt(content))

        return k.encrypt(content).hex()

    def decrypt(self,content,key):

        content = base64.b64decode(content)

        k = des(key=key,
                pad=None,
                padmode=PAD_PKCS5)

        return k.decrypt(content).decode('utf-8')


    def df_return_content(self):


        cardno = "6226621704181682"
        name = "陈丽红"
        bankname = "中国光大银行"
        type = "私"
        amount = 50.0
        bizhong = 'CNY'
        ordercode = "DF00000001"
        remark = "备注"

        content = "{},{},{},{},{},{},{},{},{}".format(
            cardno,
            name,
            bankname,
            type,
            amount,
            bizhong,
            '',
            ordercode,
            remark
        )
        return self.encrypt(content.encode('utf-8'),self.secret[:8])

    def df_bal_query(self):

        encrypted = ("customerNo={}{}".format(self.businessId,self.secret)).encode("utf-8")
        print(encrypted)

        self.data.setdefault("sign",hashlib.md5(encrypted).hexdigest())
        self.data.setdefault("customerNo",self.businessId)

        print(json.dumps(self.data))
        result = request(method='POST', url=self.df_bal_query_url, data=self.data, verify=True)
        res = json.loads(result.content.decode('utf-8'))
        # print(res)
        if res['status'] != 'succ':
            raise PubErrorCustom(res['errMsg'])

        return res['errMsg']

    def df_order_query(self):

        self.data.setdefault("customerNo",self.businessId)
        self.data.setdefault("inputCharset","UTF-8")
        self.data.setdefault("payVersion",'00')
        self.data.setdefault("tradeCustorder","DF00000002")
        self.data.setdefault("payDate",UtilTime().arrow_to_string(format_v="YYYYMMDD"))
        self._sign()
        self.data.setdefault('signType',"MD5")

        from urllib.parse import unquote
        print(json.dumps(self.data))
        result = request(method='POST', url=self.df_order_query_url, data=self.data, verify=False)
        res = json.loads(result.content.decode('utf-8'))
        print(res)
        print(unquote(res['tradeReason'], 'utf-8'))


        self.data = res
        sign = self.data.pop('sign')
        signType = self.data.pop('signType')

        self._sign()
        if sign != self.data.get('sign'):
            print("签名错误!")

        if str(res['status']) != 'succ':
            print("111")
            print(res['errMsg'])


        # if res['status'] != 'succ':
        #     raise PubErrorCustom(res['errMsg'])
        #
        # return res['errMsg']

    def df_api(self):
        self.data.setdefault('customerNo', self.businessId)
        self.data.setdefault('inputCharset', "utf8")
        self.data.setdefault('payDate', UtilTime().arrow_to_string(format_v="YYYYMMDD"))
        self.data.setdefault('inputCharset', "00")

        self.data.setdefault('content',self.df_return_content())
        self.data.setdefault('payVersion',"00")

        self._sign()

        self.data.setdefault('signType', "MD5")

        self._request_df()

        return self.response



if __name__=='__main__':

    # data={
    #     "orderAmt" : "50000",
    #     "orderId": "12312312111aaa1aaa",
    #     "notifyUrl":"http://www.baidu.com",
    # #     "memberId" : "1"
    # # }
    #
    res = LastPass_KUAIJIE(data={}).df_order_query()
    # print(res)
    # # print(res['retMsg'])