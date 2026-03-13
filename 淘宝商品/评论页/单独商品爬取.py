import requests
import pandas as pd
import json
import time
import hashlib
import gzip
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 忽略SSL警告（避免冗余输出）
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ============ 1. 核心配置（按需修改） ============
ITEM_ID = "1010969056730"  # 目标商品ID
YOUR_COOKIE = 'wk_cookie2=13b6e243aa04733a0ddc226b9e6c5883; cna=MDEOIhjI5B0CAXjzW65/vFGP; xlly_s=1; lid=tb356880569; wk_unb=UUpgR1XLzzmCjrJdeA%3D%3D; isg=BMLCudPWHzN-aQODiiYoc52AE8gkk8atZ5Hz1gzb7jXgX2LZ9CMWvUicD1sjRD5F; dnk=tb356880569; uc1=pas; uc3=nk2; tracknick=tb356880569; _l_g_=Ug%3D%3D; uc4=id4; havana_lgc_exp=1804305857831; unb=2211732220148; lgc=tb356880569; cookie1=W8ty8J4rxuJ19CR1aYsIW1OHZvGQuzmKHm3xBUuGSZ0%3D; login=true; cookie17=UUpgR1XLzzmCjrJdeA%3D%3D; cookie2=1e8c563faa59f5c82ae148dee363c5df; _nk_=tb356880569; sgcookie=E100byYzxHbNo5N2fQsiuAXL4EXq7E4io%2FpW0zAV6QCzjmR%2FHmnAz0w0EeHAYcM%2By9jvIHyCnhkiRlxs05g1%2FguqkiKgiFuVuBTjcVJkDBRC2pLMDznQl%2BNfGl%2FmButmNZMX; cancelledSubSites=empty; sg=98b; t=8bdcaeeae773cfa99a65af6b0516ae31; csg=f259d30b; sn=; _tb_token_=e363f31b8913b; mtop_partitioned_detect=1; _m_h5_tk=4ea0f85b119f7d30e2e103d481bf9de4_1773212381829; _m_h5_tk_enc=887e8af03324d9a8d22d3370c89c922d; tfstk=gt4rezO_naQyGR6g_50F7ZnFpM0-D2W1ayMItWVnNYDlp_hn88wmxeN5265E3JHSV4qSteyjhJTQNyrv85FLP_3Cw4F-J2X1CNgUw73dZeQ6JzJDifPmtpDlcqb3O9vcCN__wgc-RSX_VVXy0Xcn-bDoxSfqNbcn-DcuislnOLxHrJVcgxhyZ3cnxZAmsXgnKJ0hgqcIZ2cuK0f4ixhn-vcRd209CfmlZ9hAInT5Z0DgZx8H7ChrqBNDAeTCibmrImXy8e--a0kgZxWyeQCsmWnUJBLEj7qTpf2kE9kLuS4ujRXXVYqZT5ZUZaYmPzFujD4GpH2ZzJogrmRhT7NoLql0S6tthrk7Kzoc1FoIoPiirosAFDgr_J48UB83ISN_ymUFQKDLVf3mTyCMYvoh47pKiiauJuJHY0cxgA1VgBvzYb0zEgdJvHnJMjk1wDxpv0cxgA1VgHKK2IhqC_nh.'

START_PAGE = 1  # 起始页码
PAGE_COUNT = 20  # 要爬取的总页数（每页20条左右）
DELAY = 3  # 每页请求间隔（秒，防反爬，建议3-5）


def decompress_response(raw_content):
    try:

        return raw_content.decode('utf-8')
    except UnicodeDecodeError:

        return gzip.decompress(raw_content).decode('utf-8')


def extract_comments_from_response(response_text):

    if 'mtopjsonp' not in response_text:
        return [], "响应格式错误，未找到mtopjsonp标记"

    # 提取JSONP中的核心JSON
    start = response_text.find('(') + 1
    end = response_text.rfind(')')
    json_str = response_text[start:end]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return [], "JSON解析失败"

    # 检查接口返回状态
    ret_status = data.get('ret', ['SUCCESS'])
    if 'FAIL' in str(ret_status[0]):
        return [], f"接口返回失败: {ret_status[0]}"

    # 提取评论列表（兼容两种字段路径）
    rate_detail = data.get('data', {}).get('rateDetail', {})
    comments_list = rate_detail.get('rateList', [])
    if not comments_list:
        comments_list = data.get('data', {}).get('rateList', [])

    # 整理评论数据
    parsed_comments = []
    for comment in comments_list:
        parsed_comments.append({
            '评分': comment.get('rateType', ''),
            '评论内容': comment.get('feedback') or '',
            '评论时间': comment.get('rateDate') or comment.get('feedbackDate') or '',
            '商品规格': comment.get('skuMap', '')  # 新增：商品规格
        })
    return parsed_comments, "成功"


