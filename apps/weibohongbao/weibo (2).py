import requests,base64,re,rsa,random,urllib3,json,time
from urllib.parse import unquote,quote
from binascii import b2a_hex
urllib3.disable_warnings() # 取消警告
import re

class WeiboBase(object):

    def __init__(self,**kwargs):

        self.sessionRes = kwargs.get("sessionRes",None)
        self.cookieKey = kwargs.get("cookieKey",None)
        print("会话:{}".format(self.sessionRes))

        self.session = requests.session()
        self.get_session()

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

    def reset_session(self,sessionRes=None,cookieKey=None):
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

    def login(self,username,password):
        pass

class WeiBoLoginForPhone(WeiboLogin):

    def getvercode(self,username):
        """
        手机登录获取验证码
        :param username: 手机号
        :return:
        """
        pass

    def login_by_vercode(self,username,vercode):
        """
        手机端验证码登录
        :param username:
        :return:
        """
        pass

class WeiboGroup(WeiboBase):
    """
    群管理
    """

    def __init__(self,**kwargs):

        super(WeiboGroup,self).__init__(**kwargs)

        self.session.headers['Content-type']="application/x-www-form-urlencoded; charset=utf-8"
        self.session.headers['User-agent'] = "Weibo/39290 (iPhone; iOS 12.4.1; Scale/2.00)"
        self.params = {
            "gsid": self.sessionRes['gsid'],
            "sensors_mark": "0",
            "wm": "3333_2001",
            "sensors_is_first_day": "false",
            "from": "109B293010",
            "sensors_device_id": "7F2E6523-1726-4FB9-87E5-038B80BC8AC7",
            "c": "iphone",
            "v_p": "78",
            "skin": "default",
            "s": self.sessionRes['s'],
            "v_f": "1",
            "networktype": "wifi",
            "b": "0",
            "lang": "zh_CN",
            "ua": "iPhone11,8__weibo__9.11.2__iphone__os12.4.1",
            "sflag": "1",
            "ft": "0",
            "aid": "01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.",
            "launchid": "icon"
        }

    def create(self,name):
        """
        创建群组
        :param name:
            name : 群名称
        :return:
        """

        #创建群前先调用检查接口
        url = """https://api.weibo.cn/2/groupchat/check_valid"""

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

        rRes=self.session.post(url=url,data=data,params=self.params)
        res = json.loads(rRes.content.decode('utf-8'))
        if "errmsg" in res and res['errmsg']:
            raise Exception(res['errmsg'])

        # 创建群
        url="""https://api.weibo.cn/2/groupchat/create"""

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
        res = json.loads(self.session.post(url=url,data=data,params=self.params).content.decode('utf-8'))
        if "errmsg" in res and res['errmsg']:
            raise Exception(res['errmsg'])
        else:
            #务必保存群数据后续需要使用
            print(res)
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
        pass
        self.session.headers['Referer'] = 'https://www.weibo.com/u/{}?is_hot=1'.format(to)
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
            "refer_from":"profile_headerv6"
        }
        res = json.loads(self.session.post(url=url,data=data).content.decode("utf-8"))
        if res['code'] != "100000":
            raise Exception(res['msg'])

class WeiboPay(WeiboBase):

    def __init__(self,**kwargs):
        kwargs.setdefault("cookieKey", ".weibo.com")
        super(WeiboPay, self).__init__(**kwargs)

    def pay(self,price,amount,num,msgid):

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
        res = json.loads(rRes.content.decode("utf-8"))
        # print(res)
        if res['code'] != "100000":
            raise Exception(res['msg'])
        return res['data']['url'], res['data']['url'].split("out_pay_id=")[1].split('&')[0]

def get_timestamp():
    return int(time.time()*1000)
