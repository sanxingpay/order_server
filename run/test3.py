

import requests
import base64
import rsa
import json
import binascii
import re


class WeboHongbaoBase(object):

    def __init__(self,**kwargs):
        self.obj=dict(
            username = kwargs.get("username",None),
            password = kwargs.get("password", None))

        self.inithandler()

    def inithandler(self):

        self.obj['WBCLIENT'] = 'ssologin.js(v1.4.18)'

        self.obj['session'] = requests.session()
        self.obj['session'].headers['User-Agent'] = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)"

    def encrypt_passwd(self, pubkey, servertime, nonce):  # rsa加密密码
        key = rsa.PublicKey(int(pubkey, 16),
                            int('10001', 16))  # int('10001', 16) 并非要转换成16进制，而是说10001是16 进制的数，int函数要将其转化为十进制
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.obj['password'])
        password = rsa.encrypt(message.encode('utf-8'), key)
        a= binascii.b2a_hex(password)
        return a

    def login(self):
        print("登录账号：{},登录密码：{}".format(self.obj['username'],self.obj['password']))
        resp = self.obj['session'].get(
            'http://login.sina.com.cn/sso/prelogin.php?'
            'entry=weibo&callback=sinaSSOController.preloginCallBack&'
            'su=%s&rsakt=mod&checkpin=1&client=%s' %
            (base64.b64encode(self.obj['username'].encode('utf-8')), self.obj['WBCLIENT'])
        )
        pre_login_str = re.match(r'[^{]+({.+?})', resp.text).group(1)
        pre_login = json.loads(pre_login_str)

        data = {
            'entry': 'weibo',
            'gateway': 1,
            'from': '',
            'savestate': 7,
            'userticket': 1,
            'ssosimplelogin': 1,
            'su': base64.b64encode(requests.utils.quote(self.obj['username']).encode('utf-8')),
            'service': 'miniblog',
            'servertime': pre_login['servertime'],
            'nonce': pre_login['nonce'],
            'vsnf': 1,
            'vsnval': '',
            'pwencode': 'rsa2',
            'sp': self.encrypt_passwd( pre_login['pubkey'],
                                 pre_login['servertime'], pre_login['nonce']),
            'rsakv': pre_login['rsakv'],
            'encoding': 'UTF-8',
            'prelt': '53',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.si'
                   'naSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }

        resp = self.obj['session'].post(
            'http://login.sina.com.cn/sso/login.php?client=%s' % self.obj['WBCLIENT'],
            data=data
        )
        login_url = re.search('replace\\(\'([^\']+)\'\\)', resp.text).group(1)  # 正则表达式匹配(需要前面加\\

        resp = self.obj['session'].get(login_url)
        login_str = re.search('\((\{.*\})\)', resp.text).group(1)

        self.obj['login_info'] = json.loads(login_str)
        print("登录成功：{}".format(self.obj['login_info']))
        #
        # uniqueid = login_info["userinfo"]["uniqueid"]
        # return (session, uniqueid)

    def request_hongbao_weibo(self):

        data={
            "uid" : self.obj['login_info']["userinfo"]["uniqueid"],
            "groupid" : 1000303,
            # "eid" : 0,
            # "amount" : 600,
            # "num" : 3,
            # "share" : 0,
            # "_type" : 1,
            # "isavg" : 0,
            # "tab" : 2,
            # "pass" : "allwin",
            # "passtip" : ""
        }

        self.obj['session'].headers['Origin'] = "https://hongbao.weibo.cn"
        self.obj['session'].headers['Referer'] = "https://hongbao.weibo.cn/h5/pay?groupid=1000303&ouid=6424853549"
        resp = self.obj['session'].post(
            'https://hongbao.weibo.cn/aj_h5/createorder?st=0cfa67&current_id=6424853549&_rnd=1575302901348',
            data=data
        )
        print(resp.text)


    def run(self):
        self.login()
        # self.request_hongbao_weibo()

if __name__ == '__main__':
    WeboHongbaoBase(username="17623069111",password="!@#tc123").run()