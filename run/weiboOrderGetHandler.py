import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

"""
同步红包支付号
"""

from apps.weibohongbao.weiboCallback import callbackGetOrdercode


if __name__ == '__main__':
    callbackGetOrdercode().run()