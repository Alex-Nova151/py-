# ======================== 第一步：安装依赖 ========================
# pip install requests brotli zstandard

import requests
import json
import hashlib
import time
import gzip
import brotli
import zstandard as zstd
import csv
from io import BytesIO
from typing import Union, Dict, Any
import re

# ======================== 第二步：核心配置 ========================
COOKIE = (
    "t=8bdcaeeae773cfa99a65af6b0516ae31; thw=xx; wk_cookie2=13b6e243aa04733a0ddc226b9e6c5883; "
    "aui=2211732220148; useNativeIM=false; cookie2=1e8c563faa59f5c82ae148dee363c5df; "
    "_tb_token_=e363f31b8913b; mtop_partitioned_detect=1; "
    "_m_h5_tk=108e6e1d2b1f33851be4ed2146b1d820_1773063203443; "
    "_m_h5_tk_enc=309639baf91d898c26ebd55b58d09f60; xlly_s=1; cna=ZaTJIUMEym4BASQOBFu0d0OC; "
    "_samesite_flag_=true; 3PcFlag=1773055145577; unb=2222117525605; lgc=tb796526637184; "
    "cancelledSubSites=empty; cookie17=UUpjNFQlp6X6R2jFXg%3D%3D; dnk=tb796526637184; "
    "tracknick=tb796526637184; _l_g_=Ug%3D%3D; sg=45a; _nk_=tb796526637184; "
    "cookie1=ACkwAPHjFbL7S4jJqjFH0ELmVrj21Yi83aAA1xO9o6o%3D; mt=ci=0_1; "
    "wk_unb=UUpjNFQlp6X6R2jFXg%3D%3D; "
    "sgcookie=E100kpb873qikcrsCUDTZx6s4wJ%2FxYcjKUrWAd8dn1aiTU2KcqicQ%2FsPrkOaX327%2FJtci8xUdZsEvNlGCdcn0Bp%2BmgWUflIByOFUypJfggxnics%3D; "
    "csg=9e54104d; skt=ecc5aac1b9a30db9; "
    "uc1=cookie21=U%2BGCWk%2F7oPIg&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&existShop=false&cookie14=UoYZaZf%2F2ht%2BLw%3D%3D&pas=0&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D; "
    "sn=; uc3=nk2=F5RCbIpmBlskEIrjoV4%3D&lg2=URm48syIIVrSKA%3D%3D&vt3=F8dD29ZlsbhgDxJsfUI%3D&id2=UUpjNFQlp6X6R2jFXg%3D%3D; "
    "existShop=MTc3MzA1NTIwNA%3D%3D; "
    "uc4=nk4=0%40FY4JgmwqUdyP3Wz5wmX0%2F2FpS1r%2BhtamwQ%3D%3D&id4=0%40U2gp9GH8uFkAtfOmJfkNq6f%2B9jvdmci%2B; "
    "_cc_=V32FPkk%2Fhw%3D%3D; _hvn_lgc_=0; "
    "havana_lgc2_0=eyJoaWQiOjIyMjIxMTc1MjU2MDUsInNnIjoiYmYyZWJkN2JjNDVlZWVjMGVkNzQ5N2RhNmRhMGM4MWMiLCJzaXRlIjowLCJ0b2tlbiI6IjFnd1plOHF5MmxrQXI0MW5YbjUzX3B3In0; "
    "ultraCookieBase=1k6S5%2BcxkgQpZVbCskN2%2BBYVKqvrrXwY4mFaS3TuuJbPmAFDnAyp%2FRUQw0Px8FrIZ6aWdtY0jWAtg8y1k6YN31wgE%2BXDKGrf2xWAoWPL%2BoyZdiQfzcugyivvFPyRlY3sGSCHUHjvB22kkt5OgNIjtwh2l%2F7QCeONpc4q%2Bd7FKWx3J321KScAKno5ADxWazFe%2FbwbI46JAvOWx5GTmglmSDxsDJx5g1PFw9WvCtgIErbphVBh3ajztmMxa%2FFP9adjv8YhjMzQ%2Bvuk%2FLg5FyAHTFi8lBbZzzvR%2BsFPPraqz6ercOOUSwpJysb1E1BJa27Cp3NQmChSqPN6oyi7L; "
    "havana_lgc_exp=1804159206918; sdkSilent=1773084006917; havana_sdkSilent=1773084006917; "
    "tfstk=gGQmf-i4si-j1Nkz-A8bVc3bk8r8cET6KO39BFpa4LJSDFEf6CjlOOvY1oTAqdXPEKuYGsBk_Of1DStThfcfr90tk-Zf_VY97JeLJyCfMFTapEfLX2kXGC04WhRVaEOtMkJPfyCfGbRdVnruJPj3enAZbdWwz3RXtFR27IlzZCAHQFJ2bYoyTLJw7OuVa4R6_dJw_O5zZC9yQF8NQUPk1LJw7FlVKSJAh9QzKq1B5YdoCaODmp523sCAzzxrc_volq_lqeJUoL0Z7aAc_9axW2q9LM9vvdXzyqYGaCXkvi2noOfNOG-lSxPALTSGQQs7IcvhbsICb3V4u_YDn9b5UjoMoGWfSnsm1W1yuTsBdnr7FQbAJhvBqYyVw_v2xGXYFVJAx_WkvaH-JeSCENxe8g5j4DPfjVOz6aosfnRWZpeTL-HqRdtFS7VoYht2NIauZ7msfnRWZpFuZD-60QObr; "
    "isg=BLy8wpxJ-eE_U81R8EveOIntjVputWDf_V89pJY9yKeLYVzrvsUwbzJXQYkZKZg3"
)

