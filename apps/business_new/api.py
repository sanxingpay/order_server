from apps.utils import GenericViewSetCustom
from rest_framework.decorators import list_route

from libs.core.decorator.response_new import Core_connector
from libs.core.decorator.response_new1 import Core_connector_Response_Html
from libs.core.decorator.response_daifu import Core_connector_DAIFU
from libs.core.decorator.response_neichong import Core_connector_NEICHONG

from apps.business.utils import CreateOrder
from apps.business_new.df_api import dfHandler
from apps.business_new.jd_api import jdHandler
from apps.lastpass.utils import LastPass_GCPAYS
from django.shortcuts import render
from django.http import HttpResponse
import json
from apps.utils import RedisOrderCreate
from libs.utils.exceptions import PubErrorCustom
from libs.utils.mytime import UtilTime

from apps.order.models import CashoutList
from apps.user.models import Users
from apps.pay.models import WeiboPayUsername
from apps.account import AccounRollBackForApiFee,AccountRollBackForApi


class BusinessNewAPIView(GenericViewSetCustom):

    @list_route(methods=['POST'])
    @Core_connector()
    def create_order(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        return {"data":CreateOrder(user=request.user, request_param=data, lock="1").run()}

    @list_route(methods=['GET'])
    @Core_connector_Response_Html()
    def DownOrder(self,request):

        html = RedisOrderCreate().redis_get(request.query_params.get("o"))
        print(html)
        if not html:
            raise PubErrorCustom("此订单已过期!")
        else:
            return HttpResponse(html, content_type='text/html')


    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def getWeiboUserInfo(self,request):

        data=[]
        u = WeiboPayUsername.objects.filter(status='0')
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

        print(request.data)
        if not request.data.get("datas"):
            raise PubErrorCustom("无会话数据!")

        for item in request.data.get("datas"):
            try:
                s = WeiboPayUsername.objects.get(id=item['id'])
            except WeiboPayUsername.DoesNotExist:
                raise PubErrorCustom("无此账户信息!{}".format(item['id']))

            if not len(s.session):
                s.session = {}
                s.session['uid'] = item['uid']
                s.session['cookie']={}
                s.session['cookie']['pccookie'] = item['session']

            else:
                s.session = json.loads(s.session)
                if not len(s.session['cookie']):
                    s.session['cookie']={}
                s.session['cookie']['pccookie'] = item['session']
            s.logintime = UtilTime().timestamp
            s.session = json.dumps(s.session)
            s.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def df(self,request):

        dfHandler(request.data,request.META.get("HTTP_X_REAL_IP"),True).run()
        return None

    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def dfQuery(self,request):

        return dfHandler(request.data,request.META.get("HTTP_X_REAL_IP")).Query()

    @list_route(methods=['GET'])
    @Core_connector_DAIFU()
    def dfQueryTest(self,request):

        return dfHandler(request.query_params,request.META.get("HTTP_X_REAL_IP"),isip=False).BalQueryTest()

    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def BalQuery(self,request):

        return dfHandler(request.data,request.META.get("HTTP_X_REAL_IP")).BalQuery()


    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def JdOrderQuery(self,request):

        return jdHandler(request.data).OrderQuery()

    # @list_route(methods=['GET'])
    # @Core_connector_DAIFU(transaction=True)
    # def DF_duizhang(self,request):
    #
    #     for item in CashoutList.objects.filter(paypassid=69):
    #         res = daifuOrderQuery(request={
    #             "userid": item.userid,
    #             "dfordercode": item.downordercode,
    #             "paypassid": item.paypassid
    #         })
    #
    #         item.df_status = res.get("data").get("code")
    #         item.save()
    #
    #     return None


    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def DF_status_save(self,request):
        try:
            obj = CashoutList.objects.get(id=request.data.get("id"))
            obj.df_status = '1'
            obj.save()
        except CashoutList.DoesNotExist:
            raise PubErrorCustom("无此提现明细!{}".format(request.data.get("id")))
        return None

    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def DF_chongzheng(self,request):

        redisRes=request.data.get("row")
        userid = redisRes.split("|")[0]
        amount = redisRes.split("|")[1]
        ordercode = redisRes.split("|")[2]
        cashout_id = redisRes.split("|")[4]

        try:
            obj = CashoutList.objects.get(id=cashout_id)
            obj.df_status = '2'
            obj.save()
        except CashoutList.DoesNotExist:
            raise PubErrorCustom("无此提现明细!{}".format(cashout_id))

        ordercodetmp = "DF%08d%s" % (int(userid), str(ordercode))

        try:
            user = Users.objects.select_for_update().get(userid=userid)
        except Users.DoesNotExist:
            raise PubErrorCustom("无此用户信息")
        AccounRollBackForApiFee(user=user,ordercode=ordercodetmp).run()
        AccountRollBackForApi(user=user, amount=float(amount),ordercode=ordercodetmp).run()

        return None


    @list_route(methods=['POST'])
    @Core_connector_NEICHONG(transaction=True)
    def CardPays(self,request):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        return LastPass_GCPAYS(data=data).run(request)