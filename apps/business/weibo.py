
import requests
import base64
import re
import rsa
import random
import urllib3
import json
import time
from urllib.parse import unquote,quote
from binascii import b2a_hex

urllib3.disable_warnings() # 取消警告

def get_timestamp():
    return int(time.time()*1000)

class WeiboBase(object):

    def __init__(self,**kwargs):
        self.amount = kwargs.get("amount")
        self.num = kwargs.get("num")
        self.sessionRes = kwargs.get("sessionRes",None)
        self.session = kwargs.get("session",None)
        self.cookieKey = kwargs.get("cookieKey",'.weibo.com')
        print("红包金额: {}分 ----- 红包数量: {} \n 会话:{}".format(self.amount,self.num,self.sessionRes))

        self.isSession=kwargs.get("isSession", None)
        self.get_session()

    def datainitHandler(self):
        html = self.session.get('https://hongbao.weibo.com/h5/pay?groupid=1000303&ouid={}'.format(self.sessionRes['uid'])).text
        self.sessionRes['st'] = html.split("st:")[1].split(",")[0].replace("'","")

    def get_session(self):
        try:
            if not self.sessionRes:
                self.sessionRes={}

            if self.isSession:
                self.session = requests.session()
                self.session.verify = False

                self.session.headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
                }

                for key,value in self.sessionRes['cookie'][self.cookieKey].items():
                    self.session.cookies.set(key, value)
            else:
                if not self.session:
                    self.session = requests.session()
                    self.session.verify = False

                    self.session.headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
                    }
                else:
                    self.session.verify = False

        except Exception as e:
            raise Exception("无可用session!")

