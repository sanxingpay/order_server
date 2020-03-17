

import time
from functools import wraps
from django.db import transaction
from libs.core.http.response import HttpResponse
from libs.utils.log import logger
from libs.utils.exceptions import PubErrorCustom,InnerErrorCustom

class Core_connector_DAIFU:
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


        if not isinstance(res, dict):
            res = {'data': None, 'msg': None, 'header': None}
        if 'data' not in res:
            res['data'] = None
        if 'msg' not in res:
            res['msg'] =  {}
        if 'header' not in res:
            res['header'] = None
        # logger.info("返回报文:{}".format(res['data']))
        return HttpResponse(data= res['data'],headers=res['header'], msg=res['msg'])

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