def build_data_str(page: int) -> str:
    """根据页码生成 DATA_STR（保持其他参数不变）"""
    base = (
        '{"appId":"43356","params":"{\\"device\\":\\"HMA-AL00\\",\\"isBeta\\":\\"false\\",'
        '\\"grayHair\\":\\"false\\",\\"from\\":\\"nt_history\\",\\"brand\\":\\"HUAWEI\\",'
        '\\"info\\":\\"wifi\\",\\"index\\":\\"4\\",\\"rainbow\\":\\"\\",'
        '\\"schemaType\\":\\"auction\\",\\"elderHome\\":\\"false\\",'
        '\\"isEnterSrpSearch\\":\\"true\\",\\"newSearch\\":\\"false\\",'
        '\\"network\\":\\"wifi\\",\\"subtype\\":\\"\\",\\"hasPreposeFilter\\":\\"false\\",'
        '\\"prepositionVersion\\":\\"v2\\",\\"client_os\\":\\"Android\\",'
        '\\"gpsEnabled\\":\\"false\\",\\"searchDoorFrom\\":\\"srp\\",'
        '\\"debug_rerankNewOpenCard\\":\\"false\\",\\"homePageVersion\\":\\"v7\\",'
        '\\"searchElderHomeOpen\\":\\"false\\",\\"search_action\\":\\"initiative\\",'
        '\\"sugg\\":\\"_4_1\\",\\"sversion\\":\\"13.6\\",\\"style\\":\\"list\\",'
        '\\"ttid\\":\\"600000@taobao_pc_10.7.0\\",\\"needTabs\\":\\"true\\",'
        '\\"areaCode\\":\\"CN\\",\\"vm\\":\\"nw\\",\\"countryNum\\":\\"156\\",'
        '\\"m\\":\\"pc_sem\\",\\"page\\":\\"PAGE_PLACEHOLDER\\",\\"n\\":48,\\"q\\":\\"%E6%89%8B%E6%9C%BA\\",'
        '\\"qSource\\":\\"url\\",\\"pageSource\\":\\"tbpc.pc_sem_alimama/a.search_history.d1\\",'
        '\\"tab\\":\\"all\\",\\"pageSize\\":48,\\"totalPage\\":100,\\"totalResults\\":4800,'
        '\\"sourceS\\":\\"0\\",\\"sort\\":\\"_coefp\\",\\"bcoffset\\":\\"\\",\\"ntoffset\\":\\"\\",'
        '\\"filterTag\\":\\"\\",\\"service\\":\\"\\",\\"prop\\":\\"\\",\\"loc\\":\\"\\",'
        '\\"start_price\\":null,\\"end_price\\":null,\\"startPrice\\":null,\\"endPrice\\":null,'
        '\\"itemIds\\":null,\\"p4pIds\\":null,\\"categoryp\\":\\"\\",'
        '\\"myCNA\\":\\"ZaTJIUMEym4BASQOBFu0d0OC\\",'
        '\\"clk1\\":\\"338f7cca440c87847e0428fc08531923\\",'
        '\\"refpid\\":\\"mm_26632258_3504122_32538762\\"}"}'
    )
    return base.replace('PAGE_PLACEHOLDER', str(page))

# ======================== 第三步：工具函数 ========================
def extract_token_from_cookie(cookie: str) -> str:
    try:
        tk_part = [item.strip() for item in cookie.split(';') if '_m_h5_tk=' in item][0]
        token = tk_part.split('=')[1].split('_')[0]
        return token
    except IndexError:
        raise ValueError("Cookie中未找到_m_h5_tk字段")

def decompress_response(resp: requests.Response) -> str:
    content_encoding = resp.headers.get('Content-Encoding', '').lower()
    content = resp.content
    try:
        if content_encoding == 'zstd':
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(content, max_output_size=10*1024*1024).decode('utf-8')
        elif content_encoding == 'br':
            return brotli.decompress(content).decode('utf-8')
        elif content_encoding == 'gzip':
            with gzip.GzipFile(fileobj=BytesIO(content)) as f:
                return f.read().decode('utf-8')
        else:
            return resp.text
    except Exception as e:
        return resp.text

