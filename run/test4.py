
import re

html="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta id="viewport" name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0">
  <link href="//img.t.sinajs.cn/t4/appstyle/red_envelope/css/mobile/red_envelope/get.css?version=809210b2a1dd308d" type="text/css" rel="stylesheet" />
  <script type="text/javascript" src="//js.t.sinajs.cn/t6/apps/enp_bee/js/seer.min.js"></script>
  <script type="text/javascript">
  $CONFIG = {};
  $CONFIG['jsPath'] = '//js.t.sinajs.cn/t6/';
  $CONFIG['cssPath'] = '//img.t.sinajs.cn/t4/';
  $CONFIG['imgPath'] = '//img.t.sinajs.cn/t4/';
  $CONFIG['set_id'] = "6000060150625";
  $CONFIG['uid'] = "5904854490" ;
  </script>
  </script>
  <title>左手枫叶_95753的群组红包</title>
</head>
<body>
  <div class="receive_list" id="pl_redEnvelope_detail">
  <!-- 客人态红包详情 -->
  <div class="user_head">
    <em class="time_tip"></em>
    <div class="user_img">
    <img src="https://tvax1.sinaimg.cn/default/images/default_avatar_male_180.gif?KID=imgbed,tva&Expires=1576052739&ssig=A0n5VlMpiG" alt="">
  </div>
  <p class="red_user"><span class="username">左手枫叶_95753</span>的红包</p>
  <p class="blessing">快来抢，手快有，手慢无。恭喜发财！</p>
  <p class="total_money">收到<em class="fs_big">0.01</em>元</p>
    <a href="https://mall.e.weibo.com/h5/redenvelope/redlist?sinainternalbrowser=topnav" class="wallet_href arr_r" suda-uatrack="key=qunzu_zhadan_hongbao&value=zhadan_hongbao_lqxq_wdhb">查看我收到的红包</a>
  </div>
  <div class="list_area">
  <div class="list_amount">
    <p class="amount">1个红包，<em class="fc_red">0.01</em>元</p>
    </div>
  <ul class="list_wrap" node-type="detailList">
    <li bonus_id="424717557">
  <div class="left_info">
  <img src="https://tvax1.sinaimg.cn/default/images/default_avatar_male_180.gif?KID=imgbed,tva&Expires=1576052739&ssig=A0n5VlMpiG" />
  </div>
  <div class="right_info" node-type="leave_msg">
  <div class="top_info">
  <span class="username">右手枫叶</span>
 <span class="red_money fr">0.01元</span>
    </div>
  <div class="bottom_info" style="display:block;" node-type="leaveMsg">
  <a class="msg fc_blue" href="javascript:;" suda-uatrack="key=qunzu_zhadan_hongbao&value=zhadan_hongbao_ly">留言</a>
  <p class="pub_data" node-type="time">2019-12-11 13:20:03</p>
  </div>
  <div class="bottom_msg" style="display:none;" node-type="leaveMsgInput">
  <input type="text" node-type="msgValue" placeholder="留言不超过15字">
  <a href="javascript:;" class="fl" node-type="msgSend" data="bonus_id=424717557">发送</a>
  </div>
  </div>
  </li>
    </ul>
  <div node-type="loader" style="padding:30px;margin: -4rem 0 3rem;text-align:center;display:none;">加载中...</div>
  <div class="send_btn_area flex">
    <a href="sinaweibo://browser?url=https%3A%2F%2Fmall.e.weibo.com%2Fh5%2Fredenvelope%2Fcreate%3Fpage%3D2%26uicode%3D20000230&sinainternalbrowser=topnav&portrait_only=1" class="send_btns flex_item" suda-uatrack="key=qunzu_zhadan_hongbao&value=zhadan_hongbao_wyfhb">我也要发红包</a>
    <a href="sinaweibo://sendweibo?content=%E6%BB%A1%E6%BB%A1%E7%9A%84%E7%88%B1%E6%88%91%E9%83%BD%E6%94%B6%E5%88%B0%E5%95%A6%EF%BC%81%E6%88%91%E5%88%9A%E6%88%90%E5%8A%9F%E6%8A%A2%E5%88%B0%E4%BA%86%40%E5%B7%A6%E6%89%8B%E6%9E%AB%E5%8F%B6_95753+%E5%8F%91%E9%80%81%E7%9A%84%23%E7%BE%A4%E7%BB%84%E7%BA%A2%E5%8C%85%23%EF%BC%8C+2019%E8%AE%A9%E7%BA%A2%E5%8C%85%E9%99%AA%E4%BD%A0%E8%B7%A8%E5%B9%B4%EF%BC%8C%E5%BF%AB%E5%BF%AB%E5%8F%91%E4%B8%AA%E7%BA%A2%E5%8C%85%E8%AE%A9%E7%BE%A4%E9%87%8C%E5%97%A8%E8%B5%B7%E6%9D%A5%EF%BD%9Ehttp%3A%2F%2Ft.cn%2FRUlmvGd&urls=%5B%7B%22title%22%3A%22%5Cu7fa4%5Cu7ec4%5Cu73b0%5Cu91d1%5Cu7ea2%5Cu5305+%5Cu5e26%5Cu7740%5Cu5fae%5Cu535a%5Cu9001%5Cu60ca%5Cu559c%5Cu3002%5Cu5feb%5Cu6765%5Cu4f53%5Cu9a8c%5Cu5fae%5Cu535a%5Cu7fa4%5Cu7ec4%5Cu7ea2%5Cu5305%5Cu5427%5Cuff01%22%2C%22icon%22%3A%22http%3A%5C%2F%5C%2Fu1.sinaimg.cn%5C%2Fupload%5C%2F2014%5C%2F06%5C%2F20%5C%2Ftimeline_card_small_money.png%22%2C%22content%22%3A%22%25E6%25BB%25A1%25E6%25BB%25A1%25E7%259A%2584%25E7%2588%25B1%25E6%2588%2591%25E9%2583%25BD%25E6%2594%25B6%25E5%2588%25B0%25E5%2595%25A6%25EF%25BC%2581%25E6%2588%2591%25E5%2588%259A%25E6%2588%2590%25E5%258A%259F%25E6%258A%25A2%25E5%2588%25B0%25E4%25BA%2586%2540%25E5%25B7%25A6%25E6%2589%258B%25E6%259E%25AB%25E5%258F%25B6_95753%2B%25E5%258F%2591%25E9%2580%2581%25E7%259A%2584%2523%25E7%25BE%25A4%25E7%25BB%2584%25E7%25BA%25A2%25E5%258C%2585%2523%25EF%25BC%258C%2B2019%25E8%25AE%25A9%25E7%25BA%25A2%25E5%258C%2585%25E9%2599%25AA%25E4%25BD%25A0%25E8%25B7%25A8%25E5%25B9%25B4%25EF%25BC%258C%25E5%25BF%25AB%25E5%25BF%25AB%25E5%258F%2591%25E4%25B8%25AA%25E7%25BA%25A2%25E5%258C%2585%25E8%25AE%25A9%25E7%25BE%25A4%25E9%2587%258C%25E5%2597%25A8%25E8%25B5%25B7%25E6%259D%25A5%25EF%25BD%259Ehttp%253A%252F%252Ft.cn%252FRUlmvGd%22%7D%5D&pagetitle=发微博&go_home=1" class="send_btns flex_item yellow_btn" suda-uatrack="key=qunzu_zhadan_hongbao&value=zhadan_hongbao_fwbshb">发微博晒红包</a>
  </div>
  </div>
  <!-- 客人态红包详情 -->
  </div>
</body>
<script type="text/javascript" src="//js.t.sinajs.cn/t6/apps/enp_redenvelope_m/js/base.js"></script>
<script type="text/javascript" src="//js.t.sinajs.cn/t6/apps/enp_redenvelope_m/js/pl/redEnvelope/detail/index.js?version=809210b2a1dd308d"></script>
<script type="text/javascript" src="//js.t.sinajs.cn/t6/apps/enp_bee/js/bee-0.1.1.min.js"></script>
<script type="text/javascript" src="//js.t.sinajs.cn/open/analytics/js/suda.js"></script>
</html>
"""

res = re.compile(r'<a.*=zhadan_hongbao_gxth">?.*?</a>').findall(html)
if res and len(res)>0 and  '感谢土豪' in res[0]:
    print("成功")
else:
    print("已抢")

