

import time
from django.utils import timezone
from datetime import datetime,timedelta

#当前时间转时间戳
def datetime_toTimestamp():
    return time.mktime(timezone.now().timetuple())

def send_toTimestamp(t):
    t1=str(t)
    t2=time.strptime(t1[0:19],"%Y-%m-%d %H:%M:%S")
    return time.mktime(t2)

def timestamp_toDatetime(timestamp):
    return datetime.fromtimestamp(timestamp)

def timestamp_toTime(timestamp):
    timeArray = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

def diff_day(start, end=None):
    end=timezone.now()
    d = (end - start).days
    h = (end-start).seconds / 3600

    return d + round(h / 24.0, 1)

#字符串转化为时间戳
def string_toTimestamp(st):
    return time.mktime(time.strptime(st, "%Y-%m-%d %H:%M:%S"))

def islimit_time(start,end):
    t = timestamp_toDatetime(start) + timedelta(hours=end)
    t1=datetime.now()

    if t1 <= t:
        return True
    else:
        return False

def add_time(start, end):
    t = timestamp_toDatetime(start) + timedelta(hours=end)
    if t <= datetime.now():
        return '00:00:00'
    a = (t - datetime.now()).seconds
    f = a // 60
    s = a % 60

    h = f // 60
    f = f % 60
    return '%02d:%02d:%02d' % (h, f, s)


# -*- coding: utf-8 -*-
# class DateUtilsBase(object):
#
#	 @staticmethod
#	 def get_today_start():
#		 now = arrow.utcnow().to("local")
#		 return now.floor("day")
#
#	 @staticmethod
#	 def get_today_end():
#		 now = arrow.utcnow().to("local")
#		 return now.ceil("day")
#
#	 @staticmethod
#	 def get_today_start_end():
#		 return DateUtilsBase.get_today_start(), DateUtilsBase.get_today_end()
#
#	 @staticmethod
#	 def get_week_start():
#		 now = arrow.utcnow().to("local")
#		 return now.floor("week")
#
#	 @staticmethod
#	 def get_week_end():
#		 now = arrow.utcnow().to("local")
#		 return now.ceil("week")
#
#	 @staticmethod
#	 def get_week_start_end():
#		 return DateUtilsBase.get_week_start(), DateUtilsBase.get_week_end()
#
#	 @staticmethod
#	 def get_month_start():
#		 now = arrow.utcnow().to("local")
#		 return now.floor("month")
#
#	 @staticmethod
#	 def get_month_end():
#		 now = arrow.utcnow().to("local")
#		 return now.ceil("month")
#
#	 @staticmethod
#	 def get_month_start_end():
#		 return DateUtilsBase.get_month_start(), DateUtilsBase.get_month_end()
#
#	 @staticmethod
#	 def get_quarter_start():
#		 now = arrow.utcnow().to("local")
#		 return now.floor("quarter")
#
#	 @staticmethod
#	 def get_quarter_end():
#		 now = arrow.utcnow().to("local")
#		 return now.ceil("quarter")
#
#	 @staticmethod
#	 def get_quarter_start_end():
#		 return DateUtilsBase.get_quarter_start(), DateUtilsBase.get_quarter_end()
#
#	 @staticmethod
#	 def get_year_start():
#		 now = arrow.utcnow().to("local")
#		 return now.floor("year")
#
#	 @staticmethod
#	 def get_year_end():
#		 now = arrow.utcnow().to("local")
#		 return now.ceil("year")
#
#	 @staticmethod
#	 def get_year_start_end():
#		 return DateUtilsBase.get_year_start(), DateUtilsBase.get_year_end()

import arrow

