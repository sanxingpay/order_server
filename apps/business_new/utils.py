
import hashlib
import json
import base64

from requests import request

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

from libs.utils.exceptions import PubErrorCustom
from libs.utils.mytime import UtilTime
from libs.utils.string_extension import md5pass
from libs.utils.log import logger
from apps.utils import RedisOrderCreate

from apps.utils import url_join

class CreateOrderForLastPass(object):

    def __init__(self,**kwargs):

        #规则
        self.rules = kwargs.get("rules",None)

        #传入数据
        self.data = kwargs.get("data",None)

        #渠道ID
        self.passid = kwargs.get("passid",None)

        logger.info("规则：{}".format(self.rules))

        #请求数据
        self.request_data = {}

        #确定请求的字典key集合
        self.request_keys = []

        #参加签名数据
        self.request_data_sign = {}

        #参加加密的数据
        self.request_data_pass = {}

        #返回数据
        self.response = None

    #数据整理
    def dataHandler(self):

        for item in self.rules.get("requestData"):
            if 'value' in item:
                item['value'] = self.data.get(item['value']) if item.get("type") == "appoint" else item['value']
            res = getattr(CustDateType, "get_{}".format(item['dataType']))(item)
            self.request_data[item['key']] = res
            if item.get("sign",None) :
                self.request_data_sign[item['key']] = res

            if item.get("password",None) :
                self.request_data_pass[item['key']] = res

            if 'requestOk' in item and item['requestOk']:
                self.request_keys.append(item['key'])

        self.request_keys.append(self.rules['password']['signKey'])
        self.request_keys.append(self.rules['sign']['signKey'])

    def reuquestBeforeDataHandler(self):
        tmp={}
        for key in self.request_data:
            if key in self.request_keys:
                tmp[key]=self.request_data[key]
        self.request_data=tmp

        data={}
        if self.passid == 74:
            data['accessToken'] = self.request_data['accessToken']
            data['param'] = self.request_data
            self.request_data = data

    #加密
    def passHandler(self):
        password = PassBase(
            hashData=self.request_data,
            signData=self.request_data_pass,
            signRules=self.rules['password']
        ).run()

        self.request_data_sign[self.rules['password']['signKey']] = password
        self.request_data[self.rules['password']['signKey']] = password

    #签名
    def signHandler(self):

        if self.passid == 79:
            sign = SignBaseCustom(
                hashData=self.request_data,
                signData=self.request_data_sign,
                signRules=self.rules['sign']
            ).md5()
        else:
            sign = SignBase(
                hashData=self.request_data,
                signData=self.request_data_sign,
                signRules=self.rules['sign']
            ).run()

        self.request_data[self.rules['sign']['signKey']] = sign

    #向上游发起请求
    def requestHandlerForJson(self):
        """
        "request":{
            "url":"http://localhost:8000",
            "method" : "POST",
            "type":"json",
        },
        """
        logger.info("向上游请求的值：{}".format(json.dumps(self.request_data)))
        if self.rules.get("request").get("type") == 'json':
            result = request(
                url=self.rules.get("request").get("url"),
                method=self.rules.get("request").get("method"),
                json = self.request_data,
                headers={
                    "Content-Type": 'application/json'
                }
            )
        elif self.rules.get("request").get("type") == 'body':
            result = request(
                url = self.rules.get("request").get("url"),
                method = self.rules.get("request").get("method"),
                data=self.request_data,
            )
        elif self.rules.get("request").get("type") == 'params':
            if self.passid == 76:
                url = self.rules.get("request").get("url") + "?params={}".format(json.dumps(self.request_data))
                # data['params'] = self.request_data
                print(url)
                result = request(
                    url = url,
                    method = self.rules.get("request").get("method"),
                )
            else:
                result = request(
                    url = self.rules.get("request").get("url"),
                    method = self.rules.get("request").get("method"),
                    params = self.request_data
                )
        else:
            raise PubErrorCustom("请求参数错误!")

        try :
            self.response = json.loads(result.content.decode('utf-8'))
            logger.info("上游返回值：{}".format(result.content.decode('utf-8')))
        except Exception as e:
            raise PubErrorCustom("返回JSON错误!{}".format(result.text))

    #返回数据json映射
    def rDataMapForJson(self):
        # 返回数据映射
        str = ""
        for (index, item) in enumerate(self.rules.get("return").get("url").split(".")):
            str = str + "['{}".format(item) if index == 0 else str + "']['{}".format(item)
        str += "']"

        return eval("self.response{}".format(str))

    #返回数据
    def responseHandlerForJson(self):
        if str(self.response.get(self.rules.get("return").get("codeKey"))) != str(self.rules.get("return").get("ok")):
            raise PubErrorCustom(self.response.get(self.rules.get("return").get("msgKey")))
        return self.rDataMapForJson()

    #向上游发起请求
    def requestHandlerForHtml(self):

        logger.info("向上游请求的值：{}".format(self.request_data))
        html="""

            <html lang="zh-CN"><head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>傲银支付</title>
            </head>
                <body>
                    <div class="container">
                        <div class="row" style="margin:15px;">
                            <div class="col-md-12">
                                <form class="form-inline" method="{}" action="{}">
            """.format(self.rules['request']['method'],self.rules['request']['url'])
        for key,value in self.request_data.items():
            html+="""<input type="hidden" name="{}" value="{}">""".format(key,value)

        html += """
                                </form>
                            </div>
                        </div>
                    </div>

                    <script src="http://47.75.120.33//static/jquery-1.4.1.min.js"></script>

                    <script>
                        $(function(){document.querySelector('form').submit();})
                    ;</script>
                </body>
            </html>
        """
        RedisOrderCreate().redis_insert(md5pass(str(self.data['ordercode'])),html)

    #返回html时处理
    def responseHandlerForHtml(self):
        return url_join("/api_new/business/DownOrder?o={}".format(md5pass(str(self.data['ordercode']))))

    def runForJson(self):

        self.requestHandlerForJson()
        return self.responseHandlerForJson()

    def runForHtml(self):
        self.requestHandlerForHtml()
        return self.responseHandlerForHtml()

    def run(self):
        self.dataHandler()
        if self.rules['request']['password']:
            self.passHandler()
        if self.rules['request']['sign']:
            self.signHandler()
        self.reuquestBeforeDataHandler()
        if self.rules['return']['type'] == 'json':
            return self.runForJson()
        else:
            return self.runForHtml()


