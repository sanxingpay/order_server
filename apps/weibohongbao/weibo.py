import requests,base64,re,rsa,random,urllib3,json,time,math
from bs4 import BeautifulSoup
from urllib.parse import unquote,quote
from binascii import b2a_hex
urllib3.disable_warnings() # 取消警告
import re

class WeiboBase(object):

    def __init__(self,**kwargs):

        self.sessionRes = kwargs.get("sessionRes",None)
        self.cookieKey = kwargs.get("cookieKey",None)
        # print("会话:{}".format(self.sessionRes))

        self.session = requests.session()
        self.get_session()

        self.getProxyCount = 0

    def get_proxy(self):
        try:
            proxy = json.loads(requests.request(url="http://allwin6666.com/proxy/get/",method="GET").content.decode('utf-8'))['proxy']
            self.getProxyCount = 0
            return proxy
        except Exception:
            if self.getProxyCount >= 3:
                self.getProxyCount = 0
                return None
            else:
                self.get_proxy()
            self.getProxyCount+=1

    def use_proxy(self):
        r = self.get_proxy()
        if r:
            self.session.proxies={"http":r}

    def get_session(self):
        self.session = requests.session()
        self.session.verify = False
        if not self.sessionRes:
            self.session.headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
            }
        else:
            self.session.headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
            }
            if "cookie" in self.sessionRes and self.cookieKey in self.sessionRes['cookie'] and isinstance(self.sessionRes['cookie'][self.cookieKey],dict):
                for key, value in self.sessionRes['cookie'][self.cookieKey].items():
                    self.session.cookies.set(key, value)

    def reset_session(self,sessionRes,cookieKey):
        self.sessionRes = sessionRes
        self.cookieKey = cookieKey
        self.get_session()

class WeiboLogin(WeiboBase):

    """
    微博登录
    """

    def __init__(self,**kwargs):
        super(WeiboLogin, self).__init__(**kwargs)

class WeiboLoginForPc(WeiboLogin):

    def __init__(self,**kwargs):
        super(WeiboLoginForPc, self).__init__(**kwargs)

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }

        self.username = kwargs.get("username",None)
        self.password = kwargs.get("password",None)
        self.login_params = None

    def preLogin(self):
        '''预登录，获取一些必须的参数'''
        su = base64.b64encode(self.username.encode())  # 阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(
            quote(su), int(time.time()*1000))  # 注意su要进行quote转码
        response = self.session.get(url).content.decode()

        self.login_params = {
            "nonce":re.findall(r'"nonce":"(.*?)"', response)[0],
            "pubkey":re.findall(r'"pubkey":"(.*?)"', response)[0],
            "rsakv":re.findall(r'"rsakv":"(.*?)"', response)[0],
            "servertime":re.findall(r'"servertime":(.*?),', response)[0],
            "showpin": re.findall(r'"showpin":(.*?),', response)[0],
            "vercode":None,
            "pcid":re.findall(r'"pcid":(.*?),', response)[0].replace('"',''),
            "su":su
        }

    def getvercodeUrl(self):
        url = "https://login.sina.com.cn/cgi/pin.php?&r={}&s=0&p={}".format(math.floor(random.random() * 1e8), self.login_params['pcid'])
        return url

    def login(self):
        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.login_params['pubkey'], 16), int('10001', 16))
        message = str(self.login_params['servertime']) + '\t' + str(self.login_params['nonce']) + '\n' + str(self.password)
        sp = b2a_hex(rsa.encrypt(message.encode(), publickey))

        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1',
            'vsnf': '1',
            'su': self.login_params['su'],
            'service': 'miniblog',
            'servertime': str(int(self.login_params['servertime']) + random.randint(1, 20)),
            'nonce': self.login_params['nonce'],
            'pwencode': 'rsa2',
            'rsakv': self.login_params['rsakv'],
            'sp': sp,
            'sr': '1536 * 864',
            'encoding': 'UTF - 8',
            'prelt': '35',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }
        if self.login_params['showpin'] == '1':
            data['pcid'] = self.login_params['pcid']
            data['door'] = self.login_params['vercode']

        response = self.session.post(url, data=data, allow_redirects=False).text  # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);', response)[0]  # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url, allow_redirects=False).text  # 请求跳转页面
        ticket, ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"', result)[0]  # 获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(
            ticket, ssosavestate, int(time.time()*1000))
        data = self.session.get(uid_url).text  # 请求获取uid
        sessionRes={}
        sessionRes['uid'] = re.findall(r'"uniqueid":"(.*?)"', data)[0]
        sessionRes['cookie'] = {}
        sessionRes['cookie']['pccookie']={}
        for key, value in self.session.cookies._cookies['.weibo.com']['/'].items():
            sessionRes['cookie']['pccookie'][key] = value.value

        return sessionRes