class UtilTime(object):

    def __init__(self, timezone='local'):

        self.arrow = arrow
        #时区
        self.timezone = timezone

    # 获取当前时间的arrow结构
    @property
    def today(self):
        return self.arrow.now(self.timezone)

    # 当前时间戳
    @property
    def timestamp(self):
        return self.today.timestamp

    # 获取当前时间,自定义format
    def get_today_format(self, format_v="YYYY-MM-DD HH:mm:ss"):
        return self.today.format(format_v)

    # 时间戳转arrow
    def timestamp_to_arrow(self, timestamp=None):
        return self.arrow.get(timestamp).to(
            self.timezone) if timestamp else timestamp

    # arrow转时间戳
    def arrow_to_timestamp(self, arrow_v=None):
        return arrow_v.timestamp if arrow_v else arrow_v

    #arrow转字符串
    def arrow_to_string(self, arrow_s=None, format_v="YYYY-MM-DD HH:mm:ss"):
        return arrow_s.format(format_v) if arrow_s else self.today.format(format_v)

    #字符串转arrow
    def string_to_arrow(self, string_s=None, format_v="YYYY-MM-DD HH:mm:ss"):
        return self.arrow.get(
            string_s, format_v, tzinfo=self.timezone) if string_s else string_s

    #时间戳转字符串
    def timestamp_to_string(self, timestamp,format_v="YYYY-MM-DD HH:mm:ss"):
        return self.arrow_to_string(self.timestamp_to_arrow(timestamp),format_v)

    #时间戳转arrow
    def timestamp_to_arrow(self, timestamp):
        return self.arrow.get(timestamp)

    #字符串转时间戳
    def string_to_timestamp(self, string_s=None,
                            format_v="YYYY-MM-DD HH:mm:ss"):
        return self.string_to_arrow(
            string_s, format_v).timestamp if string_s else string_s

    #时间日期加减
    def replace(self, arrow_v, **kwargs):
        """
			example :
				days = -1  减一天
				weeks = -1 减一周
				mounts = -1 减一个月
				quarters = -1 减一个季度
				years = -1 减一年
				hours = -1 减一小时
				minutes = -1 减一分钟
				seconds = -1 减一秒钟
		"""
        return arrow_v.replace(**kwargs)

    #判断周几
    def get_week_day(self, todays=None):
        """
			todays: "YYYY-MM-DD" 字符串
			周一:1 ... 周日:7
		"""
        format_v = "YYYY-MM-DD"
        day_arrow = self.today if not todays else self.string_to_arrow(
            todays, format_v)
        day_string = self.arrow_to_string(
            self.today, format_v) if not todays else self.arrow_to_string(
                self.string_to_arrow(todays, format_v), format_v)

        week1 = day_arrow.floor('week')
        if self.arrow_to_string(week1, format_v) == day_string:
            return 1
        elif self.arrow_to_string(week1.replace(days=1),
                                  format_v) == day_string:
            return 2
        elif self.arrow_to_string(week1.replace(days=2),
                                  format_v) == day_string:
            return 3
        elif self.arrow_to_string(week1.replace(days=3),
                                  format_v) == day_string:
            return 4
        elif self.arrow_to_string(week1.replace(days=4),
                                  format_v) == day_string:
            return 5
        elif self.arrow_to_string(week1.replace(days=5),
                                  format_v) == day_string:
            return 6
        elif self.arrow_to_string(week1.replace(days=6),
                                  format_v) == day_string:
            return 7
        else:
            return None


if __name__ == '__main__':


    class CustDateType(object):

        @staticmethod
        def get_amount(obj):
            if obj['unit'] == 'F':
                return "%.{}lf".format(int(obj['point']))%(float(obj['value'])*100.0)
            elif obj['unit'] == 'Y' :
                return "%.{}lf".format(int(obj['point']))%(float(obj['value']))
            else:
                print("标志错误!")

        @staticmethod
        def get_date(obj):
            if obj.get("type") == "appoint":
                return obj.get("value")
            else:
                ut = UtilTime()
                return  ut.timestamp \
                    if obj.get("format", None) == 'timestamp' else \
                        ut.arrow_to_string(arrow_s=ut.today,format_v=obj.get("format",None)) if obj.get("format",None) \
                            else ut.arrow_to_string(arrow_s=ut.today)

        @staticmethod
        def get_string(obj):
            return str(obj.get("value"))

        @staticmethod
        def get_int(obj):
            return int(obj.get("value"))


    rules={"request_url": "http://localhost:9001", "request_urlCallBack": "http://localhost:9001", "request_method": "POST",
     "request_type": "json", "requestData": [
        {"key": "Amt", "dataType": "amount", "type": "appoint", "value": "amount", "unit": "Y", "point": 2,
         "sign": True},
        {"key": "OrderId", "dataType": "string", "type": "appoint", "value": "ordercode", "sign": True},
        {"key": "UserId", "dataType": "string", "type": "custom", "value": "5", "sign": True},
        {"key": "SignType", "dataType": "string", "type": "custom", "value": "MD5", "sign": False},
        {"key": "DateTime", "dataType": "date", "type": "custom", "value": "", "sign": True, "format": "timestamp"},
        {"key": "secret", "dataType": "string", "type": "custom", "value": "sfsfadf123213", "sign": False}],
     "sign_signKey": "sign", "sign_signType": "md5", "sign_signEncode": "UTF-8", "sign_signDataType": "key-ascii-sort",
     "sign_dataType": "upper", "sign_signValue": "", "sign_signBefore": "", "sign_signAppend": "-{secret}",
     "request_secret": "ddddddddddd"}

    request_data={
        "amount" : 100.987,
        "ordercode":123123213,
        "date1": "20180101",
        "bankcode" : "11123123"
    }

    data={}
    for item in rules['requestData']:
        if 'value' in item:
            item['value'] = request_data.get(item['value']) if item.get("type") == "appoint" else item['value']
        res = getattr(CustDateType,"get_{}".format(item['dataType']))(item)

        data[item['key']] = res
    print(data)

