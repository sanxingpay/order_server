
import json
from apps.business.weibo import WeiboHbHandler
from apps.pay.models import WeiBoHbList,WeiboPayUsername



class HbHandler(object):

    def __init__(self,session):
        self.hbC = WeiboHbHandler(sessionRes=json.loads(session),cookieKey='pccookie',isSession=True)

    def getHblist(self,page):
        return self.hbC.Hblist(page=page)

class HbExHandler:

    def __init__(self):
        pass

    def getRunWbUser(self):
        wPobj = WeiboPayUsername.objects.filter(type='0')
        if not wPobj.exists():
            return False

        for item in wPobj:

            if not item.uid or not len(item.uid):
                continue

            wObj = WeiBoHbList.objects.filter(uid=item.uid).order_by('-ctime')
            if not wObj.exists():
                ctime = "2019-12-01 00:00:01"
            else:
                ctime = wObj[0].ctime