class WeiBoLoginForPhone(WeiboLogin):

    def getvercode(self,username):
        """
        手机登录获取验证码
        :param username: 手机号
        :return:
        """
        url = """
                https://api.weibo.cn/2/account/login_sendcode?wm=3333_2001&sensors_mark=0&uid=1014111034742&sensors_is_first_day=false&from=109B293010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&v_f=1&networktype=wifi&checktoken=1d4
        a525091a7e60e4dced9f69b2e488b&did=6c622ce71e3a34c27cbd3b658eb8614e&lang=zh_CN&ua=iPhone11,8__weibo__9.11.2__iphone__os12.4.1&sflag=1&ft=0&aid=01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.&b=0&launchid=icon
                """

        data = {
            "moduleID": "account",
            "orifid": "102803%24%240",
            "featurecode": "10000225",
            "uicode": "10000944",
            "luicode": "10000384",
            "phone": username,
            "lfid": "0",
            "oriuicode": "10000225_10000384"
        }

        try:
            res = json.loads(self.session.post(url=url, data=data).content.decode("utf-8"))
            if 'sendsms' in res and res['sendsms']:
                print("发送成功!")
            else:
                raise Exception(res['errmsg'])
        except Exception as e:
            print(str(e))
            raise Exception("发送验证码不成功!,请联系管理员!")

    def login_by_vercode(self,username,vercode):
        """
        手机端验证码登录
        :param username:
        :return:
        """
        url = """
                https://api.weibo.cn/2/account/login?wm=3333_2001&sensors_mark=0&uid=1014111034742&sensors_is_first_day=false&from=109B293010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&v_f=1&networktype=wifi&checktoken=1d4a525091a7e60e4dced9f69b2e488b&did=6c622ce71e3a34c27cbd3b658eb8614e&lang=zh_CN&ua=iPhone11,8__weibo__9.11.2__iphone__os12.4.1&sflag=1&ft=0&aid=01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.&b=0&launchid=icon
                """
        """

        """
        print(username,vercode)
        data = dict(
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
            smscode=vercode,
            oriuicode="10000225_10000384_10000944",
            lfid=0
        )

        try:
            return self.filterloginres(json.loads(self.session.post(url=url, data=data).content.decode("utf-8")))
        except Exception as e:
            print(str(e))
            raise Exception("登录错误,请联系管理员!")

    def filterloginres(self,res):

        # res = json.loads(res)

        print(res)
        session=dict(
            gsid = res['gsid'],
            uid = res['uid'],
            cookie=res['cookie']['cookie'],
            s="8e3487ea",
            aid="01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.",
        )
        for key,value in session['cookie'].items():
            session['cookie'][key]=dict()
            for item in value.split('\n'):
                itemtmp = item.split(';')[0]
                key1 = itemtmp.split('=')[0]
                value1 = itemtmp.split('=')[1]
                session['cookie'][key][key1] = value1

        return session