def parse_jsonp_dynamic(jsonp_str: str) -> Union[Dict[str, Any], str]:
    """解析JSONP，自动去除首尾空白"""
    try:
        jsonp_str = jsonp_str.strip()
        pattern = re.compile(r'^mtopjsonp\d+\((.*)\)$', re.DOTALL)
        match = pattern.search(jsonp_str)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        else:
            return json.loads(jsonp_str)
    except Exception as e:
        print(f"JSONP解析失败: {e}")
        return jsonp_str

def save_to_csv(products, filename=None):
    """保存商品数据到CSV"""
    if not products:
        print("⚠️ 没有商品数据可保存")
        return
    if not filename:
        timestamp = int(time.time())
        filename = f"taobao_products_{timestamp}.csv"
    try:
        fieldnames = ['商品ID', '商品标题', '价格', '店铺名称', '店铺标签',
                      '销量', '产地', '是否促销', '秒杀信息', '商品链接']
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            written = 0
            for p in products:
                row = {
                    '商品ID': p['item_id'],
                    '商品标题': p['title'],
                    '价格': p['price'],
                    '店铺名称': p['shop_name'],
                    '店铺标签': p['shop_tag'],
                    '销量': p['real_sales'],
                    '产地': p['procity'],
                    '是否促销': '是' if p['is_promotion'] else '否',
                    '秒杀信息': p['second_kill_text'],
                    '商品链接': p['product_url'][:200]
                }
                writer.writerow(row)
                written += 1
            print(f"✅ 已写入 {written} 行商品数据到 {filename}")
        return filename
    except Exception as e:
        print(f"❌ 保存CSV文件时出错：{str(e)}")
        return None

