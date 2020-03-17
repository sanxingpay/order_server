import json
import logging
import requests

headers = {
    "Cookie": "unpl=V2_ZzNtbUsAFBIiDEJcLh0JBGJWEVpLBBAWc1pFUnJNWQBhAhFeclRCFX0URlVnGVkUZAMZXENcRxJFCEdkeBBVAWMDE1VGZxBFLV0CFSNGF1wjU00zQwBBQHcJFF0uSgwDYgcaDhFTQEJ2XBVQL0oMDDdRFAhyZ0AVRQhHZHgYVA1vBRZfS1dzJXI4dmR9EFQBbwQiXHJWc1chVEBTch9VAioAE1VKX0URdwFGZHopXw%3d%3d; retina=1; cid=3; webp=1; __jdv=123%7Cdirect%7C-%7Cnone%7C-%7C1571058061038; visitkey=9167145407902092; TrackerID=oi8lWlewpOBp3700e4Xq-78uKMv2kDyPzvahkDtDb9o9Jfb_bU98PdMAodxW2T-1myOEh8OjdT0K-nMT80BUxd1BI6maSsGfQQQdZL4HGLX-lifQTzJJt2wMm8-E68CWw3ZxllpO6AdWkHz9ml0D2g; pt_key=AAJdpfKPADDX5Hoq7O-gzqRVKyVFJ5NUpdGWervlINBhjjyM1dkydG9De6elgfDdJRhLZepEDyI; pt_pin=jd_4115779e208a6; pt_token=k6extcg8; pwdt_id=jd_4115779e208a6; shshshfp=73c72033ff2d6fd2764b79ed74d390d8; shshshfpa=b5152faa-0f0f-1347-be54-ede8de458c68-1571156571; shshshfpb=uUTh4d%2BA2hAJqnFPW3OcyAA%3D%3D; 3AB9D23F7A4B3C9B=AHKTIAMJEDRLFXXHWX7QXOX44HHYPOIBZ7ZH6DR5HE237ZW4FVJ72N2KUTFDYAYQZD7LAAX7JTX23YVR7YZHH326K4; qd_ad=mjrpay.jd.com%7C-%7Cjd%7C-%7C0; qd_uid=K1S2D58J-DBG2SQMHUYVNJGSFEWR4; qd_sq=1; qd_fs=1571157089728; qd_ls=1571157089728; qd_ts=1571157089728; __jda=123.2099975381.1571058058.1571058061.1571156570.3; mba_muid=2099975381; login_source_type=wx_qq",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "http://md-mobile.jd.com",
    "Host": "md-mobile.jd.com",
}


