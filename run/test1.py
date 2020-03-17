import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()


from rest_framework import serializers

class Amount:
    amount = 0

class AmountSerializers(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)


Amount.amount = "123.123"
print(AmountSerializers(Amount,many=False).data)