# ============ 3. 主逻辑（多页爬取） ============
if __name__ == "__main__":
    print(f"===== 开始爬取商品 {ITEM_ID} 的评论（共{PAGE_COUNT}页）=====")

    # 第一步：提取签名Token
    token_part = None
    for item in YOUR_COOKIE.split('; '):
        if item.startswith('_m_h5_tk='):
            token_part = item.split('=')[1]
            break

    if token_part is None:
        print("错误：Cookie中未找到_m_h5_tk，请检查Cookie是否正确！")
        exit()
    token = token_part.split('_')[0]
    print(f"✅ 提取到签名Token: {token[:10]}...\n")

    # 第二步：循环爬取每页
    all_comments = []  # 汇总所有页的评论
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'cookie': YOUR_COOKIE,
        'referer': f'https://detail.tmall.com/item.htm?id={ITEM_ID}',
        'accept-encoding': 'gzip, deflate, br'
    }
    base_url = 'https://h5api.m.tmall.com/h5/mtop.taobao.rate.detaillist.get/6.0/'

    for current_page in range(START_PAGE, START_PAGE + PAGE_COUNT):
        print(f"----- 处理第 {current_page} 页 -----")

        # 生成当前页的动态参数
        current_timestamp = str(int(time.time() * 1000))
        request_data = {
            "auctionNumId": ITEM_ID,
            "pageNo": current_page,  # 关键：当前页码
            "pageSize": 20,
            "orderType": "",
            "searchImpr": "-8",
            "expression": "",
            "skuVids": "",
            "rateSrc": "pc_rate_list",
            "rateType": ""
        }
        data_string = json.dumps(request_data, separators=(',', ':'))


        sign_str = f"{token}&{current_timestamp}&12574478&{data_string}"
        signature = hashlib.md5(sign_str.encode()).hexdigest()

        # 构建请求参数
        params = {
            "jsv": "2.7.5",
            "appKey": "12574478",
            "t": current_timestamp,
            "sign": signature,
            "api": "mtop.taobao.rate.detaillist.get",
            "v": "6.0",
            "dataType": "jsonp",
            "type": "jsonp",
            "callback": f"mtopjsonp{current_page + 19}",  # 动态callback
            "data": data_string
        }

        # 发送请求并处理
        try:
            response = requests.get(
                base_url,
                headers=headers,
                params=params,
                timeout=15,
                verify=False  # 忽略SSL验证
            )
            print(f"请求状态码: {response.status_code}")

            # 解压响应
            response_text = decompress_response(response.content)
            print(f"响应预览: {response_text[:200]}")

            # 提取评论
            page_comments, msg = extract_comments_from_response(response_text)
            print(f"提取结果: {msg} | 本页评论数: {len(page_comments)}")

            # 汇总数据
            if page_comments:
                all_comments.extend(page_comments)

            # 防反爬延迟（最后一页不延迟）
            if current_page < START_PAGE + PAGE_COUNT - 1:
                print(f"等待 {DELAY} 秒后继续...\n")
                time.sleep(DELAY)

        except requests.exceptions.Timeout:
            print(f"❌ 第{current_page}页请求超时，跳过该页\n")
            continue
        except Exception as e:
            print(f"❌ 第{current_page}页处理异常: {str(e)[:100]}\n")
            continue

    # 第三步：保存汇总数据
    print("\n===== 爬取完成，开始保存数据 =====")
    if all_comments:
        df = pd.DataFrame(all_comments)
        # 生成带时间戳的文件名（避免覆盖）
        filename = '商品评论数据/商品10.csv'
        # UTF-8带BOM，兼容Excel
        df.to_csv(filename, index=False, encoding='utf-8-sig')

        print(f"✅ 数据已保存到: {filename}")
        print(f"📊 总计提取 {len(df)} 条有效评论")
        print("\n📌 前5条数据预览:")
        print(df[['页码', '用户名', '评论内容']].head().to_string(index=False))
    else:
        print("❌ 未提取到任何评论数据！")
        print("可能原因：1) Cookie过期 2) 商品无评论 3) 接口风控拦截")

    print("\n程序执行结束。")