class JD(object):

    def __init__(self,payId,cookie):
        self.payId = payId
        self.headers = headers
        self.cookie = cookie
        self.addressIds = self.addressDetail()



    def addressDetail(self):
        '''
        获取收获地址
        :return:
        '''
        url = "http://md-mobile.jd.com/order/getAddressList"
        rep = requests.get(url=url,headers=self.headers, verify=False)
        data =json.loads(rep.text)['deliveryGoodsVos'][0]
        addressDetail = {
            "consignee": data['consignee'],
            "telephone": data['telephone'],
            "addressDetail": data['addressDetail'],
            "addressIds": '{},{},{}'.format(data['provinceId'], data['cityId'], data['countyId']),
            "deliveryFare": "0",
            "enderId": "105963",
        }

        return addressDetail

    def create_order(self):
        '''
        创建订单
        :return:
        '''

        # self.headers["Cookie"] = self.cookie,

        url = "http://md-mobile.jd.com/order/linkOrderSubmit/".format(self.payId)
        rep = requests.post(url=url, data=self.addressIds,headers=self.headers, verify=False)


    def payId_code(self):
        '''
        生成交易码
        :return:
        '''
        url = "http://md-mobile.jd.com/order/toCounter"

        data = {
            "orderId": "105776405074",
            "screen": "",
            "goodsTotalPrice": "40.00",
            "deliveryFare": "0",
            "payLinkKey":self.payId,
        }
        rep = requests.post(url=url, verify=False, headers=headers, data=data)  # 获取支付号和请求京东收银地址
        print(rep)
        # if json.loads(rep.text.get("counterUrl")) == "1":  # 请求成功
        url = json.loads(rep.text).get("counterUrl")  # 获取跳转求京东收银地址
        print(url)
        return url


    def  jd_checkstand(self,url):
        ''''
        京东收银台
        '''

        rep = requests.get(url=url,headers=headers,verify=True)
        print(rep.text)
        payId = url.split("=")[1].split("&")[0]
        return payId

    def payld_ajx(self,payId):
        '''
        发起支付

        :return:
        '''
        headers = {
            "Cookie": "unpl=V2_ZzNtbUsAFBIiDEJcLh0JBGJWEVpLBBAWc1pFUnJNWQBhAhFeclRCFX0URlVnGVkUZAMZXENcRxJFCEdkeBBVAWMDE1VGZxBFLV0CFSNGF1wjU00zQwBBQHcJFF0uSgwDYgcaDhFTQEJ2XBVQL0oMDDdRFAhyZ0AVRQhHZHgYVA1vBRZfS1dzJXI4dmR9EFQBbwQiXHJWc1chVEBTch9VAioAE1VKX0URdwFGZHopXw%3d%3d; retina=1; cid=3; webp=1; __jdv=123%7Cdirect%7C-%7Cnone%7C-%7C1571058061038; visitkey=9167145407902092; TrackerID=oi8lWlewpOBp3700e4Xq-78uKMv2kDyPzvahkDtDb9o9Jfb_bU98PdMAodxW2T-1myOEh8OjdT0K-nMT80BUxd1BI6maSsGfQQQdZL4HGLX-lifQTzJJt2wMm8-E68CWw3ZxllpO6AdWkHz9ml0D2g; pt_key=AAJdpfKPADDX5Hoq7O-gzqRVKyVFJ5NUpdGWervlINBhjjyM1dkydG9De6elgfDdJRhLZepEDyI; pt_pin=jd_4115779e208a6; pt_token=k6extcg8; pwdt_id=jd_4115779e208a6; shshshfp=73c72033ff2d6fd2764b79ed74d390d8; shshshfpa=b5152faa-0f0f-1347-be54-ede8de458c68-1571156571; shshshfpb=uUTh4d%2BA2hAJqnFPW3OcyAA%3D%3D; 3AB9D23F7A4B3C9B=AHKTIAMJEDRLFXXHWX7QXOX44HHYPOIBZ7ZH6DR5HE237ZW4FVJ72N2KUTFDYAYQZD7LAAX7JTX23YVR7YZHH326K4; qd_ad=mjrpay.jd.com%7C-%7Cjd%7C-%7C0; qd_uid=K1S2D58J-DBG2SQMHUYVNJGSFEWR4; qd_sq=1; qd_fs=1571157089728; qd_ls=1571157089728; qd_ts=1571157089728; __jda=123.2099975381.1571058058.1571058061.1571156570.3; mba_muid=2099975381; login_source_type=wx_qq",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "accept-language": "zh-CN,en-US;q=0.8",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://pay.m.jd.com/cpay/pay-index.html?payId={}&appId=d_m_mdbang".format(payId),
        }
        data = json.dumps({"appId":"d_m_mdbang","payId":payId})
        url = 'https://pay.m.jd.com/index.action?functionId=wapWeiXinPay&body={}&appId=d_m_mdbang&payId={}&_format_=JSON'.format(
            data,payId)

        rep = requests.get(url=url,verify=False,headers=headers)
        print(rep.text)



    def main(self):
        '''
        程序主入口
        :return:
        '''

        # 生成订单
        self.create_order()
        # 生成交易码
        url = self.payId_code()
        print(url)
        # 进入京东收银台
        # url="https://pay.m.jd.com/cpay/pay-index.html?payId=e5f901c1677f4a88be25527efc4a562e&appId"
        payId= self.jd_checkstand(url)
        print(payId)

        # 发起支付
        self.payld_ajx(payId)


if __name__ == '__main__':

    try:
        payId = '14177ae1e5cdac8857b9c9f5ea9590ab'
        cookie = 1212
        JD(payId, cookie).main()

    except Exception as e:
        '''异常
        '''
        FORMAT = "%(asctime)s %(name)s %(levelname)s %(levelno)s %(lineno)s %(message)s"
        logging.basicConfig(filename="jd.log", filemode="a", datefmt="%Y/%m/%d %H:%M:%S", format=FORMAT)
        logging.error(payId + "==>>>>>>>>" + str(e))