class CustDateType(object):

    @staticmethod
    def get_amount(obj):
        if obj['unit'] == 'F':
            # return float(Decimal(str(float(obj['value']) * 100.0)).quantize(Decimal(obj['point']))) if 'point' in obj else float(obj['value']) * 100.0
            return "%.{}lf".format(int(obj['point'])) % (float(obj['value']) * 100.0) if 'point' in obj else float(obj['value']) * 100.0
        elif obj['unit'] == 'Y':
            # return float(Decimal(str(float(obj['value']))).quantize(Decimal(obj['point']))) if 'point' in obj else float(obj['value'])
            return "%.{}lf".format(int(obj['point'])) % (float(obj['value'])) if 'point' in obj else float(obj['value'])
        else:
            raise PubErrorCustom("标志错误!")

    @staticmethod
    def get_date(obj):
        if obj.get("type") == "appoint":
            return obj.get("value")
        else:
            ut = UtilTime()
            return ut.timestamp * 1000 \
                if obj.get("format", None) == 'timestamp' else \
                ut.arrow_to_string(arrow_s=ut.today, format_v=obj.get("format", None)) if obj.get("format", None) \
                    else ut.arrow_to_string(arrow_s=ut.today)

    @staticmethod
    def get_string(obj):
        return str(obj.get("value"))

    @staticmethod
    def get_int(obj):
        return int(obj.get("value"))