# ======================== 第四步：主逻辑（多页，20页） ========================
if __name__ == "__main__":
    # 配置抓取参数
    MAX_PAGES = 20          # 改为20页
    DELAY_SECONDS = 2        # 请求间隔，避免被封

    headers = {
        "authority": "h5api.m.taobao.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "cookie": COOKIE,
        "pragma": "no-cache",
        "referer": "https://uland.taobao.com/sem/tbsearch?_input_charset=utf-8&bc_fl_src=tbsite_NOX36458&bd_vid=10221894582388341429&channelSrp=baiduSomama&clk1=661af1010d5122b2ba1961a60e144833&commend=all&ie=utf8&initiative_id=tbindexz_20170306&keyword=%E8%93%9D%E7%89%99%E8%80%B3%E6%9C%BA&localImgKey=&page=2&preLoadOrigin=https%3A%2F%2Fwww.taobao.com&q=%E8%93%9D%E7%89%99%E8%80%B3%E6%9C%BA&refpid=mm_26632258_3504122_32538762&search_type=item&source=suggest&sourceId=tb.index&spm=tbpc.pc_sem_alimama%2Fa.search_history.d1&ssid=s5-e&suggest_query=&tab=all&wq=",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    base_url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"

    try:
        token = extract_token_from_cookie(COOKIE)
        print(f"✅ 提取到 token: {token}")
    except ValueError as e:
        print(f"❌ Token提取失败：{e}")
        exit(1)

    all_products = []

    for page in range(1, MAX_PAGES + 1):
        print(f"\n========== 正在抓取第 {page} 页 ==========")
        data_str = build_data_str(page)

        timestamp = int(time.time() * 1000)
        sign_raw = f"{token}&{timestamp}&12574478&{data_str}"
        sign = hashlib.md5(sign_raw.encode('utf-8')).hexdigest()

        params = {
            "jsv": "2.7.2",
            "appKey": "12574478",
            "t": timestamp,
            "sign": sign,
            "api": "mtop.relationrecommend.wirelessrecommend.recommend",
            "v": "2.0",
            "type": "jsonp",
            "dataType": "jsonp",
            "callback": "mtopjsonp3",
            "data": data_str
        }

        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            print(f"✅ 请求成功 - 状态码：{response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 第 {page} 页请求失败：{e}")
            break

        response_text = decompress_response(response)
        final_data = parse_jsonp_dynamic(response_text)

        if not isinstance(final_data, dict):
            print(f"⚠️ 第 {page} 页数据格式异常，停止抓取")
            break

        # 核心：纯中括号索引获取商品列表
        try:
            data_section = final_data['data']
            items_array = data_section['itemsArray']
        except KeyError:
            print("❌ 未找到 data 或 itemsArray 字段，停止抓取")
            break

        if not items_array:
            print("✅ 已无更多商品，停止翻页")
            break

        print(f"🔍 本页获取到 {len(items_array)} 个商品")

        page_sales_count = 0
        for idx, item in enumerate(items_array):
            if not isinstance(item, dict):
                continue

            # 初始化默认值
            real_sales = ""
            shop_name = ""
            second_kill_text = ""

            # 1. 纯中括号获取店铺名称
            try:
                shop_info = item['shopInfo']
                shop_name = shop_info['title']
            except KeyError:
                shop_name = ""

            # 2. 纯中括号获取秒杀信息
            try:
                second_kill_info = item['secondKillInfo']
                second_kill_text = second_kill_info['text3']
            except KeyError:
                second_kill_text = ""

            # 3. 核心：纯中括号获取realSales
            try:
                real_sales = item['realSales']
                page_sales_count += 1
                # 可以选择打印部分销量，避免刷屏
                if len(all_products) < 10:
                    print(f"   ✅ 商品 {item['item_id']} 销量: {real_sales}")
            except KeyError:
                # 如果顶层没有，尝试嵌套索引
                try:
                    ut_log_map = item['utLogMap']
                    real_sales = ut_log_map['realSales']
                    page_sales_count += 1
                    if len(all_products) < 10:
                        print(f"   ✅ 商品 {item['item_id']} 销量(utLogMap): {real_sales}")
                except KeyError:
                    try:
                        extra_params = item['extraParams']
                        for param in extra_params:
                            if 'realSales' in param:
                                real_sales = param['realSales']
                                page_sales_count += 1
                                if len(all_products) < 10:
                                    print(f"   ✅ 商品 {item['item_id']} 销量(extraParams): {real_sales}")
                                break
                    except KeyError:
                        real_sales = ""
                        # 可选打印缺失信息，但为避免刷屏，可注释
                        # print(f"   ❌ 商品 {item.get('item_id', '未知')} 未找到 realSales 字段")

            # 构建商品字典
            product = {
                'item_id': item['item_id'] if 'item_id' in item else "",
                'title': re.sub(r'<[^>]+>', '', item['title']) if 'title' in item else "",
                'price': item['price'] if 'price' in item else "",
                'shop_name': shop_name,
                'shop_tag': item['shopTag'] if 'shopTag' in item else "",
                'real_sales': real_sales,
                'procity': item['procity'] if 'procity' in item else "",
                'is_promotion': str(item['isP4p']).lower() == 'true' if 'isP4p' in item else False,
                'second_kill_text': second_kill_text,
                'product_url': item['auctionURL'] if 'auctionURL' in item else (item['productUrl'] if 'productUrl' in item else "")
            }
            all_products.append(product)

        print(f"📊 本页有销量信息的商品数: {page_sales_count} / {len(items_array)}")

        if page < MAX_PAGES:
            print(f"⏳ 等待 {DELAY_SECONDS} 秒后继续下一页...")
            time.sleep(DELAY_SECONDS)

    print(f"\n📦 共抓取 {len(all_products)} 个商品（{min(page, MAX_PAGES)} 页）")
    if all_products:
        # 显示前3个有销量的商品信息
        print("\n📋 前3个有销量的商品信息：")
        sales_products = [p for p in all_products if p['real_sales']]
        for i, p in enumerate(sales_products[:3]):
            print(f"\n【商品 {i+1}】")
            print(f"标题: {p['title'][:50]}...")
            print(f"价格: ¥{p['price']}")
            print(f"店铺: {p['shop_name']}")
            print(f"销量: {p['real_sales']}")
            print(f"店铺标签: {p['shop_tag']}")
            print("-" * 40)

        # 保存到CSV
        filename = f"taobao_products_{int(time.time())}.csv"
        save_to_csv(all_products, filename)

        # 最终统计
        sales_count = sum(1 for p in all_products if p['real_sales'])
        print(f"\n📈 有销量信息的商品: {sales_count} 个 ({sales_count/len(all_products)*100:.1f}%)")

        price_list = []
        for p in all_products:
            try:
                price = float(p['price']) if p['price'] else None
                if price is not None:
                    price_list.append(price)
            except:
                pass
        if price_list:
            print(f"📊 价格统计：")
            print(f"  平均价格: ¥{sum(price_list)/len(price_list):.2f}")
            print(f"  最低价格: ¥{min(price_list):.2f}")
            print(f"  最高价格: ¥{max(price_list):.2f}")

        promo_count = sum(1 for p in all_products if p['is_promotion'])
        print(f"📈 促销商品: {promo_count}个 ({promo_count/len(all_products)*100:.1f}%)")
        second_kill_count = sum(1 for p in all_products if p['second_kill_text'])
        print(f"⏰ 秒杀商品: {second_kill_count}个")
    else:
        print("⚠️ 未提取到任何商品，请检查Cookie或接口。")

    print("\n🎉 程序执行完成！")