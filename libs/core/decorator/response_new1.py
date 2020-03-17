
import time
from functools import wraps
from django.db import transaction
from libs.utils.log import logger
from libs.utils.exceptions import PubErrorCustom,InnerErrorCustom
from django.shortcuts import render

class Core_connector_Response_Html:
    def __init__(self,**kwargs):
        self.transaction = kwargs.get('transaction',None)
        self.pagination = kwargs.get('pagination',None)
        self.serializer_class = kwargs.get('serializer_class',None)
        self.model_class = kwargs.get('model_class',None)
        self.lock = kwargs.get('lock',None)
        self.encryption =  kwargs.get('encryption',False)
        self.check_google_token = kwargs.get('check_google_token',None)
        self.is_file = kwargs.get('is_file',None)
        self.h5ValueHandler = None

    def __request_validate(self,request):

        logger.info("代付请求数据:{}".format(request.data))


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
                # self.start = time.time()
                self.__request_validate(request)
                response=self.__run(func,outside_self,request,*args, **kwargs)
                # self.end=time.time()
                return response
            except PubErrorCustom as e:
                print("PubErrorCustom")
                print(e.msg)
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return render(request, 'error.html', {'error': e.msg})
            except InnerErrorCustom as e:
                print(1)
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return render(request, 'error.html', {'error': e.msg})
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return render(request, 'error.html', {'error': str(e)})
        return wrapper