class WeiboHbPay(WeiboBase):

    def __init__(self,**kwargs):

        self.payScWeiboUrl = None
        self.payScWeiboParams = None
        self.wapPayUrl = None
        self.ordercode = None
        kwargs.setdefault("isSession",True)
        super(WeiboHbPay,self).__init__(**kwargs)
        self.session.headers['Referer'] = "https://hongbao.weibo.com/h5/pay?groupid=1000303&ouid={}".format(self.sessionRes['uid'])
        self.session.headers['Content-Type'] = "application/x-www-form-urlencoded"
        self.session.headers['Origin'] = "https://hongbao.weibo.com"
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)'

    def getPayUrl(self):
        url = "https://hongbao.weibo.com/aj_h5/createorder?st={}&current_id={}".format(self.sessionRes['st'],self.sessionRes['uid'])
        data = {
            "uid": self.sessionRes['uid'],
            "groupid": "1000303",
            "eid": 0,
            "amount": self.amount,
            "num": self.num,
            "share": 0,
            "_type": 1,
            "isavg": 0,
            "tab": 2,
            "pass":"123456"
        }
        res = json.loads(self.session.post(url=url, data=data).content.decode("utf-8"))
        print("getPayUrl: {}".format(res))
        if res['ok'] != 1:
            #授权失败
            raise Exception(res['msg'])
        else:
            # self.payScWeiboUrl = res['url']
            #暂时用这种方式跳转
            return res['url'],res['url'].split("out_pay_id=")[1].split('&')[0]

    def getPayParams(self):

        params =  ""
        try:
            self.session.get(url=self.payScWeiboUrl)
        except Exception as a:
            # print(a)
            params = str(a).split("No connection adapters were found for")[1].\
                replace("sinaweibo://wbpay?", "").replace("'",'').split("pay_params=")[1]
            params = unquote(params, 'utf-8')
            print(params)
        self.payScWeiboParams = params

    def orderForWeibo(self):
        data={
            'uid' : self.sessionRes['uid'],
            'gsid' : self.sessionRes['gsid'],
            'request_str' : self.payScWeiboParams,
            'is4g' : 0,
            'apple_pay_allowed' :  0,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/prepare"
        try:
            res = self.session.post(url=url,data=data)
        except Exception as e:
            raise  Exception("createOrderForWeibo Error ： {}".format(str(e)))

    def orderForAliPay(self):

        data={
            'uid' : self.sessionRes['uid'],
            'gsid' : self.sessionRes['gsid'],
            "channel" : "ali_wap",
            "coupon_amount" : 0,
            'request_str' : self.payScWeiboParams,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/buildparams"
        self.session.headers['User-Agent'] = 'iOS__iPhone__iOS__12.4.1__828*1792__iPhone11,8__arm64e__0__9.11.2__2.0.0'

        try:
            res = json.loads(self.session.post(url=url, data=data).content.decode('utf-8'))
            if res['code'] != "100000":
                raise Exception("系统异常,请联系管理员!")
            # 成功 code=="100000"
            print(res)
            self.wapPayUrl = res['data']['wap_pay_url']
            self.ordercode = res['data']['pay_id']
        except Exception as e:
            print("orderForAliPay ! ： {}".format(str(e)))
            raise Exception("系统异常,请联系管理员!")

    def createSkipAliPayResponse(self):
        # print(self.headers)
        print(self.wapPayUrl)
        html = self.session.get(url=self.wapPayUrl).text

        return html,self.ordercode

    def run(self):
        self.datainitHandler()
        return self.getPayUrl()

class WeiboHbHandler(WeiboBase):

    def __init__(self,**kwargs):
        super(WeiboHbHandler, self).__init__(**kwargs)
        self.session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

    def Hblist(self,page=1):

        url="https://hongbao.weibo.com/aj_h5/hongbaopage?page={}".format(page)
        res = json.loads(self.session.get(url=url).content.decode('utf-8'))
        return res['cnt'],res['data']['list']


class WeiboLogin(WeiboBase):

    def __init__(self,**kwargs):

        super(WeiboLogin,self).__init__(**kwargs)
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)'

    def get_vercode(self,username):
        url = """
        https://api.weibo.cn/2/account/login_sendcode?wm=3333_2001&sensors_mark=0&uid=1014111034742&sensors_is_first_day=false&from=109B293010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&v_f=1&networktype=wifi&checktoken=1d4
a525091a7e60e4dced9f69b2e488b&did=6c622ce71e3a34c27cbd3b658eb8614e&lang=zh_CN&ua=iPhone11,8__weibo__9.11.2__iphone__os12.4.1&sflag=1&ft=0&aid=01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.&b=0&launchid=icon
        """

        data={
            "moduleID":"account",
            "orifid":"102803%24%240",
            "featurecode":"10000225",
            "uicode":"10000944",
            "luicode":"10000384",
            "phone":username,
            "lfid":"0",
            "oriuicode":"10000225_10000384"
        }

        try:
            res = json.loads(self.session.post(url=url,data=data).content.decode("utf-8"))
            if 'sendsms' in res and res['sendsms']:
                print("发送成功!")
            else:
                raise Exception(res['errmsg'])
        except Exception as e:
            print(str(e))
            raise Exception("发送验证码不成功!,请联系管理员!")

    def login(self,username,smscode):

        url = """
        https://api.weibo.cn/2/account/login?wm=3333_2001&sensors_mark=0&uid=1014111034742&sensors_is_first_day=false&from=109B293010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&v_f=1&networktype=wifi&checktoken=1d4a525091a7e60e4dced9f69b2e488b&did=6c622ce71e3a34c27cbd3b658eb8614e&lang=zh_CN&ua=iPhone11,8__weibo__9.11.2__iphone__os12.4.1&sflag=1&ft=0&aid=01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.&b=0&launchid=icon
        """
        """

        """
        data=dict(
            guestid="1014111034742",
            getcookie="1",
            uicode="10000062",
            imei="b3103498dc4cc5d7a32ad955b837aeba70766e74",
            device_name="iPhone",
            device_id="6c622ce71e3a34c27cbd3b658eb8614e83ab357b",
            moduleID="account",
            request_ab="1",
            preload_ab="1",
            luicode="10000944",
            phone=username,
            orifid="102803%24%240%24%240",
            featurecode="10000225",
            cfrom="",
            smscode=smscode,
            oriuicode="10000225_10000384_10000944",
            lfid=0
        )

        try:
            return self.filterloginres(json.loads(self.session.post(url=url, data=data).content.decode("utf-8")))
        except Exception as e:
            print(str(e))
            raise Exception("登录错误,请联系管理员!")

    def pcLogin(self,username,password):

        '''预登录，获取一些必须的参数'''
        self.su = base64.b64encode(username.encode())  #阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(quote(self.su),get_timestamp()) #注意su要进行quote转码
        response = self.session.get(url).content.decode()
        # print(response)
        self.nonce = re.findall(r'"nonce":"(.*?)"',response)[0]
        self.pubkey = re.findall(r'"pubkey":"(.*?)"',response)[0]
        self.rsakv = re.findall(r'"rsakv":"(.*?)"',response)[0]
        self.servertime = re.findall(r'"servertime":(.*?),',response)[0]

        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey, 16), int('10001', 16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(password)
        self.sp = b2a_hex(rsa.encrypt(message.encode(), publickey))

        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
            'vsnf': '1',
            'su': self.su,
            'service': 'miniblog',
            'servertime': str(int(self.servertime) + random.randint(1, 20)),
            'nonce': self.nonce,
            'pwencode': 'rsa2',
            'rsakv': self.rsakv,
            'sp': self.sp,
            'sr': '1536 * 864',
            'encoding': 'UTF - 8',
            'prelt': '35',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }
        response = self.session.post(url, data=data, allow_redirects=False).text  # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);', response)[0]  # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url, allow_redirects=False).text  # 请求跳转页面
        ticket, ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"', result)[0]  # 获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(
            ticket, ssosavestate, get_timestamp())
        data = self.session.get(uid_url).text  # 请求获取uid
        uid = re.findall(r'"uniqueid":"(.*?)"', data)[0]

        sessionRes={}
        for key,value in self.session.cookies._cookies['.weibo.com']['/'].items():
            sessionRes[key] = value.value

        return sessionRes

    def filterloginres(self,res):

        # res = json.loads(res)

        session=dict(
            gsid = res['gsid'],
            uid = res['uid'],
            cookie=res['cookie']['cookie']
        )
        for key,value in session['cookie'].items():
            session['cookie'][key]=dict()
            for item in value.split('\n'):
                itemtmp = item.split(';')[0]
                key1 = itemtmp.split('=')[0]
                value1 = itemtmp.split('=')[1]
                session['cookie'][key][key1] = value1

        return session,res

