from DrissionPage import ChromiumPage
import time
import re
import csv
from fake_useragent import UserAgent

f =open('商品评论数据/商品10.csv', mode='w', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(f,fieldnames=[
    '评论',
    '分数',
    '产品',
    '名字'
])
csv_writer.writeheader()
dp =ChromiumPage()
#dp.listen.start('client.action')

dp.get('https://item.jd.com/100248102702.html')

time.sleep(2)
dp.listen.start('client.action')

dp.scroll.to_see('全部评价')
time.sleep(2)
dp.ele('text=全部评价').click()

for page in range(1,21):
    print(f'正在采集{page}')
    time.sleep(2)
    if page == 1:

        resp = dp.listen.wait()
        json_data =resp.response.body
    else:
        resp = dp.listen.wait()
        json_data =resp.response.body

    #print(json_data)
    #{'body': {'cityId': 72, 'cityName': '朝阳区', 'complete': True, 'countyId': 55653, 'countyName': '八里庄街道', 'hideLevel': '3', 'provinceId': 1, 'provinceName': '北京', 'townId': 0}, 'code': '0', 'message': 'success', 'timestamp': 1772963525455}
    # 不对 延时等待
    #解析数据
    datas = json_data['result']['floors'][2]['data']
    for data in datas:
       try:
            dit ={
                '评论':data['commentInfo']['commentData'],
                '分数': data['commentInfo']['commentScore'],
                '产品': data['commentInfo']['productSpecifications'],
                '名字': data['commentInfo']['userNickName']

            }
            csv_writer.writerow(dit)
            print(dit)
       except:
           pass
    #定位评论页面
    tab =dp.ele('css:._rateListContainer_1ygkr_45')
    tab.scroll.to_bottom()
    time.sleep(2)