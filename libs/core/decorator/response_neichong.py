

import time
from functools import wraps
from django.db import transaction
from libs.core.http.response import HttpResponse
from libs.utils.log import logger
from libs.utils.exceptions import PubErrorCustom,InnerErrorCustom

class Core_connector_NEICHONG:
    def __init__(self,**kwargs):
        self.transaction = kwargs.get('transaction',None)
        self.pagination = kwargs.get('pagination',None)

    def __request_validate(self,request):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):

        if self.transaction:
            with transaction.atomic():
                res = func(outside_self, request, *args, **kwargs)
        else:
            res = func(outside_self, request, *args, **kwargs)

        return res

    def __response__validate(self,outside_self,func,response):
        logger.info('[%s : %s]Training complete in %lf real seconds' % (outside_self.__class__.__name__, getattr(func, '__name__'), self.end - self.start))

        return response

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.start = time.time()
                self.__request_validate(request)
                response=self.__run(func,outside_self,request,*args, **kwargs)
                self.end=time.time()
                return response
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse(success=False, msg=e.msg, data=None)
            except InnerErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse(success=False, msg=e.msg, rescode=e.code, data=None)
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse(success=False, msg=str(e), data=None)
        return wrapper