class WeiboHb(WeiboBase):

    """
    发红包
    """
    def __init__(self,**kwargs):
        kwargs.setdefault("cookieKey", ".weibo.cn")
        super(WeiboHb, self).__init__(**kwargs)

        self.sendlist=[]

    def listfilter(self,html,max_set_id):

        pattern = re.compile(r'<a.*recvdetailowner.*set_id=.*?>')
        result = [ {"url":item.replace('<a href="','').replace('">',''),"set_id":item.split('set_id=')[1].split('&')[0]} for item in pattern.findall(html) ]
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
            flag, res = s.getlist(year=year, type=type, page=page, max_set_id=max_set_id)
            for item in res:
                self.sendlist.append(item)
            if not flag:
                print("已经查完了")
                break
            page += 1
        return self.sendlist

    def send(self,data1,group_id):
        print("正在发红包{}".format(data1['url']))




        self.session.headers={
            "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)",
            "Accept":"*/*"
        }
        # self.reset_session(sessionRes=self.sessionRes, cookieKey='pccookie')
        print(data1['referer'])
        res = self.session.get(url=data1['referer'])

        print(res.text)
        st = res.text.split('"st"')[1].split(",")[0].replace(':','').replace('"',"")



        url = "https://m.weibo.cn/groupChat/userChat/sendMsg/"


        self.session.headers['Referer'] = data1['referer']

        rdata={
            "group_id":group_id,
            "luckybag_url":"https://mall.e.weibo.com/redenvelope/draw?set_id={}".format(data1['set_id']),
            "format":"cards",
            "st":st
        }
        res = json.loads(self.session.post(url=url,data=rdata).content.decode('utf-8'))
        if res['ok'] != 1:
            raise Exception(res['msg'])
        print("发送成功 {}".format(data1['set_id']))

    def sendAll(self,groups):


        for item in self.sendlist:
            self.session.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
            group_id = groups['group_id']
            print(item['url'])
            html = self.session.get(item['url']).text
            # print(html)

            pattern = re.compile(r'继续发此红包')
            res = pattern.findall(html)
            if len(res)>0:
                pattern = re.compile(r'<a.*http://m.weibo.cn/groupChat/userChat/groupListForLuckyBag?.*?class=')
                item['referer'] = pattern.findall(html)[0].replace('<a href="', '').split('"')[0]
                self.send(item,group_id)
            else:
                print("红包关闭!{}".format(item['url']))

class WeiboHbGet(WeiboBase):

    """
    抢红包
    """
    def __init__(self,**kwargs):
        kwargs.setdefault("cookieKey", "pccookie")
        super(WeiboHbGet, self).__init__(**kwargs)

    def rob(self,url):
        res = self.session.get(url=url)
        print(res.text)

if __name__ == '__main__':

    sessionRes={
        "uid":"6424853549",
        "gsid":"_2A25w6NaUDeRxGeBK6VYZ9S3JzzWIHXVRvG1crDV6PUJbkdAKLVGgkWpNR848UDtjlXSXHAUqSDQLtG4I24hy6dfZ",
        "s":"8e3487ea",
        "cookie":{
            '.weibo.cn':{
                "SCF": "AjOaGw1K_o2AsNr4Ql_tYHlJuCsZ0nyT_18ASL-aVaSo4IKl-q-jVEzH3hXqGCQgjQ..",
                "SUB": "_2A25w6AIaDeRhGeBK6VYZ9S3JzzWIHXVQYkhSrDV6PUJbitANLVjbkWtNR848UEgvOUx1GEo9LH5hsR4IKFLtbk5x",
                "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5NHD95QcShzX1h-0SKB4Ws4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSoBEShnfe0-X1Btt",
                "SUHB": "0u5RzAEo3ZR2O_"},
            ".weibo.com":{
                "SCF":"AjOaGw1K_o2AsNr4Ql_tYHk1EL7tHikNzSHfmJ3edScL2_if5LrjWd4CaPOqAXb6KQ..",
                "SUB":"_2A25w7k9VDeRhGeBK6VYZ9S3JzzWIHXVQYHsdrDV8PUJbitAKLUbSkWtNR848UCGmjYDPtAM9E5QNyr-KYzP2iLQ1",
                "SUBP":"0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5NHD95QcShzX1h-0SKB4Ws4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSoBEShnfe0-X1Btt",
                "SUHB":"0G0uBhJS7yv_0s"
            }
        }
    }

    # sessionRes={
    #     "uid":"5904854490",
    #     "gsid":"_2A25w7mdsDeRxGeNH61YZ9SrIwjyIHXVRuv2krDV6PUJbkdANLWekkWpNSvs4pXlbM9Y5nwrhIW9CMeSeI72q7Um8",
    #     "s":"8611d53b"
    # }

    groups={
        "group_id":"4446532289545356"
    }

    s=WeiboHb(sessionRes=sessionRes,cookieKey='.weibo.com')
    max_set_id = "0"
    s.getlistAll(year="2019",type="2",max_set_id=max_set_id)
    s.sendAll(groups)

    # s = WeiboGroup(sessionRes=sessionRes)
    #
    # s.create("test6右手枫叶")
    #
    # groupid="4446532289545356"
    # uids="5904854490,1222835533"
    # s.join(groupid=groupid,uids=uids)

    #4446532289545356