

from apps.order.models import Order
from libs.utils.mytime import UtilTime
from utils.exceptions import PubErrorCustom

from apps.business_new.serializers import OrderModelSerializerToJd

class jdHandler(object):

    def __init__(self,data):
        self.data =data
        self.ut = UtilTime()

    def OrderQuery(self):


        if not self.data.get('day') :
            raise PubErrorCustom("查询日期不能为空")
        if len(self.data.get('day')) != 10:
            raise PubErrorCustom("日期格式不正确")

        start_day = self.data.get('day') + ' 00:00:01'
        end_day = self.data.get('day') + ' 23:59:59'

        start_day = self.ut.string_to_timestamp(string_s=start_day)
        end_day = self.ut.string_to_timestamp(string_s=end_day)

        return {"data" : OrderModelSerializerToJd(Order.objects.filter(isjd='0',createtime__lte=end_day,createtime__gte=start_day),many=True).data}