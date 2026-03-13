from DrissionPage import ChromiumPage
from pprint import pprint
import re
import csv
from fake_useragent import UserAgent
import time
f =open('商品页.csv', mode='w', encoding='utf-8', newline='')
#字典写入方法
csv_writer=csv.DictWriter(f,fieldnames=[
    '标题',
    '原价',
    '销量',
    '店名',
    'id',
    '卖点',
    '颜色',
    '评论',
])
#写入表头
csv_writer.writeheader()
dp = ChromiumPage()


#from DrissionPage import  ChromiumOptions
#path = r"D:\腾讯电脑管家软件搬家\软件搬家\Google Chrome\chrome.exe"
#ChromiumOptions().set_browser_path(path).save()

# 加载前要监听
dp.listen.start('api.m.jd.com/api?appid=search-pc-java&t')
# 访问
dp.get('https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&suggest=1.his.0.0&wq=&pvid=648939b156ff42619bcf9d0574574706&spmTag=YTAyMTkuYjAwMjM1Ni5jMDAwMDQ2ODkuMSUyM2hpc2tleXdvcmQ')
#下滑页面
# 循环
for page in range(1,11):
    print('正在采集第{}'.format(page))



    next_page = dp.ele('text=下一页')  #ele 元素缩写  模糊定位
    dp.scroll.to_see(next_page) #下滑到某元素可见

    # 等待加载   监听多个 返回列表
    resp_list =dp.listen.wait(5)
    #for 循环 列表
    for resp in resp_list:

        #获取数据
        json_data =resp.response.body
        #获取键值对
        keys = json_data.keys()
        # 判断
        if 'abBuriedTagMap' in keys:
            # 字典取值 遍历
            for i in json_data['data']['wareList']:

               # pprint(i)
                title= i['wareName'].replace('\n', '')
               #替换标题
                new_title =re.sub('<.*?>', '',title)
                dit={
                    '标题':new_title,
                    # 核心是用 or {} 强制把 None 转为空字典
                    '原价': (i.get('wareBuried') or {}).get('price', '无原价').replace('\n', '').strip(),
                    '销量': i['totalSales'],
                    '店名': i['shopName'],
                    'id': i['skuId'],
                    '卖点': i['sellingPoint'],
                    '颜色': i['color'],
                    '评论': i['commentFuzzy'],

                }
               #写入数据
                csv_writer.writerow(dit)
                print(dit)
    next_page.click()