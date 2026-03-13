import pandas as pd
import re

# 假设你的原始数据已经读取到df中（比如从CSV/数据库读取）
df = pd.read_csv("商品清洗数据.csv")  # 或从数据库读取的df

# ========== 仅这一段：处理销量列（转数字）+ 降序排列 ==========
def clean_sales(sales_str):
    """专处理含“万”/“+”的销量，转为可排序的数字"""
    if pd.isna(sales_str):
        return 0
    sales_str = str(sales_str).strip().replace("+", "")
    # 核心：处理“万”单位
    if "万" in sales_str:
        num = re.findall(r'(\d+(?:\.\d+)?)', sales_str)
        return int(float(num[0]) * 10000) if num else 0
    # 处理纯数字
    return int(sales_str) if sales_str.isdigit() else 0

# 1. 新增销量数字列（核心操作：把“万”转成数字）
df['销量_数字'] = df['销量'].apply(clean_sales)

# 2. 按销量数字降序排列（核心操作：降序）
df_sorted = df.sort_values(by='销量_数字', ascending=False)
# ========== 核心操作结束 ==========

# 可选：查看结果（验证“万”是否正确转换+排序）
print(df_sorted[['销量', '销量_数字']].head(10))
df_sorted.to_csv("商品数据清洗2.csv", index=False,encoding='utf-8-sig')