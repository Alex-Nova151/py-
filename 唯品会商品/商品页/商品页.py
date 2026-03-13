import requests
import csv
import json
import re
from pprint import pprint
import time
import random
import warnings

# 忽略SSL警告
warnings.filterwarnings('ignore')


# 解决TFS拦截问题的核心优化：添加超时、重试、动态参数
def getcontent(pid):
    url = 'https://mapi-pc.vip.com/vips-mobile/rest/shopping/pc/product/module/list/v2'

    # 优化1：cookies使用字典格式，避免格式错误
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
        'VipDFT': '-1',
        'user_class': 'b',
        'VipUINFO': 'luc%3Ab%7Csuc%3Ab%7Cbct%3Ac_new%7Chct%3Ac_new%7Cbdts%3A0%7Cbcts%3A0%7Ckfts%3A0%7Cc10%3A0%7Crcabt%3A0%7Cp2%3A0%7Cp3%3A1%7Cp4%3A0%7Cp5%3A1%7Cul%3A3105',
        'mars_sid': '1c044a785786b82c3d882dc09231eb7d',
        'visit_id': 'B78DA5229E3E222433FBA6255A7DB995',
        'VIP_QR_FIRST': '1',
        'vip_access_times': '%7B%22list%22%3A1%7D',
        'vipshop_passport_src': 'https%3A%2F%2Fcategory.vip.com%2Fsuggest.php%3Fkeyword%3D%25E6%2589%258B%25E6%259C%25BA%26ff%3D235%7C12%7C1%7C1%26tfs_url%3D%252F%252Fmapi-pc.vip.com%252Fvips-mobile%252Frest%252Fshopping%252Fpc%252Fsearch%252Fproduct%252Frank',
        '_jzqco': '%7C%7C%7C%7C%7C1.1103518368.1773066593771.1773066593771.1773197530446.1773066593771.1773197530446.0.0.0.2.2',
        'vip_tracker_source_from': '',
        'PASSPORT_ACCESS_TOKEN': 'E410E03E0957062B7F0806FB606D87F8778E1B0A',
        'VipLID': '0%7C1773197550%7C3eb271',
        'vip_sec_fp_wtk': 'cwEAAzBqMeKeeVFgqrUyqzcaiCslxtKLTDzUDryjk99vJkBoqOPb7epeyI7Uxx0bRwt9GHJUTukejKikcbh93f9MHmhsxMs',
        'fe_global_sync': '1',
        'tfs_fp_token': 'BnToLYmxP4ut9GvOQdjQju3D+seghpojptv0pfz35DoShIgRYJGwowFc+i9FpWnWWzZklKvALBJQqBTI2YpA2eg%3D%3D',
        'pg_session_no': '5',
        'waitlist': '%7B%22pollingId%22%3A%22EDA15A1B-3D6A-42D0-A6E3-DA36779604B4%22%2C%22pollingStamp%22%3A1773198319511%7D',
        'sfl_d': '0',
        'tfs_c': '1',
        'tfs_fp_timestamp': str(int(time.time() * 1000)),  # 优化2：使用当前时间戳，避免过期
        'vip_sec_fp_smtoken': 'BGnVcoHZ+GDf8UYfF5bvKpJekH4Uooql39Cv+mBTvsb1MlAQb4PuqgOyrvoEuPXZjQo+H5zcd77DVXOd7IxhGZg==',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://category.vip.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = (
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
        ('productIds', pid),
        ('scene', 'search'),
        ('standby_id', 'nature'),
        ('extParams',
         '{"stdSizeVids":"","preheatTipsVer":"3","couponVer":"v2","exclusivePrice":"1","iconSpec":"2x","ic2label":1,"superHot":1,"bigBrand":"1"}'),
        ('context', ''),
        ('tfs_fp_token', 'BnToLYmxP4ut9GvOQdjQju3D+seghpojptv0pfz35DoShIgRYJGwowFc+i9FpWnWWzZklKvALBJQqBTI2YpA2eg=='),
        ('_', str(int(time.time() * 1000))),  # 优化3：动态生成时间戳参数
    )

    # 优化4：添加重试机制和超时设置
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # 添加随机延迟，模拟真人操作
            time.sleep(random.uniform(1, 3))

            # 设置超时时间，避免请求卡死
            response = requests.get(
                url=url,
                headers=headers,
                params=params,
                cookies=cookies,
                timeout=15,
                verify=False  # 临时关闭SSL验证，避免证书问题
            )

            # 检查响应状态码
            if response.status_code == 200:
                json_data = response.json()
                # 增加数据校验，避免KeyError
                if 'data' in json_data and 'products' in json_data['data']:
                    products = json_data['data']['products']
                    product_list = []

                    for product in products:
                        # 增加字段校验，避免字段不存在导致报错
                        product_info = {
                            '标题': product.get('title', ''),
                            '品牌': product.get('brandShowName', ''),
                            '价格': product.get('price', {}).get('salePrice', ''),
                            '原价': product.get('price', {}).get('marketPrice', ''),
                            '商品ID': product.get('productId', '')
                        }
                        product_list.append(product_info)

                    return product_list  # 返回所有商品信息列表
                else:
                    print("响应数据格式异常，未找到products字段")
                    retry_count += 1
                    time.sleep(2)
            else:
                print(f"请求失败，状态码: {response.status_code}")
                retry_count += 1
                time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            retry_count += 1
            time.sleep(2)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            retry_count += 1
            time.sleep(2)
        except Exception as e:
            print(f"其他异常: {e}")
            retry_count += 1
            time.sleep(2)

    print("多次重试后仍失败")
    return None