class WeiboGroup(WeiboBase):
    """
    群管理
    """

    def __init__(self,**kwargs):

        kwargs.setdefault("cookieKey", ".weibo.com")
        super(WeiboGroup,self).__init__(**kwargs)

        self.params="?gsid={}&sensors_mark=0&wm=3333_2001&sensors_is_first_day=false&from=109B493010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&s={}&v_f=1&networktype=wifi&b=0&lang=zh_CN&ua=iPhone11,8__weibo__9.11.4__iphone__os12.4.1&sflag=1&ft=0&aid={}&launchid=10000365--x".format(
            self.sessionRes['gsid'],
            self.sessionRes['s'],
            self.sessionRes['aid']
        )

    def create(self,name):
        """
        创建群组
        :param name:
            name : 群名称
        :return:
        """

        # self.reset_session(None,None)
        # self.session.headers['Content-type']="application/x-www-form-urlencoded; charset=utf-8"
        # self.session.headers['User-agent'] = "Weibo/39290 (iPhone; iOS 12.4.1; Scale/2.00)"

        #创建群前先调用检查接口
        url = """https://api.weibo.cn/2/groupchat/check_valid"""+self.params

        data={
            "orifid": "0$$0",
            "uicode": "10000983",
            "luicode": "10000251",
            "has_affiliation" : "1",
            "text": name,
            "lfid":"0",
            "type":"1",
            "oriuicode":"10000414_10000251"
        }
        print(self.params)
        print(data)
        rRes=self.session.post(url=url,data=data)
        res = json.loads(rRes.content.decode('utf-8'))
        print(res)
        if "errmsg" in res and res['errmsg']:
            raise Exception(res['errmsg'])

        # 创建群
        url="""https://api.weibo.cn/2/groupchat/create"""+self.params

        data={
            "page_type": "1",
            "validate_type": "3",
            "orifid": "0$$0",
            "members": self.sessionRes['uid'],
            "publicity" : "1",
            "fromapp":"2",
            "uicode": "10000983",
            "summary":"",
            "lfid": "0",
            "name":name,
            "oriuicode":"10000414_10000251"
        }
        res = json.loads(self.session.post(url=url,data=data).content.decode('utf-8'))
        if "errmsg" in res and res['errmsg']:
            raise Exception(res['errmsg'])
        else:
            #务必保存群数据后续需要使用
            return res

    def join(self,groupid,uids):

        """
        加入成员
        :param groupid:
            groupid : 群ID
            uids: 成员ID集合(逗号隔开)
        :return:
        """

        url="""https://api.weibo.cn/2/groupchat/join"""

        data = {
            "moduleID":"wymessage",
            "orifid":"0$${}$$0".format(groupid),
            "uicode":"10000251",
            "id":groupid,
            "luicode":"10000253",
            "validate_type":"1",
            "uids": uids,
            "lfid":"0",
            "oriuicode":"10000414_10000254_10000253"

        }
        rRes = self.session.post(url=url, data=data,params=self.params)
        res = json.loads(rRes.content.decode('utf-8'))
        # print(res)
        if "errmsg" in res and res['errmsg']:
            raise Exception(res['errmsg'])

