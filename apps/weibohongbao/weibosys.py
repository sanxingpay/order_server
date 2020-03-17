
import random,json,time

from django.db import transaction


from libs.utils.mytime import UtilTime
from libs.utils.log import logger
from libs.utils.exceptions import PubErrorCustom

from apps.weibohongbao.weibo import WeiboPay,WeiBoLoginForPhone,WeiboGroup,WeiboFollow,WeiboHb,WeiboHbGet,WeiboLoginForPc
from apps.weibohongbao.models import WeiboUser,WeiboSendList,WeiboGroupMember,WeiboGroup as WeiboGroupModel,WeiboTask

class weiboSysRun(object):

    def __init__(self,isQueryTask=True):

        self.ut = UtilTime()

        self.wbOUser = None
        self.wbOTask = None

        if isQueryTask:
            wbOTasks = WeiboTask.objects.filter(umark='0',status='1',date=self.ut.arrow_to_string(format_v="YYYY-MM-DD")).order_by('sort')
            if not wbOTasks.exists():
                logger.error("无任务可执行!")
                return

            self.wbOTask = wbOTasks[0]

            try:
                self.wbOUser = WeiboUser.objects.get(uid=self.wbOTask.uid,status='0')
            except WeiboUser.DoesNotExist:
                logger.error("无可用组长!")
                return

            self.robnumber = self.wbOTask.robnumber
            self.minamount = self.wbOTask.minamount
            self.maxamount = self.wbOTask.maxamount

    def pay(self,order):
        """
        生成微博支付订单
        :param order:  订单表
        :return:
        """
        amount = float(order.amount)

        if not(self.minamount <= amount <= self.maxamount):
            raise PubErrorCustom("金额范围在 {}-{}".format(self.minamount,self.maxamount))

        #计算单价
        price = amount / self.robnumber

        print(price)
        if round(price,2) * self.robnumber !=amount:
            raise PubErrorCustom("该金额不正确")

        print("单价:{},总价{},红包个数{}".format(price,amount,self.robnumber))
        wbPayClass = WeiboPay(sessionRes=json.loads(self.wbOUser.session))

        url,ordercode, = wbPayClass.pay(price=price,num=self.robnumber,amount=amount)
        wapurl,payordercode = wbPayClass.getPayId(url)
        html = wbPayClass.createorder(wapurl)

        order.isjd = '0'
        order.jd_ordercode = ordercode
        order.jd_payordercode = payordercode
        order.jd_data = json.dumps({
            "payurl": url,
            "userid": self.wbOUser.userid, #码商ID
            "status": "0",  # 0-待支付,1-已支付,未发红包,2-已发红包,3-红包被抢
            "num": self.robnumber,  # 红包个数
            "ok_num": 0,  # 已抢个数
            "run_username": [],  # 抢红包的人的集合
        })
        order.save()
        self.payafter(order,self.wbOUser.session)
        return html

    def payafter(self,order,session):
        from apps.weibohongbao.weiboCallback import callback
        """
        微博订单回调通知
        :param ordercode:系统订单号
        :return:
        """
        weiboHandler = callback()
        weiboHandler.redis_client.lpush(weiboHandler.lKey, "{}|allwin|{}|allwin|{}|allwin|{}".format(
            order.ordercode,
            order.jd_payordercode,
            session,
            UtilTime().today.replace(minutes=120).timestamp))

    def getvercode(self,username):
        """
        获取手机验证码(目前手机登录用)
        :param username:
        :return:
        """
        wbLoginClass = WeiBoLoginForPhone()
        wbLoginClass.getvercode(username)

    def phonelogin(self,username,vercode):
        """
        :param username: 登录手机号
        :param vercode: 验证码
        :return:
        """
        try:
            wbUserObj = WeiboUser.objects.get(username=username)
        except WeiboUser.DoesNotExist:
            raise PubErrorCustom("账号不存在!")

        wbLoginClass = WeiBoLoginForPhone()
        wbUserObj.session = wbLoginClass.login_by_vercode(username,vercode)
        wbUserObj.uid = wbUserObj.session['uid']
        wbUserObj.session = json.dumps(wbUserObj.session)
        wbUserObj.logintime = UtilTime().timestamp
        wbUserObj.session_status = '0'
        wbUserObj.save()


    def pclogin(self,datas):

        rdatas=[]
        for item in datas:
            try:
                wbUserObj = WeiboUser.objects.get(username=item['username'])
            except WeiboUser.DoesNotExist:
                rdatas.append({
                    "username":wbUserObj.username,
                    "code":"10001",
                    "msg":"账号不存在系统登录失败!"
                })
                continue
            wbLFPClass = WeiboLoginForPc(username=wbUserObj.username,password=wbUserObj.password)
            if 'params' in item and item['params']['showpin'] == '1':
                wbLFPClass.login_params = item['params']
                wbLFPClass.login_params['vercode'] = item['vercode']
                try:
                    if wbUserObj.session:
                        session = json.loads(wbUserObj.session)
                    else:
                        session = {}
                        session['cookie'] = {}
                    res = wbLFPClass.login()
                    print(res)
                    session['uid'] = res['uid']
                    session['cookie']['pccookie'] = res['cookie']['pccookie']

                    wbUserObj.session = json.dumps(session)
                    wbUserObj.uid = session['uid']
                    wbUserObj.logintime = UtilTime().timestamp
                    wbUserObj.save()
                except Exception as e:
                    logger.error(str(e))
                    rdatas.append({
                        "username": wbUserObj.username,
                        "code": "10002",
                        "msg": "密码或验证码错误,请重新输入!",
                        "url": wbLFPClass.getvercodeUrl(),
                        "params" : wbLFPClass.login_params
                    })
                    continue
            else:
                wbLFPClass.preLogin()
                if wbLFPClass.login_params['showpin'] == '1':
                    rdatas.append({
                        "username": wbUserObj.username,
                        "code": "10002",
                        "msg": "需要获取验证码登录!",
                        "url": wbLFPClass.getvercodeUrl(),
                        "params" : wbLFPClass.login_params
                    })
                    continue
                else:
                    try:
                        if wbUserObj.session:
                            session = json.loads(wbUserObj.session)
                        else:
                            session = {}
                            session['cookie'] = {}
                        res = wbLFPClass.login()
                        print(res)
                        session['uid'] = res['uid']
                        session['cookie']['pccookie'] = res['cookie']['pccookie']

                        wbUserObj.session = json.dumps(session)
                        wbUserObj.uid = session['uid']
                        wbUserObj.logintime = UtilTime().timestamp
                        wbUserObj.save()
                    except Exception as e:
                        logger.error(str(e))
                        rdatas.append({
                            "username":wbUserObj.username,
                            "code": "10001",
                            "msg":"账号或密码错误!"
                        })
                        continue
        print(rdatas)
        return rdatas


    def groupjoin(self,uid,uids,name,userid):

        """
        创建群并添加成员
        :param uid: 群组长uid
        :param uids: 群成员uid
        :param name: 群名称
        :return:
        """


        try:
            userBossObj = WeiboUser.objects.get(uid=uid)
        except WeiboUser.DoesNotExist:
            raise PubErrorCustom("群组长ID不正确{}".format(uid))

        userMemberObjs = []

        for item in uids.split(","):
            try:
                userMemberObjs.append(WeiboUser.objects.get(uid=item))
            except WeiboUser.DoesNotExist:
                raise PubErrorCustom("群成员ID不正确{}".format(item))

        #群组长关联各个群成员
        print(userBossObj.session)
        followClass = WeiboFollow(sessionRes=json.loads(userBossObj.session))
        for item in userMemberObjs:
            followClass.follow(item.uid)

        #群成员关注群组长
        for item in userMemberObjs:
            WeiboFollow(sessionRes=json.loads(item.session)).follow(userBossObj.uid)

        #添加群
        wbGroupClass = WeiboGroup(sessionRes=json.loads(userBossObj.session))
        res = wbGroupClass.create(name=name)

        WeiboGroupModel.objects.create(**{
            "group_id" : res['id'],
            "name": name,
            "userid":userid,
            "uid":uid
        })

        #添加成员
        wbGroupClass.join(groupid=res['id'],uids=uids)

        for item in uids.split(","):
            WeiboGroupMember.objects.create(**{
                "group_id": res['id'],
                "name" : name,
                "userid":userid,
                "uid" : uid,
                'son_uid':item
            })

    def gethb(self):
        time.sleep(2)

        if self.wbOUser and self.wbOTask:
            pass
        else:
            print("无可用用户或可用任务")
            return

        wbHbClass = WeiboHb(sessionRes=json.loads(self.wbOUser.session))
        wbSLObj = WeiboSendList.objects.filter().order_by('-setid')
        if not wbSLObj.exists():
            max_set_id = 0
        else:
            max_set_id = wbSLObj[0].setid

        try:
            sendlist = wbHbClass.getlistAll(year="2019", type="2", max_set_id=max_set_id)
            with transaction.atomic():
                for item in sendlist:
                    WeiboSendList.objects.create(**{
                        "groupid":self.wbOTask.groupid,
                        "setid":item['set_id'],
                        "uid":self.wbOUser.uid,
                        "uids":json.dumps({"uids":[]}),
                        "swithurl":item['url'],
                        "taskid":self.wbOTask.taskid,
                        "userid":self.wbOTask.userid,
                        "amount":item['amount'],
                        "getcount":item['getcount'],
                        "sendcount":item['sendcount'],
                        "status": '0' if item['getcount'] == item['sendcount'] else '1'
                    })
        except Exception as e:
            logger.error(str(e))
            self.gethb()

    def send(self):
        """
        发红包
        :return:
        """

        time.sleep(3)

        if self.wbOUser and self.wbOTask:
            pass
        else:
            return


        wbHbClass = WeiboHb(sessionRes=json.loads(self.wbOUser.session))
        wbSLObj = WeiboSendList.objects.filter(status='1',umark='1').order_by('setid')
        if not wbSLObj.exists():
            return

        for item in wbSLObj:
            try:
                with transaction.atomic():
                    wbHbClass.send(item)
                    item.umark='0'
                    item.save()
            except Exception as e:
                logger.error(str(e))


    def rob(self):

        time.sleep(5)

        if self.wbOUser and self.wbOTask:
            pass
        else:
            return

        WbSLObj = WeiboSendList.objects.filter(status=1,taskid=self.wbOTask.taskid)

        if WbSLObj.exists():
            for item in WbSLObj:
                uidsObj=json.loads(item.uids)
                print(uidsObj)
                print(item.groupid)
                for item_member in WeiboGroupMember.objects.filter(group_id=item.groupid):

                    if len(item.uids) and item_member.son_uid in uidsObj['uids']:
                        continue

                    time.sleep(20)

                    wbUserObj = WeiboUser.objects.get(uid=item_member.son_uid)
                    try:
                        print(item_member.son_uid)
                        rFlag = WeiboHbGet(sessionRes=json.loads(wbUserObj.session)).rob(url=item.url)
                        if rFlag:
                            uidsObj['uids'].append(item_member.son_uid)
                            item.getcount +=1
                    except Exception as e:
                        logger.error("抢红包失败",str(e),item_member.son_uid,item.url)

                if item.getcount>=item.sendcount:
                    item.status = '0'

                print(uidsObj)
                item.uids = json.dumps(uidsObj)
                item.save()





        # wbSLObj = WeiboSendList.objects.filter(taskid=self.wbOTask.taskid)
        # rate=0.0
        # if wbSLObj.exists():
        #     amount = 0.0
        #     for item in wbSLObj:
        #         price = float(item.amount) / item.sendcount
        #         amount += price * float(item.getcount)
        #     rate = amount * 100.0 / (float(self.wbOTask.amountwhat) * float(self.wbOTask.robnumber))
        # self.wbOTask.progree = rate
        # self.wbOTask.save()



