import pandas as pd
import re


def clean_product_data():
    """
    商品数据深度清洗核心函数
    核心逻辑：删除销量空值 + 去重 + 基础格式规整
    """
    # ===================== 1. 读取原始数据 =====================
    # 读取CSV（路径：脚本上一级目录的data1.csv）
    df = pd.read_csv('商品页.csv')
    print("=" * 50)
    print("原始数据基础信息：")
    print(f"原始数据总行数：{len(df)}")
    print(f"销量列空值数量：{df['销量'].isna().sum()}")
    print(f"完全重复行数量：{df.duplicated().sum()}")
    print("=" * 50)

    # ===================== 2. 核心清洗步骤 =====================
    # 2.1 删除销量列为空/NaN的行（你的核心需求）
    df = df[df['销量'].notna()]

    # 2.2 删除完全重复的行（Day3要求：去重，不删细粒度差异行）
    df = df.drop_duplicates()

    # 2.3 统一数据格式（可选，适配Day3“格式统一”要求）
    # 2.3.1 价格列清洗：去除非数字字符，转浮点数（示例，根据你的列名调整）
    if '原价' in df.columns:
        df['原价'] = df['原价'].apply(
            lambda x: float(re.sub(r'[^\d.]', '', str(x))) if pd.notna(x) else 0.0
        )

    # 2.3.2 重置索引（避免清洗后索引混乱）
    df = df.reset_index(drop=True)

    # ===================== 3. 清洗结果验证 =====================
    print("\n清洗后数据基础信息：")
    print(f"删除空值+去重后行数：{len(df)}")
    print(f"剩余销量列空值数量：{df['销量'].isna().sum()}")
    print("\n清洗后销量列前20条示例：")
    print(df['销量'].head(20))
    print("=" * 50)

    # ===================== 4. 保存清洗后的数据 =====================
    # 保存到上一级目录，命名为cleaned_data1.csv（区分原始数据）
    df.to_csv('商品清洗数据.csv', index=False)
    print("✅ 清洗后的数据已保存为：../cleaned_data1.csv")

    return df


# 执行清洗函数
if __name__ == "__main__":
    cleaned_df = clean_product_data()