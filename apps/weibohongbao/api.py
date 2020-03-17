import json
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from libs.core.decorator.response_daifu import Core_connector_DAIFU

from auth.authentication import Authentication

from libs.utils.mytime import UtilTime

from libs.utils.exceptions import PubErrorCustom
from libs.utils.mytime import send_toTimestamp
from apps.weibohongbao.models import WeiboUser,WeiboParams
from apps.weibohongbao.weibosys import weiboSysRun

from apps.user.models import Users


class WeiBoAPIView(viewsets.ViewSet):

    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def getVerCodeForWeibo(self, request, *args, **kwargs):
        try:
            wbUobj = WeiboUser.objects.get(id=request.data['id'])
        except WeiboUser.DoesNotExist:
            raise PubErrorCustom("无此账号信息!")
        if wbUobj.type!='0':
            raise PubErrorCustom("只有发送红包的账号可以验证码登录!")

        weiboSysRun().getvercode(username=wbUobj.username)


    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def pcPreLogin(self, request, *args, **kwargs):
        try:
            wbUobj = WeiboUser.objects.get(id=request.data['id'])
        except WeiboUser.DoesNotExist:
            raise PubErrorCustom("无此账号信息!")
        if wbUobj.type!='0':
            raise PubErrorCustom("只有发送红包的账号可以验证码登录!")

        weiboSysRun().getvercode(username=wbUobj.username)


    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def vercodeLoginForWeibo(self, request, *args, **kwargs):
        if not request.data.get("vercode",None):
            raise PubErrorCustom("验证码不能为空!")

        try:
            wbUobj = WeiboUser.objects.get(id=request.data['id'])
        except WeiboUser.DoesNotExist:
            raise PubErrorCustom("无此账号信息!")
        if wbUobj.type!='0':
            raise PubErrorCustom("只有发送红包的账号可以验证码登录!")

        weiboSysRun(isQueryTask=False).phonelogin(username=wbUobj.username,vercode=request.data.get("vercode",None))

    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def loginForPc(self, request, *args, **kwargs):

        return {"data":weiboSysRun(isQueryTask=False).pclogin(datas=request.data['datas'])}


    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def checkToken(self,request):

        try:
            Users.objects.get(google_token=request.data['token'].strip())
        except Users.DoesNotExist:
            raise PubErrorCustom("token不存在!")

        return None

    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def getWeiboUserInfo(self,request):

        try:
            user = Users.objects.get(google_token=request.data['token'].strip())
        except Users.DoesNotExist:
            raise PubErrorCustom("token不存在!")

        data=[]
        u = WeiboUser.objects.filter(status='0',userid=user.userid)
        if u.exists():
            for item in u:
                data.append({
                    "id" : item.id,
                    "username":item.username,
                    "password":item.password
                })

        return {"data":data}

    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def setWeiboUserinfo(self,request):

        try:
            Users.objects.get(google_token=request.data['token'].strip())
        except Users.DoesNotExist:
            raise PubErrorCustom("token不存在!")

        if not request.data.get("datas"):
            raise PubErrorCustom("无会话数据!")

        for item in request.data.get("datas"):
            try:
                s = WeiboUser.objects.get(id=item['id'])
            except WeiboUser.DoesNotExist:
                raise PubErrorCustom("无此账户信息!{}".format(item['id']))

            if not len(s.session):
                s.session = {}
                s.uid = item['uid']
                s.session_status='0'
                s.session['uid'] = item['uid']
                s.session['cookie']={}
                s.session['cookie']['pccookie'] = item['session']
            else:
                s.session = json.loads(s.session)
                if not len(s.session['cookie']):
                    s.session['cookie']={}
                s.session['cookie']['pccookie'] = item['session']
                s.session_status = '0'
            s.logintime = UtilTime().timestamp
            s.session = json.dumps(s.session)
            s.save()

        return None


    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def addGroup(self, request, *args, **kwargs):

        uid = request.data['uid']
        userid = request.data['userid']
        print("uid:{} userid:{}".format(uid,userid))
        wParams = WeiboParams.objects.get(id=1)
        name = wParams.nameid

        wbUobj = WeiboUser.objects.filter(userid=userid,status='0',type='1')

        if not wbUobj.exists():
            raise PubErrorCustom("无合法的抢红包账号!")

        uids=""
        for item in wbUobj:
            uids += "{},".format(item.uid)
        uids=uids[:-1]
        print(uids)

        wbClass = weiboSysRun()

        wbClass.groupjoin(uid=uid,uids=uids,name=name,userid=userid)

        wParams.nameid +=1
        wParams.save()
