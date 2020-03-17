

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
获取红包列表
"""

from apps.weibohongbao.weiboCallback import callbackGetHbList


if __name__ == '__main__':
    callbackGetHbList().run()