import requests
import csv
import re
import json
import time
import random
from datetime import datetime


# 创建CSV文件并写入表头
def init_csv(file_name='商品10.csv'):
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 定义CSV表头
        headers = [
            '评论ID',  '评论内容',
            '商品名称', '商品品牌', '商品颜色规格', '商品价格'
        ]
        writer.writerow(headers)


# 解析评论数据并写入CSV
def write_comment_to_csv(comment_data, file_name='商品10.csv'):
    # 提取关键信息
    row_data = [
        comment_data.get('reputation', {}).get('reputationId', ''),  # 评论ID
        comment_data.get('reputation', {}).get('content', ''),  # 评论内容
        comment_data.get('reputationProduct', {}).get('goodsName', ''),  # 商品名称
        comment_data.get('reputationProduct', {}).get('brandName', ''),  # 商品品牌
        comment_data.get('reputationProduct', {}).get('colorInfo', ''),  # 颜色规格
        comment_data.get('reputationProduct', {}).get('vipShopPrice', ''),  # 会员价

    ]

    # 写入CSV文件
    with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)


# 主爬虫函数
def crawl_comments():
    # 初始化CSV文件
    init_csv()

    for i in range(1, 11):
        print(f"正在抓取第 {i} 页评论...")
        url = 'https://mapi-pc.vip.com/vips-mobile/rest/content/reputation/queryBySpuId_for_pc?callback=getCommentDataCb&app_name=shop_pc&app_version=4.0&warehouse=VIP_NH&fdc_area_id=104104101&client=pc&mobile_platform=1&province_id=104104&api_key=70f71280d5d547b2a7bb370a529aeea1&user_id=658423206&mars_cid=1773066588654_baba7187396b366af9105afdcf9ad5be&wap_consumer=b&is_default_area=1&spuId=5147410482083196929&brandId=1713638214&page=1&pageSize=10&functions=angle&timestamp=1773210238000&keyWordNlp=%E5%85%A8%E9%83%A8-%E6%8C%89%E9%BB%98%E8%AE%A4%E6%8E%92%E5%BA%8F&tfs_fp_token=Bcx8ISSU6cl%2Fw7YjwgASZbAeBhix253bNN7eTYpNP72u%2BibkxysMksy88wwQlr7s3r%2BQ6sOuDz2dgDjpUg%2BkGdA%3D%3D&_=1773210221081'

        cookies = {
            'vip_cps_cuid': 'CU1773066583392f6ace0111b6fb8ecd',
            'vip_cps_cid': '1773066583394_d365b227c1b98fd3c4dbe455c7d116a1',
            'vip_wh': 'VIP_NH',
            'PAPVisitorId': '0d99e9576e11072fe5a518f71efdb72f',
            'vip_new_old_user': '1',
            'vip_address': '%257B%2522pname%2522%253A%2522%255Cu5e7f%255Cu4e1c%255Cu7701%2522%252C%2522pid%2522%253A%2522104104%2522%252C%2522cname%2522%253A%2522%255Cu5e7f%255Cu5dde%255Cu5e02%2522%252C%2522cid%2522%253A%2522104104101%2522%257D',
            'vip_province': '104104',
            'vip_province_name': '%E5%B9%BF%E4%B8%9C%E7%9C%81',
            'vip_city_name': '%E5%B9%BF%E5%B7%9E%E5%B8%82',
            'vip_city_code': '104104101',
            'mars_cid': '1773066588654_baba7187396b366af9105afdcf9ad5be',
            'mars_pid': '0',
            'vip_sec_fp_vvid': 'NWFmNGU2NmEtYzBkNi00NGFhLWFmMzMtMWJhM2E0OGYzY2NlMTc3MzA2NjU4OTk4NshEKaU=',
            'pc_fdc_area_id': '103104107',
            'pc_fdc_source_ip': '1',
            'is_default_area': '1',
            'VipRUID': '658423206',
            'VipUID': '44282466db313cc57431754f0e6f0c6a',
            'VipRNAME': 'ph_*****************************508',
            'VipDegree': 'D1',
            'vip_sec_fp_vid': '658423206',
            'vip_ipver': '31',
            'user_class': 'b',
            'VipUINFO': 'luc%3Ab%7Csuc%3Ab%7Cbct%3Ac_new%7Chct%3Ac_new%7Cbdts%3A0%7Cbcts%3A0%7Ckfts%3A0%7Cc10%3A0%7Crcabt%3A0%7Cp2%3A0%7Cp3%3A1%7Cp4%3A0%7Cp5%3A1%7Cul%3A3105',
            'mars_sid': '1c044a785786b82c3d882dc09231eb7d',
            'VIP_QR_FIRST': '1',
            'vip_access_times': '%7B%22list%22%3A1%7D',
            '_jzqco': '%7C%7C%7C%7C%7C1.1103518368.1773066593771.1773066593771.1773197530446.1773066593771.1773197530446.0.0.0.2.2',
            'PASSPORT_ACCESS_TOKEN': 'E410E03E0957062B7F0806FB606D87F8778E1B0A',
            'VipLID': '0%7C1773197550%7C3eb271',
            'fe_global_sync': '1',
            'vip_tracker_source_from': '',
            'visit_id': '5A266B8DDA886267F678754CC79BF1C9',
            'VipDFT': '-1',
            'sfl_d': '0',
            'tfs_c': '1',
            'pg_session_no': '19',
            'vip_sec_fp_smtoken': 'BVnNsbm3oWQAiK9Tj0kezgRpeX/RMn8C+mHZTvm8Bq1Bu9W7c1vXxc0cFlMgZbXWyfTjIG1sJxH+VBxOVI/TV7g==',
            'vip_sec_fp_wtk': 'cwEAAzBqMTVhWou9Ng0NIf8jbSFobEhrqZbOkR95l3QAYddhCMnBlnQr9Qeu0BKX9SDF0eO4jApozCEFohNMktMgkqIxXsc',
            'tfs_fp_token': 'BVnNsbm3oWQAiK9Tj0kezgRpeX/RMn8C+mHZTvm8Bq1Bu9W7c1vXxc0cFlMgZbXWyfTjIG1sJxH+VBxOVI/TV7g%3D%3D',
            'waitlist': '%7B%22pollingId%22%3A%2263AFE144-4307-4C56-85F0-4179CFAAC4D2%22%2C%22pollingStamp%22%3A1773207670463%7D',
            'tfs_fp_timestamp': '1773207670979',
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://detail.vip.com/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        # 使用动态时间戳避免被拦截
        current_timestamp = str(int(time.time() * 1000))

        params = (
            ('callback', 'getCommentDataCb'),
            ('app_name', 'shop_pc'),
            ('app_version', '4.0'),
            ('warehouse', 'VIP_NH'),
            ('fdc_area_id', '104104101'),
            ('client', 'pc'),
            ('mobile_platform', '1'),
            ('province_id', '104104'),
            ('api_key', '70f71280d5d547b2a7bb370a529aeea1'),
            ('user_id', '658423206'),
            ('mars_cid', '1773066588654_baba7187396b366af9105afdcf9ad5be'),
            ('wap_consumer', 'b'),
            ('is_default_area', '1'),
            ('spuId', '2768383906444582913'),
            ('brandId', '1711576586'),
            ('page', str(i)),
            ('pageSize', '10'),
            ('functions', 'angle'),
            ('timestamp', current_timestamp),
            ('keyWordNlp', '\u5168\u90E8-\u6309\u9ED8\u8BA4\u6392\u5E8F'),
            ('tfs_fp_token',
             'BVnNsbm3oWQAiK9Tj0kezgRpeX/RMn8C+mHZTvm8Bq1Bu9W7c1vXxc0cFlMgZbXWyfTjIG1sJxH+VBxOVI/TV7g=='),
            ('_', current_timestamp),
        )

        try:
            # 添加随机延迟，模拟真人操作
            time.sleep(random.uniform(1, 3))

            response = requests.get(
                url=url,
                headers=headers,
                params=params,
                cookies=cookies,
                timeout=15
            )

            # 移除回调函数包裹，提取JSON数据
            response_text = response.text
            # 使用正则提取JSON部分
            json_str = re.search(r'getCommentDataCb\((.*)\)', response_text).group(1)
            # 解析JSON
            data = json.loads(json_str)

            if data.get('code') == 1 and data.get('data'):
                # 遍历每条评论
                for comment in data['data']:
                    # 写入CSV
                    write_comment_to_csv(comment)
                    print(f"成功解析并写入评论: {comment.get('reputation', {}).get('reputationId', '')}")
            else:
                print(f"第{i}页无数据或请求失败: {data.get('msg', '未知错误')}")

        except Exception as e:
            print(f"第{i}页抓取失败: {str(e)}")
            continue


# 执行爬虫
if __name__ == '__main__':
    crawl_comments()
    print("评论抓取完成，数据已保存到 vip_comments.csv 文件中")