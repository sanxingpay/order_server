
rules={
    #上游请求网关
    "request":{
        "url":"http://localhost:8000",
        "method" : "POST",
        "type":"json",
    },
    # 上游返回数据处理
    "return":{
        "type":"json",
        "codeKey" : "code",
        "msgKey" : "msg",
        "ok" : "1",
        "url" : "data.url"
    },
    #密钥
    "secret" :"fsdafsdafsaf",
    #请求值数据
    "requestData":[
        {
            "key":"amount",
            "type" : "appoint",
            "dataType" : "amount",
            "unit" : "Y",
            "point": 1,
            "value": "order.amount",
            "sign":True
        },
        {
            "key": "amount1",
            "type": "appoint",
            "dataType": "amount",
            "unit": "F",
            "point":2,
            "value": "user.amount",
            "sign": True
        },
        {
            "key": "date",
            "type": "custom",
            "dataType" : "date",
            "format" : "YYYY-MM-DD HH:mm:ss",
            "sign": True
        },
        {
            "key": "timestamp",
            "type": "custom",
            "dataType": "timestamp",
            "sign": True
        },
    ],
    #按照key ascii码排序 然后md5加密
    "sign":{
        "signType" : "md5",
        "signEncode" : "utf-8",
        "signDataType" : "key-ascii-sort",
        "signAppend" : "-{secret}"
    }
    # 按照指定key排序md5加密
    # "sign":{
    #     "signType" : "md5",
    #     "signEncode" : "utf-8",
    #     "signDataType" : "key-appoint",
    #     "signValue" : "{secret}-{secret}",
    #     "signKey" : "sign",
    #     "dataType" : "upper"
    # }
}