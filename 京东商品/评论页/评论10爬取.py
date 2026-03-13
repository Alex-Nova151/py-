from DrissionPage import ChromiumPage
import time
import re
import csv
import os
from fake_useragent import UserAgent



# ==================== 核心配置 ====================
# 1. 定义你要采集的商品详情页URL列表（替换为你的20个商品链接）
PRODUCT_URLS = [
    'https://item.jd.com/100129016845.html',  # 商品1
    'https://item.jd.com/100182833355.html',  # 商品2
    'https://item.jd.com/10150117226424.html',  # 商品3
    'https://item.jd.com/100129016839.html',  # 商品4
    'https://item.jd.com/100191176323.html',  # 商品5
    'https://item.jd.com/100201589726.html',  # 商品6
    'https://item.jd.com/100157830512.html',  # 商品7
    'https://item.jd.com/100201589726.html',  # 商品8
    'https://item.jd.com/100248102668.html',  # 商品9
    'https://item.jd.com/100248102670.html',  # 商品10
    'https://item.jd.com/100248102702.html',  # 商品11
    'https://item.jd.com/100189191001.html',  # 商品12
    'https://item.jd.com/100248102688.html',  # 商品13
    'https://item.jd.com/100106087181.html',  # 商品14
    'https://item.jd.com/100162469372.html',  # 商品15
    'https://item.jd.com/100162469378.html',  # 商品16
    'https://item.jd.com/100162425498.html',  # 商品17
    'https://item.jd.com/100143837568.html',  # 商品18
    'https://item.jd.com/100215674663.html',  # 商品19
    'https://item.jd.com/10191502918974.html',  # 商品20
]

# 2. 创建保存CSV的新文件夹（不存在则自动创建）
SAVE_FOLDER = '商品评论数据'
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ==================== 初始化浏览器 ====================
dp = ChromiumPage()
dp.listen.start('client.action')  # 启动监听

# ==================== 批量采集每个商品的评论 ====================
for idx, product_url in enumerate(PRODUCT_URLS, start=1):
    """
    idx: 商品序号（1-20）
    product_url: 商品详情页URL
    """
    print(f'\n========== 开始采集第{idx}个商品 ==========')
    print(f'商品链接：{product_url}')

    # 定义当前商品的CSV文件路径（保存到新文件夹，命名为 商品1.csv、商品2.csv...）
    csv_file_path = os.path.join(SAVE_FOLDER, f'商品{idx}.csv')

    # 初始化CSV文件并写入表头
    f = open(csv_file_path, mode='w', encoding='utf-8', newline='')
    csv_writer = csv.DictWriter(f, fieldnames=['评论', '分数', '产品', '名字'])
    csv_writer.writeheader()

    try:
        # 打开商品详情页
        dp.get(product_url)
        time.sleep(3)  # 等待页面加载完成（延长等待时间，避免加载不完整）

        # 滚动到"全部评价"并点击
        dp.scroll.to_see('全部评价')
        time.sleep(1)
        dp.ele('text=全部评价').click()
        time.sleep(2)

        # 采集20页评论（和你原代码一致）
        for page in range(1, 21):
            print(f'  正在采集第{idx}个商品的第{page}页评论')
            time.sleep(2)

            # 等待监听的响应数据
            resp = dp.listen.wait(timeout=10)  # 增加超时，避免卡死
            json_data = resp.response.body

            # 解析评论数据（兼容不同的JSON结构，增加异常捕获）
            try:
                # 适配京东评论接口的JSON结构（你原代码的解析路径）
                datas = json_data['result']['floors'][2]['data']
                for data in datas:
                    try:
                        dit = {
                            '评论': data['commentInfo']['commentData'],
                            '分数': data['commentInfo']['commentScore'],
                            '产品': data['commentInfo']['productSpecifications'],
                            '名字': data['commentInfo']['userNickName']
                        }
                        csv_writer.writerow(dit)
                        # print(dit)  # 如需打印每条评论，取消注释
                    except Exception as e:
                        # 跳过解析失败的单条评论
                        continue
            except Exception as e:
                print(f'    第{page}页数据解析失败：{e}')
                continue

            # 滚动到评论区底部，准备下一页
            tab = dp.ele('css:._rateListContainer_1ygkr_45', timeout=5)
            if tab:
                tab.scroll.to_bottom()
            time.sleep(1)

        print(f'第{idx}个商品采集完成！CSV文件已保存：{csv_file_path}')

    except Exception as e:
        print(f'第{idx}个商品采集出错：{e}')
    finally:
        # 确保文件关闭
        f.close()

# 关闭浏览器
dp.quit()
print('\n所有商品采集完成！所有CSV文件已保存到：', SAVE_FOLDER)