class PassBase(object):
    def __init__(self,**kwargs):

        #请求的值
        self.hashData = kwargs.get("hashData",None)

        #加密的值
        self.signData = kwargs.get("signData",None)

        #加密规则
        self.signRules = kwargs.get("signRules",None)

    def hashBeforeHandler(self):

        # 按字典key ascii码排序(key-value) 并过滤空值
        if self.signRules["signDataType"] == 'key-ascii-sort':
            strJoin = ""
            for item in sorted({k: v for k, v in self.signData.items() if v != ""}):
                strJoin += "{}={}&".format(str(item), str(self.signData[item]))
            strJoin = strJoin[:-1]
            if self.signRules.get("signAppend", None):
                strJoin = "{}{}".format(strJoin, self.signRules["signAppend"].format(**self.hashData))
            if self.signRules.get("signBefore", None):
                strJoin = "{}{}".format(self.signRules["signBefore"].format(**self.hashData), strJoin)

            return strJoin

        # 按指定key排序
        elif self.signRules["signDataType"] == 'key-appoint':
            strJoin = self.signRules["signValue"].format(**self.hashData)
            if self.signRules.get("signAppend", None):
                strJoin = "{}{}".format(strJoin, self.signRules["signAppend"].format(**self.hashData))
            if self.signRules.get("signBefore", None):
                strJoin = "{}{}".format(self.signRules["signBefore"].format(**self.hashData), strJoin)

            return strJoin

        # 按json字符串
        elif self.signRules["signDataType"] == 'key-json':
            return json.dumps(self.signData, ensure_ascii=False).replace(' ','')

    def aesPass(self):
        signData = self.hashBeforeHandler()
        logger.info("请求待加密字符串：{}".format(signData))

        res = AES.new(key=self.signRules['Gpass'].encode('utf-8'),mode=AES.MODE_CBC,iv=self.signRules['cheap'].encode('utf-8')). \
                    encrypt(getattr(self, self.signRules['tianchong'])(signData).encode('utf-8'))

        return str(base64.b64encode(res),"utf-8") if self.signRules['Pout'] == 'base64' else str(res.hex(),"utf-8")

    def pkcs5padding(self,s):
        aes_len = AES.block_size
        return s + (aes_len - len(s) % aes_len) * chr(aes_len - len(s) % aes_len)


    def run(self):
        return getattr(self,self.signRules['signType'])()

class SignBase(object):

    def __init__(self,**kwargs):

        #请求的值
        self.hashData = kwargs.get("hashData",None)

        #加密的值
        self.signData = kwargs.get("signData",None)

        #加密规则
        self.signRules = kwargs.get("signRules",None)


    def hashBeforeHandler(self):

        #按字典key ascii码排序(key-value) 并过滤空值
        if self.signRules["signDataType"] == 'key-ascii-sort':
            strJoin = ""
            for item in sorted({k: v for k, v in self.signData.items() if v != ""}):
                strJoin += "{}={}&".format(str(item),str(self.signData[item]))
            strJoin=strJoin[:-1]
            if self.signRules.get("signAppend", None):
                strJoin="{}{}".format(strJoin,self.signRules["signAppend"].format(**self.hashData))
            if self.signRules.get("signBefore", None):
                strJoin="{}{}".format(self.signRules["signBefore"].format(**self.hashData),strJoin)

            return strJoin

        #按指定key排序
        elif  self.signRules["signDataType"] == 'key-appoint':
            return self.signRules["signValue"].format(**self.hashData)

    def md5(self):
        signData = self.hashBeforeHandler()
        logger.info("请求待签名字符串：{}".format(signData))
        return hashlib.md5(signData.encode(self.signRules['signEncode'])).hexdigest().upper() \
            if self.signRules.get('dataType',None) == 'upper' else hashlib.md5(signData.encode(self.signRules['signEncode'])).hexdigest()

    def rsa_ecb_pkcs1padding(self):
        signData = self.hashBeforeHandler()
        logger.info("请求待签名字符串：{}".format(signData))
        self.signRules['Spass'] = "-----BEGIN RSA PRIVATE KEY-----\n" + self.signRules['Spass'] + "\n-----END RSA PRIVATE KEY-----"
        return str(base64.b64encode(PKCS1_v1_5.new(RSA.importKey(self.signRules['Spass'])).sign(SHA.new(signData.encode("utf-8")))),'utf-8')

    def run(self):
        return getattr(self,self.signRules['signType'])()


class SignBaseCustom(object):

    def __init__(self,**kwargs):

        #请求的值
        self.hashData = kwargs.get("hashData",None)

        #加密的值
        self.signData = kwargs.get("signData",None)

        #加密规则
        self.signRules = kwargs.get("signRules",None)


    def md5(self):
        s = "?amount={amount}&attach={attach}&outOrderNo={outOrderNo}&payType={payType}{appId}{nonceStr}{timestamp}".format(**self.hashData)
        print(s)
        s = hashlib.md5(s.encode(self.signRules['signEncode'])).hexdigest()
        s+=self.hashData['secret']
        print(s)
        s = hashlib.md5(s.encode(self.signRules['signEncode'])).hexdigest().upper()
        return s



if __name__ == '__main__':
    CreateOrderForLastPass().run()