
from requests import request
import time,urllib,json
# from apps.business.weibo import WeiboCallBack,WeiboHbPay
from apps.weibohongbao.weibo import WeiboPay
from apps.weibohongbao.weibosys import weiboSysRun
from apps.utils import RedisHandler,url_join
from libs.utils.mytime import UtilTime
from libs.utils.log import logger
from apps.order.models import Order

class callback(object):

    def __init__(self):
        self.lKey = "WEIBOHONGBAO_ORDERS"
        self.redis_client = RedisHandler(key=self.lKey,db="default").redis_client

    def run(self):
        print("红包回调处理开启!")
        while True:
            redisRes = self.redis_client.brpop(self.lKey)[1]
            if not redisRes:
                continue

            self.ordercode = redisRes.decode('utf-8').split("|allwin|")[0]
            self.other_ordercode = redisRes.decode('utf-8').split("|allwin|")[1]
            self.session = redisRes.decode('utf-8').split("|allwin|")[2]
            self.endtime = redisRes.decode('utf-8').split("|allwin|")[3]
            print(self.other_ordercode)
            # print(UtilTime().timestamp)
            # print(int(self.endtime))
            # print(self.session)
            if UtilTime().timestamp >= int(self.endtime):
                continue
            try:
                ut = UtilTime()
                end_time = ut.arrow_to_string(format_v="YYYY-MM-DD")
                start_time = ut.arrow_to_string(ut.today.shift(days=-3),format_v="YYYY-MM-DD")
                # print(json.loads(self.session))
                wbPayClass = WeiboPay(sessionRes=json.loads(self.session))
                """
                cookieKey='pccookie'
                """
                flag,s= wbPayClass.queryOrderForWeibo(ordercode=self.other_ordercode,start_time=start_time,end_time=end_time)
                print(s)
                if not flag:
                    self.redisdataCall("查询失败!{}".format(s))
                    continue
                else:
                    if not len(s):
                        self.redisdataCall("查询无数据!{}".format(s))
                        continue
                    else:
                        if s[0]['status'] == '2':
                            print("成功")
                            pass
                        elif s[0]['status'] == '4':
                            self.redisdataCall("交易关闭!{}".format(s))
                            continue
                        elif s[0]['status'] == '1':
                            print("待完成状态")
                            self.redisdataCall()
                            continue
                        else:
                            self.redisdataCall("未知状态!{}".format(s))
                            continue

                request_data = {"orderid": self.ordercode}
                result = request('POST', url=urllib.parse.unquote(
                    '{}/callback_api/lastpass/jingdong_callback'.format(url_join())), data=request_data,json=request_data, verify=False)
                if result.text != 'success':
                    print("请求对方服务器错误! {}".format(self.ordercode))
            except Exception as e:
                self.redisdataCall(str(e))
                continue

    def redisdataCall(self,error=None):
        if error:
            logger.info(error)
        self.redis_client.lpush(self.lKey, "{}|allwin|{}|allwin|{}|allwin|{}".format(self.ordercode, self.other_ordercode,self.session,self.endtime))
        time.sleep(1)

class callbackGetOrdercode(object):

    def __init__(self):
        self.lKey = "WEIBOHONGBAO_GETORDERS"
        self.redis_client = RedisHandler(key=self.lKey,db="default").redis_client

    def run(self):
        print("红包订单同步开始!")
        while True:
            redisRes = self.redis_client.brpop(self.lKey)[1]
            if not redisRes:
                continue

            self.ordercode = redisRes.decode('utf-8').split("|allwin|")[0]
            self.session = redisRes.decode('utf-8').split("|allwin|")[1]
            self.endtime = redisRes.decode('utf-8').split("|allwin|")[2]

            if UtilTime().timestamp >= int(self.endtime):
                continue
            try:
                orderObj = Order.objects.get(ordercode=self.ordercode)

                wbPayClass =WeiboPay(sessionRes=json.loads(self.session))
                payordercode = wbPayClass.getPayId(json.loads(orderObj.jd_data)['payurl'])

                orderObj.jd_payordercode = payordercode
                orderObj.save()

                weiboHandler = callback()
                weiboHandler.redis_client.lpush(weiboHandler.lKey, "{}|allwin|{}|allwin|{}|allwin|{}".format(
                    orderObj.ordercode,
                    orderObj.jd_payordercode,
                    self.session,
                    UtilTime().today.replace(minutes=120).timestamp))

            except Exception as e:
                self.redisdataCall(str(e))
                continue

    def redisdataCall(self,error=None):
        if error:
            logger.info(error)
        self.redis_client.lpush(self.lKey, "{}|allwin|{}|allwin|{}".format(self.ordercode,self.session,self.endtime))
        time.sleep(1)


class callbackGetHbList(object):
    """
    获取红包列表
    """

    def __init__(self):
        # self.lKey = "WEIBOHONGBAO_SEND"
        # self.redis_client = RedisHandler(key=self.lKey,db="default").redis_client
        pass

    def run(self):
        print("获取红包列表开始!")
        while True:
            weiboSysRun().gethb()

class callbackSendHb(object):
    """
    发送红包
    """

    def __init__(self):
        # self.lKey = "WEIBOHONGBAO_SEND"
        # self.redis_client = RedisHandler(key=self.lKey,db="default").redis_client
        pass

    def run(self):
        print("发送红包开始!")
        while True:
            weiboSysRun().send()


class callbackRobHb(object):
    """
    抢红包
    """

    def __init__(self):
        # self.lKey = "WEIBOHONGBAO_SEND"
        # self.redis_client = RedisHandler(key=self.lKey,db="default").redis_client
        pass

    def run(self):
        print("抢红包开始!")
        while True:
            weiboSysRun().rob()