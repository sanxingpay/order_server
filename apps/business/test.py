
import hmac
import base64
from hashlib import sha256

def get_sign(data,appsecret):
    appsecret = appsecret.encode('utf-8')  # 秘钥
    data = data.encode('utf-8')  # 加密数据

    print(type(appsecret),type(data))
    signature = base64.b64encode(hmac.new(appsecret, data, digestmod=sha256).digest())
    print(signature)
    # 获取十六进制加密数据
    signature = hmac.new(appsecret, data, digestmod=sha256).hexdigest()
    print(signature)



get_sign("amount=1.64&currency=CNY&jOrderId=1110460&jUserId=1&jUserIp=192.168.0.1&merchantId=21effc28b373dbbb33bfd43f5f2a54ce&notifyUrl=http://47.75.120.33/callback_api/lastpass/callback&orderType=1&payWay=AliPay&signatureMethod=HmacSHA256&signatureVersion=1&timestamp=1586343243000","9e04f36acc10b8ed1df3ed03b512553c")