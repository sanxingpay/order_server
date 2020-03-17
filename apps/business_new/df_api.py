import time
import hashlib
import json
from requests import request as requestHandler

from django.db import transaction
from django.db import connection

from libs.utils.exceptions import PubErrorCustom
from libs.utils.log import logger
from libs.utils.mytime import UtilTime
from libs.utils.string_extension import hexStringTobytes

from apps.user.models import Users
from apps.order.models import CashoutList
from apps.lastpass.utils import LastPass_BAWANGKUAIJIE,LastPass_KUAIJIE,LastPass_GCPAYS
from apps.cache.utils import RedisCaCheHandler
from apps.account import AccountCashoutConfirmForApi,AccountCashoutConfirmForApiFee
from apps.pay.models import PayPassLinkType
from apps.utils import RedisHandler


class dfHandler(object):


    def __init__(self,data,ip=None,islock=False,isip=True):

        print(ip)


        self.data = data

        if islock:
            try:
                self.user = Users.objects.select_for_update().get(userid=self.data.get("businessid"))
            except Users.DoesNotExist:
                raise PubErrorCustom("无效的商户!")
        else:
            try:
                self.user = Users.objects.get(userid=self.data.get("businessid"))
            except Users.DoesNotExist:
                raise PubErrorCustom("无效的商户!")


        paypass = self.get_paypasslinktype()

        if not len(paypass):
            raise PubErrorCustom("通道暂未开放!")
        if len(paypass) > 1:
            raise PubErrorCustom("代付通道不允许设置多通道!")

        self.paypasslinktype = paypass[0]

        #T0提现 90%
        self.t0Tx = 0.8

        if isip:
            if ip not in ['47.75.120.33']:
                data =RedisCaCheHandler(
                    method="filter",
                    serialiers="WhiteListModelSerializerToRedis",
                    table="whitelist",
                    filter_value={
                        "userid" : self.user.userid
                    }
                ).run()

                if not len(data):
                    raise PubErrorCustom("拒绝访问!")

                isIpValid = False
                for item in data[0]['dfobj'].split(','):
                    if str(item)==str(ip):
                        isIpValid = True
                        break

                if not isIpValid:
                    raise PubErrorCustom("拒绝访问!")

    def get_paypasslinktype(self):
        paypass = PayPassLinkType.objects.raw(
            """
            SELECT t1.*,t2.typename ,t2.name as paytypename,t3.name as paypassname FROM paypasslinktype as t1 
            INNER JOIN paytype as t2 on t1.paytypeid = t2.paytypeid
            INNER JOIN paypass as t3 on t1.passid = t3.paypassid
            WHERE t1.to_id=%s and t1.type='1' and t3.status='0'
            """, [self.user.userid]
        )
        paypass = list(paypass)
        return paypass

    def get_ok_bal(self):


        if self.paypasslinktype.passid in ['51','54']:
            weeknum = UtilTime().get_week_day()

            if weeknum in [6,7]:
                ok_bal = float(self.user.today_pay_amount) * self.t0Tx - (float(self.user.today_cashout_amount) + float(self.user.today_fee_amount))
            else:
                ok_bal = float(self.user.lastday_bal) + (float(self.user.today_pay_amount) * self.t0Tx - (float(self.user.today_cashout_amount) + float(self.user.today_fee_amount)))

            print("用户ID{} 周几{} 昨日余额{} 当填充值金额{} 当天提现金额{} 当天手续费{}".format(self.user.userid, weeknum, self.user.lastday_bal,
                                                                self.user.today_pay_amount, self.user.today_cashout_amount,self.user.today_fee_amount ))
        else:
            ok_bal = self.user.bal

        return ok_bal

    def BalQuery(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not self.data.get("nonceStr"):
            raise PubErrorCustom("随机数!")


        md5params = "{}{}{}{}".format(
            self.user.google_token,
            str(self.data.get("businessid")),
            self.data.get("nonceStr"),
            self.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("代付查询待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("代付查询签名:{}-----{}".format(sign, self.data.get("sign")))
        if sign != self.data.get("sign"):
            raise PubErrorCustom("验签失败!")

        # user = AccountBase(userid=self.user.userid,amount=1).query()

        ok_bal = self.get_ok_bal()

        return {"data":{
            "bal" : round(float(self.user.bal),2),
            "stop_bal" : round(float(self.user.stop_bal),2),
            "ok_bal" : round(ok_bal,2)
        }}

    def BalQueryTest(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")

        # user = AccountBase(userid=self.user.userid,amount=1).query()

        ok_bal = self.get_ok_bal()

        return {"data":{
            "bal" : round(float(self.user.bal),2),
            "stop_bal" : round(float(self.user.stop_bal),2),
            "ok_bal" : round(ok_bal,2)
        }}

    def Query(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not self.data.get("down_ordercode"):
            raise PubErrorCustom("商户订单号为空!")
        if not self.data.get("nonceStr"):
            raise PubErrorCustom("随机数!")

        md5params = "{}{}{}{}{}".format(
            self.user.google_token,
            str(self.data.get("down_ordercode")),
            str(self.data.get("businessid")),
            self.data.get("nonceStr"),
            self.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("代付查询待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("代付查询签名:{}-----{}".format(sign, self.data.get("sign")))
        if sign != self.data.get("sign"):
            raise PubErrorCustom("验签失败!")

        request={}
        # request['dfordercode'] = "DF%08d%s" % (self.user.userid,self.data.get("down_ordercode"))
        request['dfordercode'] = self.data.get("down_ordercode")
        request['userid'] =  self.user.userid
        request["paypassid"] = self.paypasslinktype.passid

        return daifuOrderQuery(request)

    def check_params(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not self.data.get("down_ordercode"):
            raise PubErrorCustom("商户订单号为空!")
        if not self.data.get("nonceStr"):
            raise PubErrorCustom("随机数!")
        if not self.data.get("amount"):
            raise PubErrorCustom("金额不能为空!")

        if float(self.data.get("amount"))<=0 :
            raise PubErrorCustom("请输入正确的提现金额!")

        if not self.data.get("accountNo"):
            raise PubErrorCustom("银行卡号不能为空!")
        if not self.data.get("bankName"):
            raise PubErrorCustom("银行名称不能为空!")
        if not self.data.get("accountName"):
            raise PubErrorCustom("账户名称不能为空!")
        if not self.data.get("sign"):
            raise PubErrorCustom("签名不能为空!")

        md5params = "{}{}{}{}{}{}{}{}{}{}".format(
            self.user.google_token,
            str(self.data.get("down_ordercode")),
            str(self.data.get("businessid")),
            self.user.google_token,
            str(self.data.get("nonceStr")),
            str(self.data.get("amount")),
            str(self.data.get("accountNo")),
            str(self.data.get("bankName")),
            str(self.data.get("accountName")),
            self.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("代付待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("代付签名:{}-----{}".format(sign, self.data.get("sign")))
        if sign != self.data.get("sign"):
            raise PubErrorCustom("验签失败!")


    def handler(self):

        ok_bal = self.get_ok_bal()
        if float(ok_bal) - abs(float(self.user.cashout_bal)) - float(self.user.fee_rule) < float(self.data.get("amount")):
            raise PubErrorCustom("可提余额不足!")

        request=dict()

        request["paypassid"] = self.paypasslinktype.passid
        request["amount"] = float(self.data.get("amount"))
        request["bank_name"] = hexStringTobytes(self.data.get("bankName")).decode('utf-8')
        request["open_name"] = hexStringTobytes(self.data.get("accountName")).decode('utf-8')
        request["bank_card_number"] = self.data.get("accountNo")
        request["downordercode"] = self.data.get('down_ordercode')
        request["memo"] = self.data.get("memo")


        #单笔不允许超过50000
        if request["amount"] - 50000.0 > 0.0:
            raise PubErrorCustom("单笔下发不能超过50000,当前金额{}".format(request["amount"]))

        #3次内同一用户同一账户金额不能相同
        res = CashoutList.objects.filter(userid=self.user.userid,bank_card_number=request["bank_card_number"],df_status='1').order_by("-createtime")
        if res.count() > 3:
            res = res[:3]

        for item in res:
            if request["amount"] == float(item.amount):
                raise PubErrorCustom("3次内同一银行卡下发金额不能相同！")


        cashout_id = daifuBalTixian(request,self.user)

        ordercode = "DF%08d%s" % (self.user.userid, request["downordercode"])

        AccountCashoutConfirmForApiFee(user=self.user,ordercode=ordercode).run()
        AccountCashoutConfirmForApi(user=self.user, amount=request["amount"],ordercode=ordercode).run()

        # float(self.user.fee_rule)

        daifu = daifuCallBack()
        daifu.redis_client.lpush(daifu.lKey, "{}|{}|{}|{}|{}|{}".format(
            self.user.userid,
            request["amount"],
            request["downordercode"],
            request["paypassid"],
            cashout_id,
            UtilTime().today.replace(minutes=120).timestamp))
        return None

    def run(self):

        self.check_params()
        self.handler()


def is_connection_usable():
    try:
        connection.connection.ping()
    except:
        return False
    else:
        return True

class daifuCallBack(object):
    def __init__(self):

        self.lKey = "DAIFU_ORDERS"

        self.redis_client = RedisHandler(key=self.lKey,db="default").redis_client

    def run(self):
        while True:

            redisRes = self.redis_client.brpop(self.lKey)[1]
            # logger.info("{}{}".format(redisRes,UtilTime().timestamp))
            if not redisRes:
                continue

            userid = redisRes.decode('utf-8').split("|")[0]
            amount = redisRes.decode('utf-8').split("|")[1]
            ordercode = redisRes.decode('utf-8').split("|")[2]
            paypassid = redisRes.decode('utf-8').split("|")[3]
            cashout_id = redisRes.decode('utf-8').split("|")[4]
            endtime = redisRes.decode('utf-8').split("|")[5]

            if UtilTime().timestamp >= int(endtime):
                continue
            try:
                res = daifuOrderQuery(request={
                    "userid": userid,
                    "dfordercode": ordercode,
                    "paypassid": paypassid
                })

                if str(res.get("data").get("code")) == '0' :
                    self.redis_client.lpush(self.lKey,"{}|{}|{}|{}|{}|{}".format(userid,amount,ordercode,paypassid,cashout_id,endtime))
                    time.sleep(1)
                    continue
                elif str(res.get("data").get("code")) == '1' :
                    result = requestHandler(method="POST",url="http://allwin6666.com/api_new/business/DF_status_save",data={"id":cashout_id})
                    result = json.loads(result.content.decode('utf-8'))
                    if str(result['rescode']) != '10000':
                        logger.info(result['msg'])
                        self.redis_client.lpush(self.lKey,
                                                "{}|{}|{}|{}|{}|{}".format(userid, amount, ordercode, paypassid,
                                                                           cashout_id, endtime))
                        time.sleep(1)
                    continue
                else:
                    result = requestHandler(method="POST", url="http://allwin6666.com/api_new/business/DF_chongzheng",
                                            data={"row": redisRes})
                    result = json.loads(result.content.decode('utf-8'))
                    if str(result['rescode']) != '10000':
                        logger.info(result['msg'])
                        self.redis_client.lpush(self.lKey,
                                                "{}|{}|{}|{}|{}|{}".format(userid, amount, ordercode, paypassid,
                                                                           cashout_id, endtime))
                        time.sleep(1)
                    continue
            except Exception as e:
                logger.info("Exception")
                logger.info(str(e))
                self.redis_client.lpush(self.lKey,"{}|{}|{}|{}|{}|{}".format(userid,amount,ordercode,paypassid,cashout_id,endtime))
                time.sleep(1)
                continue

#代付订单查询
def daifuOrderQuery(request):

    obj = CashoutList.objects.filter(userid=request.get("userid"),downordercode=request.get("dfordercode"))

    if not obj.exists():
        raise PubErrorCustom("此订单不存在!")

    obj = obj[0]
    dfordercode = "DF%08d%s" % (int(request.get("userid")), str(request.get("dfordercode")))

    if str(request.get('paypassid')) == '54':
        res = LastPass_BAWANGKUAIJIE(data={
            "orderId" : dfordercode
        }).df_query()
        obj.textstatus = res
        obj.save()
        return {"data":{"msg":res}}

    elif str(request.get('paypassid')) == '51':
        res=LastPass_KUAIJIE(data={
            "tradeCustorder" : dfordercode
        }).df_order_query()
        obj.textstatus = res
        obj.save()
        return {"data":{"msg":res}}
    elif str(request.get('paypassid')) == '69':
        res=LastPass_GCPAYS().df_order_query(data={
            "orderNo" : dfordercode
        })
        # obj.textstatus = res[1]
        # obj.save()
        return {"data":{"code":res[0],"msg":res[1]}}
    else:
        raise PubErrorCustom("代付渠道有误!")

#代付提现
def daifuBalTixian(request,user):

    if str(request.get('paypassid')) == '54':

        cashlist = CashoutList.objects.create(**{
            "userid": user.userid,
            "name": user.name,
            "amount": request.get("amount"),
            "bank_name": request.get('bank_name'),
            "open_name": request.get('open_name'),
            "bank_card_number": request.get('bank_card_number'),
            "status": "0",
            "downordercode"  : request['downordercode'],
            "memo" : request['memo']
        })

        res = LastPass_BAWANGKUAIJIE(data={
            "orderId": "DF%08d%s" % (cashlist.userid, cashlist.downordercode),
            "txnAmt" : str(int(float(cashlist.amount)*100.0)),
            "accountNo" : cashlist.bank_card_number,
            "bankName" :cashlist.bank_name,
            "accountName" : cashlist.open_name
        }).df_bal_handler()

        cashlist.status='1'
        cashlist.paypassid = '54'
        cashlist.tranid = res['REP_BODY']['tranId']
        cashlist.save()

        return cashlist.id
    elif str(request.get('paypassid')) == '51':

        cashlist = CashoutList.objects.create(**{
            "userid": user.userid,
            "name": user.name,
            "amount": request.get("amount"),
            "bank_name": request.get('bank_name'),
            "open_name": request.get('open_name'),
            "bank_card_number": request.get('bank_card_number'),
            "status": "0",
            "downordercode": request['downordercode'],
            "memo": request['memo']
        })

        res = LastPass_KUAIJIE().df_api(data={
            "orderId": "DF%08d%s" % (cashlist.userid, cashlist.downordercode),
            "txnAmt": "%.2lf"%float(cashlist.amount),
            "accountNo": cashlist.bank_card_number,
            "bankName": cashlist.bank_name,
            "accountName": cashlist.open_name
        })

        cashlist.status = '1'
        cashlist.paypassid = '51'
        cashlist.tranid = cashlist.downordercode
        cashlist.save()

        return None
    elif str(request.get('paypassid')) == '69':

        cashlist = CashoutList.objects.create(**{
            "userid": user.userid,
            "name": user.name,
            "amount": request.get("amount"),
            "bank_name": request.get('bank_name'),
            "open_name": request.get('open_name'),
            "bank_card_number": request.get('bank_card_number'),
            "status": "0",
            "downordercode": request['downordercode'],
            "memo": request['memo']
        })

        res = LastPass_GCPAYS().df_api(data={
            "orderNo": "DF%08d%s" % (cashlist.userid, cashlist.downordercode),
            "bankNo": cashlist.bank_card_number,
            "timestap" : str(cashlist.createtime),
            "realName": cashlist.open_name,
            "branchBankName" : cashlist.open_bank,
            "money": int(float(cashlist.amount)*100.0),
            "bankName": cashlist.bank_name
        })

        cashlist.status = '1'
        cashlist.paypassid = '69'
        cashlist.tranid = cashlist.downordercode
        cashlist.save()

        return cashlist.id
    else:
        raise PubErrorCustom("代付渠道有误!")