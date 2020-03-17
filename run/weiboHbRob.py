

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
抢后国宝
"""

from apps.weibohongbao.weiboCallback import callbackRobHb


if __name__ == '__main__':
    callbackRobHb().run()