

from rest_framework import serializers

import json

class OrderModelSerializerToJd(serializers.Serializer):

    createtime = serializers.IntegerField()
    jd_ordercode = serializers.CharField()
    status = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    storeId = serializers.SerializerMethodField()
    man = serializers.SerializerMethodField()

    busiId = serializers.SerializerMethodField()

    def get_busiId(self,obj):

        return "105963"


    def get_man(self,obj):

        return "aipeikeb5yc"

    def get_storeId(self,obj):

        return json.loads(obj.jd_data)['storeId']

    def get_status(self,obj):
        if str(obj.status) == '0':
            return '0'
        else:
            return '1'