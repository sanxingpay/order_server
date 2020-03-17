
from requests import request
import hashlib
import json

if __name__ == '__main__':
    url = 'http://www.gcpayz.com/paid/query/in/order/id'

    data = dict(
        orderNo="997724"
    )
    data['sign'] = ("{}{}{}".format(
        "G11959365W92A99213979DA592",
        str(data['orderNo']),
        "7312Acs2",
    )).encode("utf-8")

    data['sign']=hashlib.md5(data['sign']).hexdigest()
    url += "/{}/{}".format("997724", data.get("sign"))

    result = request('POST', url=url, json=data, verify=False,
                     headers={"Content-Type": 'application/json', "ACCESSTOKEN": "7e44b938-e52b-4580-99c7-0a79587e0f13"})

    res = json.loads(result.content.decode('utf-8'))

    print(res)