class WeiboCallBack(WeiboBase):

    def __init__(self,**kwargs):

        super(WeiboCallBack,self).__init__(**kwargs)
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        self.session.headers['Host'] = 'pay.sc.weibo.com'
        self.session.headers['Origin'] = 'https://pay.sc.weibo.com'
        self.session.headers['Referer'] = 'https://pay.sc.weibo.com/center/pc/c'

    def queryOrderForWeibo(self,ordercode,start_time,end_time):


        url = "https://pay.sc.weibo.com/aj/pc/biz/list"
        data={
            "biz_type":0,
            "status":0,
            "start_time":start_time,
            "end_time":end_time,
            "page":1,
            "page_size":10,
            # "biz_id":ordercode
            "order_id":"7400006072333"
        }
        res = json.loads(self.session.post(url,data).content.decode('utf-8'))
        if res['code']!='100000':
            return False,res['msg']
        else:
            return True,res['data']['biz']

if __name__ == '__main__':

    session={"uid": "6424853549", "cookie": {"pccookie": {"SCF": "ApRjxfCUUgfZNrF6C-HMazivcfDQbJiaECq4NBIyzO-7qfkLBMv_enLJz8HcyxX0WIQUqqiZM9r8wejh_LzAZIs.", "SUB": "_2A25w7XvhDeRhGeBK6VYZ9S3JzzWIHXVTm-oprDV8PUNbmtBeLW_CkW9NR848UCVap-qDZJKJ3LU3NXLocobowOsJ", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5JpX5K2hUgL.FoqXeoBRSKefSh.2dJLoIEQLxK-LBoMLBKqLxKqL1h.L12zLxKqL1--LB-zLxK-L12qLBo9k1K-NSKet", "SUHB": "0h1J80SCC16sb9", "ALF": "1607089958", "SSOLoginState": "1575553969"}}}
    session={"uid": "6424853549", "cookie": {"pccookie": {"SCF": "AolqRXzRJ_aPgQVpQgZA7t9w3wiXSqHS6J9VjMQv1aJ2h9c44_YdTJlkamjdiJiPybNAvwXG-3bUUosi2RoRDVA.", "SUB": "_2A25w7cV-DeRhGeBK6VYZ9S3JzzWIHXVTmrG2rDV8PUNbmtBeLUfYkW9NR848UHj9tFke__L7cb99SupV7Kc8swns", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5JpX5K2hUgL.FoqXeoBRSKefSh.2dJLoIEQLxK-LBoMLBKqLxKqL1h.L12zLxKqL1--LB-zLxK-L12qLBo9k1K-NSKet", "SUHB": "0jBIffZWGBj5F6", "ALF": "1607133356", "SSOLoginState": "1575597359"}}}

    s = WeiboHbHandler(sessionRes=session,cookieKey='pccookie',isSession=True)
    count,res=s.Hblist(page=1)
    print(count)
    print(json.dumps(res))

    # s=WeiboHbPay(sessionRes=session,amount=0.01,num=1,cookieKey='pccookie')

    # url,ordercode = s.run()
    # print(url)

    # s.payScWeiboUrl="https://pay.sc.weibo.com/api/merchant/pay/cashier?sign_type=RSA&sign=J%2BtikUjFUJIJmGkIssk9zq%2BHjaEyNd%2FNYzEx%2BpTEec8wlseEyqekmncRO1MkX0W4a0G0nkdoJ0rB10jWQs9SPATSt6HZYC%2B%2BZ8vaM77%2BEKBHqjiMdPtjtBdp0JggjWzp1Z%2Bnet42Sm%2BYOd20MEMIE8kotMiGokbpi%2FFlIRstN%2Bw%3D&seller_id=5136362277&appkey=743219212&out_pay_id=7100028362275&notify_url=https%3A%2F%2Fhb.e.weibo.com%2Fv2%2Fbonus%2Fpay%2Fwnotify&return_url=https%3A%2F%2Fhb.e.weibo.com%2Fv2%2Fbonus%2Fpay%2Fwreturn%3Fsinainternalbrowser%3Dtopnav&subject=%E5%BE%AE%E5%8D%9A%E7%BA%A2%E5%8C%85&body=%E7%B2%89%E4%B8%9D%E7%BA%A2%E5%8C%85&total_amount=1&cfg_follow_uid=5136362277&cfg_share_opt=0&cfg_follow_opt=0"
    # s.getPayParams()

    # s=WeiboLogin(cookieKey='pccookie').pcLogin(username="18580881001",password="!@#tc123")
    # print(s)
    # flag,s= WeiboCallBack(sessionRes=session,cookieKey='pccookie',isSession=True).queryOrderForWeibo(ordercode="124445895886903999",start_time="2019-12-03",end_time="2019-12-05")
    # print(flag,s)
    # if not flag:
    #     print("查询失败!")
    # else:
    #     if not len(s):
    #         print("查询无数据")
    #     else:
    #         if s[0]['status'] == '2':
    #             print("交易成功")
    #         elif s[0]['status'] == '4':
    #             print("交易关闭")
    #         elif s[0]['status'] == '1':
    #             print("待付款")
    #         else:
    #             print("未知状态")