def save_to_csv(data_list, filename='唯品会手机商品.csv'):
    """将商品数据保存到CSV文件"""
    if not data_list:
        print("没有数据可保存")
        return

    # 定义CSV表头
    headers = ['商品ID', '标题', '品牌', '价格', '原价']

    # 写入CSV文件
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_list)

    print(f"数据已保存到 {filename}，共 {len(data_list)} 条记录")


def main():
    """主函数：获取商品ID并爬取详情"""
    headers = {
        'cookie': 'vip_cps_cuid=CU1773066583392f6ace0111b6fb8ecd; vip_cps_cid=1773066583394_d365b227c1b98fd3c4dbe455c7d116a1; vip_wh=VIP_NH; PAPVisitorId=0d99e9576e11072fe5a518f71efdb72f; vip_new_old_user=1; vip_address=%257B%2522pname%2522%253A%2522%255Cu5e7f%255Cu4e1c%255Cu7701%2522%252C%2522pid%2522%253A%2522104104%2522%252C%2522cname%2522%253A%2522%255Cu5e7f%255Cu5dde%255Cu5e02%2522%252C%2522cid%2522%253A%2522104104101%2522%257D; vip_province=104104; vip_province_name=%E5%B9%BF%E4%B8%9C%E7%9C%81; vip_city_name=%E5%B9%BF%E5%B7%9E%E5%B8%82; vip_city_code=104104101; mars_cid=1773066588654_baba7187396b366af9105afdcf9ad5be; mars_pid=0; vip_sec_fp_vvid=NWFmNGU2NmEtYzBkNi00NGFhLWFmMzMtMWJhM2E0OGYzY2NlMTc3MzA2NjU4OTk4NshEKaU=; pc_fdc_area_id=103104107; pc_fdc_source_ip=1; is_default_area=1; VipRUID=658423206; VipUID=44282466db313cc57431754f0e6f0c6a; VipRNAME=ph_*****************************508; VipDegree=D1; vip_sec_fp_vid=658423206; vip_ipver=31; VipDFT=-1; user_class=b; VipUINFO=luc%3Ab%7Csuc%3Ab%7Cbct%3Ac_new%7Chct%3Ac_new%7Cbdts%3A0%7Cbcts%3A0%7Ckfts%3A0%7Cc10%3A0%7Crcabt%3A0%7Cp2%3A0%7Cp3%3A1%7Cp4%3A0%7Cp5%3A1%7Cul%3A3105; mars_sid=1c044a785786b82c3d882dc09231eb7d; visit_id=B78DA5229E3E222433FBA6255A7DB995; VIP_QR_FIRST=1; vip_access_times=%7B%22list%22%3A1%7D; vipshop_passport_src=https%3A%2F%2Fcategory.vip.com%2Fsuggest.php%3Fkeyword%3D%25E6%2589%258B%25E6%259C%25BA%26ff%3D235%7C12%7C1%7C1%26tfs_url%3D%252F%252Fmapi-pc.vip.com%252Fvips-mobile%252Frest%252Fshopping%252Fpc%252Fsearch%252Fproduct%252Frank; _jzqco=%7C%7C%7C%7C%7C1.1103518368.1773066593771.1773066593771.1773197530446.1773066593771.1773197530446.0.0.0.2.2; vip_tracker_source_from=; PASSPORT_ACCESS_TOKEN=E410E03E0957062B7F0806FB606D87F8778E1B0A; VipLID=0%7C1773197550%7C3eb271; vip_sec_fp_smtoken=BnToLYmxP4ut9GvOQdjQju3D+seghpojptv0pfz35DoShIgRYJGwowFc+i9FpWnWWzZklKvALBJQqBTI2YpA2eg==; vip_sec_fp_wtk=cwEAAzBqMeKeeVFgqrUyqzcaiCslxtKLTDzUDryjk99vJkBoqOPb7epeyI7Uxx0bRwt9GHJUTukejKikcbh93f9MHmhsxMs; fe_global_sync=1; tfs_fp_token=BnToLYmxP4ut9GvOQdjQju3D+seghpojptv0pfz35DoShIgRYJGwowFc+i9FpWnWWzZklKvALBJQqBTI2YpA2eg%3D%3D; pg_session_no=5; waitlist=%7B%22pollingId%22%3A%22EDA15A1B-3D6A-42D0-A6E3-DA36779604B4%22%2C%22pollingStamp%22%3A1773198319511%7D; tfs_fp_timestamp=1773198320470; sfl_d=0; tfs_c=1',
        'referer': 'https://category.vip.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

    url = 'https://mapi-pc.vip.com/vips-mobile/rest/shopping/pc/search/product/rank'

    params = {
        'callback': 'getMerchandiseIds',
        'app_name': 'shop_pc',
        'app_version': '4.0',
        'warehouse': 'VIP_NH',
        'fdc_area_id': '104104101',
        'client': 'pc',
        'mobile_platform': '1',
        'province_id': '104104',
        'api_key': '70f71280d5d547b2a7bb370a529aeea1',
        'user_id': '658423206',
        'mars_cid': '1773066588654_baba7187396b366af9105afdcf9ad5be',
        'wap_consumer': 'b',
        'is_default_area': '1',
        'standby_id': 'nature',
        'keyword': '手机',  # 直接使用中文，避免编码问题
        'lv3CatIds': '',
        'lv2CatIds': '',
        'lv1CatIds': '',
        'brandStoreSns': '',
        'props': '',
        'priceMin': '',
        'priceMax': '',
        'vipService': '',
        'sort': '0',
        'pageOffset': '0',
        'channelId': '1',
        'gPlatform': 'PC',
        'batchSize': '120',
        'tfs_fp_token': 'BnToLYmxP4ut9GvOQdjQju3D+seghpojptv0pfz35DoShIgRYJGwowFc+i9FpWnWWzZklKvALBJQqBTI2YpA2eg==',
        '_': str(int(time.time() * 1000)),
    }

    # 存储所有商品数据
    all_products = []

    try:
        res = requests.get(url=url, params=params, headers=headers, timeout=15, verify=False).text
        # 解析数据
        pip_list = re.findall('"pid":"(\d+)"', res)
        print(f"获取到 {len(pip_list)} 个商品ID")

        if pip_list:
            # 分批处理商品ID（每50个一批）
            batches = [pip_list[i:i + 50] for i in range(0, len(pip_list), 50)]

            for i, batch in enumerate(batches):
                if not batch:
                    continue
                print(f"\n处理第 {i + 1} 批商品ID，共 {len(batch)} 个")
                pid_str = ','.join(batch)

                # 获取商品详情
                products = getcontent(pid_str)
                if products:
                    all_products.extend(products)
                else:
                    print(f"第 {i + 1} 批商品信息获取失败")
        else:
            print("未获取到商品ID")

    except Exception as e:
        print(f"获取商品列表失败: {e}")

    # 保存数据到CSV
    save_to_csv(all_products)


if __name__ == "__main__":
    main()