class WeiboFollow(WeiboBase):
    """
    关注管理
    """

    def __init__(self,**kwargs):

        kwargs.setdefault("cookieKey","pccookie")

        super(WeiboFollow, self).__init__(**kwargs)

        self.session.headers['Content-type'] = "application/x-www-form-urlencoded; charset=utf-8"
        self.session.headers['User-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        self.session.headers['Origin'] = 'https://www.weibo.com'

    def follow(self,to):
        """
        关注
        :return:
        """
        print("关注的人:",to)
        pass
        self.session.headers['Referer'] = 'https://www.weibo.com/u/{}?is_hot=1&noscale_head=1'.format(to)
        url="https://www.weibo.com/aj/f/followed?ajwvr=6"

        data={
            "uid":to,
            "f":"1",
            "objectid":"",
            "extra":"",
            "refer_sort":"",
            "location":"page_100505_home",
            "oid":to,
            "wforce":"1",
            "nogroup":"1",
            "refer_from":"profile_headerv6",
            "template":7,
            "special_focus":1,
            "isrecommend":1,
            "is_special":0,
            "_t":0
        }
        r=self.session.post(url=url,data=data)
        print(r.text)
        res = json.loads(r.content.decode("utf-8"))
        if res['code'] != "100000":
            raise Exception(res['msg'])

class WeiboPay(WeiboBase):

    def __init__(self,**kwargs):
        kwargs.setdefault("cookieKey", ".weibo.com")
        super(WeiboPay, self).__init__(**kwargs)

    def pay(self,price,amount,num,msgid=""):

        """
        :param price: 单价
        :param amount: 总价
        :param num: 数量
        :param msgid: 群组ID
        :return:
        """
        self.session.headers['Host'] = "mall.e.weibo.com"
        self.session.headers['Accept'] = '* / *'
        self.session.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.session.headers['Accept-Language'] = 'zh-cn'
        self.session.headers['Accept-Encoding'] = 'gzip, deflate'
        self.session.headers['Content-Type'] = "application/x-www-form-urlencoded"
        self.session.headers['Origin'] = "http://mall.e.weibo.com"
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)'
        self.session.headers['Referer'] = "http://mall.e.weibo.com/h5/redenvelope/create?uicode=10000254&page=2&sinainternalbrowser=topnav&portrait_only=1&msgid={}&msgtype=2".format(msgid)

        url = "http://mall.e.weibo.com/aj/redenvelope/create"
        # self.use_proxy()
        data = {
            "bag_type": 1,
            "puicode": "",
            "msgtype": 2,
            "msgid": msgid,
            "aid": "01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.",
            "singalAmount": "%.2lf"%price,
            "count": num,
            "blessing": "快来抢，手快有，手慢无。恭喜发财！",
            "amount": "%.2lf"%amount,
            "_t": 0
        }
        rRes=self.session.post(url=url, data=data)
        print(rRes)
        res = json.loads(rRes.content.decode("utf-8"))
        print(res)
        if res['code'] != "100000":
            raise Exception(res['msg'])
        return res['data']['url'], res['data']['url'].split("out_pay_id=")[1].split('&')[0]

    def getPayId(self,url):
        print(url)
        self.reset_session(sessionRes=self.sessionRes,cookieKey='.weibo.com')
        params = unquote(self.session.head(url=url,stream=True).headers['Location'].replace("sinaweibo://wbpay?", "").split("pay_params=")[1],'utf-8')
        print(params)

        data = {
            'uid': self.sessionRes['uid'],
            'gsid': self.sessionRes['gsid'],
            'request_str': params,
            'is4g': 0,
            'apple_pay_allowed': 0,
            'from': "109B293010",
            "v_p": 78,
            "wm": "3333_2001",
            "lang": "zh_CN"
        }

        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/prepare"
        try:
            self.session.post(url=url, data=data)
        except Exception as e:
            raise Exception("createOrderForWeibo Error ： {}".format(str(e)))

        data = {
            'uid': self.sessionRes['uid'],
            'gsid': self.sessionRes['gsid'],
            "channel": "ali_wap",
            "coupon_amount": 0,
            'request_str': params,
            'from': "109B293010",
            "v_p": 78,
            "wm": "3333_2001",
            "lang": "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/buildparams"
        self.session.headers['User-Agent'] = 'iOS__iPhone__iOS__12.4.1__828*1792__iPhone11,8__arm64e__0__9.11.2__2.0.0'

        try:
            res = json.loads(self.session.post(url=url, data=data).content.decode('utf-8'))
            if res['code'] != "100000":
                raise Exception("系统异常,请联系管理员!")
            # 成功 code=="100000"
            print(res)
            return res['data']['wap_pay_url'],res['data']['pay_id']
        except Exception as e:
            print("orderForAliPay ! ： {}".format(str(e)))
            raise Exception("系统异常,请联系管理员!")

    def createorder(self,url):
        html = self.session.get(url=url).text
        return html

    def queryOrderForWeibo(self,ordercode,start_time,end_time):

        self.reset_session(sessionRes=self.sessionRes,cookieKey=".weibo.cn")
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        self.session.headers['Host'] = 'pay.sc.weibo.com'
        self.session.headers['Origin'] = 'https://pay.sc.weibo.com'
        self.session.headers['Referer'] = 'https://pay.sc.weibo.com/center/pc/c'
        url = "https://pay.sc.weibo.com/aj/pc/biz/list"
        data={
            "biz_type":0,
            "status":0,
            "start_time":start_time,
            "end_time":end_time,
            "page":1,
            "page_size":10,
            "biz_id":ordercode
        }
        print(data)
        r=self.session.post(url,data)
        print(r.text)
        res = json.loads(r.content.decode('utf-8'))
        if res['code']!='100000':
            return False,res['msg']
        else:
            return True,res['data']['biz']

class WeiboHb(WeiboBase):

    """
    发红包
    """
    def __init__(self,**kwargs):
        kwargs.setdefault("cookieKey", ".weibo.com")
        super(WeiboHb, self).__init__(**kwargs)

        self.sendlist=[]

    def listfilter(self,html,max_set_id):

        soup = BeautifulSoup(html, "html.parser")

        result=[]
        for item in soup.find_all('li'):
            url = item.a['href']
            amount = item.find_all('p',class_='amount')[0].string.replace('元','')

            c = item.find_all('p', class_='amount_status')[0].string.strip().replace("\n", "")
            getcount = c.split('/')[0]
            sendcount = c.split('/')[1].replace('个', '')

            result.append({
                "url":url,
                "amount" : amount,
                "getcount":getcount,
                "sendcount":sendcount,
                "set_id":url.split('set_id=')[1].split('&')[0]
            })


        # pattern = re.compile(r'<a.*recvdetailowner.*set_id=.*?>')
        # result = [ {"url":item.replace('<a href="','').replace('">',''),"set_id":item.split('set_id=')[1].split('&')[0]} for item in pattern.findall(html) ]
        count = len(result)
        confirm_result = [ item for item in result if str(item['set_id']) > str(max_set_id) ]
        confirm_count = len(confirm_result)
        #confirm_count 小于 count 那么不往后面继续查
        return confirm_count>=count and len(confirm_result),confirm_result

    def getlist(self,year,page,type,max_set_id=0):
        """
        :param year: 查询的年份
        :param page: 页数
        :param type: 未知
        :param max_set_id: 最大的红包ID 为了减少查询次数,只查询大于此ID的红包
        :return:
        """
        self.session.headers['Host'] = "mall.e.weibo.com"
        self.session.headers['Accept'] = '*/*'
        self.session.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.session.headers['Accept-Language'] = 'zh-cn'
        self.session.headers['Accept-Encoding'] = 'br,gzip, deflate'
        self.session.headers['Content-Type'] = "application/x-www-form-urlencoded"
        self.session.headers['Origin'] = "http://mall.e.weibo.com"
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        self.session.headers['Referer'] = "https://mall.e.weibo.com/h5/redenvelope/redlist"
        url="https://mall.e.weibo.com/h5/aj/redenvelope/redlist"

        data={
            "type":type,
            "page":page,
            "year":year,
            "_t":0
        }

        rRes=self.session.post(url=url, data=data)
        res = json.loads(rRes.content.decode("utf-8"))
        # print(res['data']['count'])
        if res['code'] != "100000":
            raise Exception(res['msg'])

        return self.listfilter(res['data']['html'],max_set_id)

    def getlistAll(self,year,type,max_set_id):
        page=1
        while True:
            flag, res = self.getlist(year=year, type=type, page=page, max_set_id=max_set_id)
            for item in res:
                self.sendlist.append(item)
            if not flag:
                print("已经查完了")
                break
            page += 1
        return self.sendlist

    def send(self,data):
        print("正在发红包{}".format(data.swithurl))

        self.session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        # self.use_proxy()

        html = self.session.get(data.swithurl).text
        pattern = re.compile(r'继续发此红包')
        res = pattern.findall(html)

        if len(res) <= 0:
            return True

        pattern = re.compile(r'<a.*http://m.weibo.cn/groupChat/userChat/groupListForLuckyBag?.*?class=')
        data.referer = pattern.findall(html)[0].replace('<a href="', '').split('"')[0]

        self.session.headers={
            "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)",
        }

        res = self.session.get(url=data.referer)
        st = res.text.split('"st"')[1].split(",")[0].replace(':','').replace('"',"")

        url = "https://m.weibo.cn/groupChat/userChat/sendMsg/"

        self.session.headers['Referer'] = data.referer

        rdata={
            "group_id":data.groupid,
            "luckybag_url":"https://mall.e.weibo.com/redenvelope/draw?set_id={}".format(data.setid),
            "format":"cards",
            "st":st
        }
        res = json.loads(self.session.post(url=url,data=rdata).content.decode('utf-8'))
        if res['ok'] != 1:
            raise Exception(res['msg'])


        data.url = "https://mall.e.weibo.com/redenvelope/draw?set_id={}".format(data.setid)
        print("发送成功 {}".format(data.setid))
        return True

    # def sendAll(self,sendlist):
    #
    #     rDatas=[]
    #     for item in sendlist:
    #         self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    #
    #         html = self.session.get(item.swithurl).text
    #         pattern = re.compile(r'继续发此红包')
    #         res = pattern.findall(html)
    #
    #         if len(res)>0:
    #             pattern = re.compile(r'<a.*http://m.weibo.cn/groupChat/userChat/groupListForLuckyBag?.*?class=')
    #             item.referer = pattern.findall(html)[0].replace('<a href="', '').split('"')[0]
    #             res =self.send(item)
    #             # item.hburl = item['url']
    #             rDatas.append(res)
    #         else:
    #             print("红包关闭!{}".format(item.swithurl))
    #
    #     return rDatas

class WeiboHbGet(WeiboBase):

    """
    抢红包
    """
    def __init__(self,**kwargs):
        kwargs.setdefault("cookieKey", "pccookie")
        super(WeiboHbGet, self).__init__(**kwargs)

    def rob(self,url):
        # self.use_proxy()
        html = self.session.get(url=url).text
        res = re.compile(r'<a.*=zhadan_hongbao_gxth">?.*?</a>').findall(html)
        print(html)
        if res and len(res) > 0 and '感谢土豪' in res[0]:
            return True
        else:
            return False

if __name__ == '__main__':



    session={"gsid": "_2A25w9MNaDeRxGeFN7lMZ-SfKyzWIHXVRoFGSrDV6PUJbkdANLXCikWpNQAQcu2B0oTsTZP8MI3kNDYr4SUZcWXcG", "uid": "7351899609", "cookie": {".sina.com.cn": {"SUB": "_2A25w9OfBDeRhGeFN7lMZ-SfKyzWIHXVQaZOJrDV_PUJbitANLXHVkWtNQAQcu14c_yasim5BUMLWL1JU2FTy1OdT", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWFFJ5QfnFU--Qse1f4QD_45NHD95QNe0-p1h.4So54Ws4DqcjJi--fi-isi-8Fi--Xi-z4iK.7i--Xi-zRiKn7i--Ni-88i-zpeh2t"}, ".sina.cn": {"SUB": "_2A25w9OfBDeRhGeFN7lMZ-SfKyzWIHXVQaZOJrDV9PUJbitANLVr4kWtNQAQcu0XN8NC2LvsLT1ZFljCtPvXuFIqq", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWFFJ5QfnFU--Qse1f4QD_45NHD95QNe0-p1h.4So54Ws4DqcjJi--fi-isi-8Fi--Xi-z4iK.7i--Xi-zRiKn7i--Ni-88i-zpeh2t"}, ".weibo.com": {"SUB": "_2A25w9OfBDeRhGeFN7lMZ-SfKyzWIHXVQaZOJrDV8PUJbitANLWzZkWtNQAQcu3Gbr_dxwGTzXgzvcd3ywBpL2A_U", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWFFJ5QfnFU--Qse1f4QD_45NHD95QNe0-p1h.4So54Ws4DqcjJi--fi-isi-8Fi--Xi-z4iK.7i--Xi-zRiKn7i--Ni-88i-zpeh2t", "SCF": "AjOaGw1K_o2AsNr4Ql_tYHlQtrfZErk1nGXWd9lQzIdvHAU6ABK9bwq6DQZXozV3LA..", "SUHB": "0xnCCbShVtNsAQ"}, ".weibo.cn": {"SUB": "_2A25w9OfBDeRhGeFN7lMZ-SfKyzWIHXVQaZOJrDV6PUJbitANLVb4kWtNQAQcu2Ev3l_Rcrit-8T52gw3LH0VOE7B", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWFFJ5QfnFU--Qse1f4QD_45NHD95QNe0-p1h.4So54Ws4DqcjJi--fi-isi-8Fi--Xi-z4iK.7i--Xi-zRiKn7i--Ni-88i-zpeh2t", "SCF": "AjOaGw1K_o2AsNr4Ql_tYHlQtrfZErk1nGXWd9lQzIdvfyw2nWXUCRB368fjlOXacQ..", "SUHB": "0qj0zWym28v8Qg"}, "pccookie": {"SCF": "AuiYezcPwKdZmaKw_RVrBO1G71X2Lq-ormw-FAjA_CneFpmTFepVEpG1JInZHBiawjdOwU4GZF006ziMcyiz5TY.", "SUB": "_2A25w9MTXDeRhGeFN7lMZ-SfKyzWIHXVTg7EfrDV8PUNbmtBeLRn9kW9NQAQcuwegf38sJD6FAkB9clNHIq5p3GuG", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWFFJ5QfnFU--Qse1f4QD_45JpX5K2hUgL.FoM0SK2R1K.ceh.2dJLoIEqLxK-LB.qLB-zLxKBLBo.L1K5LxKBLBonL1h5LxKMLB--LBo27eBtt", "SUHB": "0vJIrTxZ7L4vkd", "ALF": "1607591942", "SSOLoginState": "1576055943"}}, "s": "06586e7d", "aid": "01A7-rs9h5H2UJarozhxkn1a8KGuR4gxRZsRYl94cHDdyCUxQ."}

    s=WeiboGroup(sessionRes=session)
    s.create("test4")