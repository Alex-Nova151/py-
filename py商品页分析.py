# ===================== 商品页简化分析（价格+销量，适配销量含+/万格式，字段名：价格） =====================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr
import os
import re

# ===================== 1. 路径配置 =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 替换为你的真实文件名
JD_PRODUCT_FILE = "商品页.csv"
VIP_PRODUCT_FILE = "唯品会手机商品.csv"
TB_PRODUCT_FILE = "taobao_products_1773062993.csv"

# 路径拼接
JD_PRODUCT_PATH = os.path.join(BASE_DIR, "京东商品", "商品页", JD_PRODUCT_FILE)
VIP_PRODUCT_PATH = os.path.join(BASE_DIR, "唯品会商品", "商品页", VIP_PRODUCT_FILE)
TB_PRODUCT_PATH = os.path.join(BASE_DIR, "淘宝商品", "商品页", TB_PRODUCT_FILE)

# 结果保存路径
OUTPUT_FOLDER = os.path.join(BASE_DIR, "数据分析")
CHART_FOLDER = os.path.join(OUTPUT_FOLDER, "商品页简化分析图表")
os.makedirs(CHART_FOLDER, exist_ok=True)

# 手机价格带配置
PHONE_PRICE_BANDS = {
    0: "0-1000元（入门机）",
    1000: "1000-2000元（千元机）",
    2000: "2000-3000元（中端机）",
    3000: "3000-4000元（中高端）",
    4000: "4000元以上（旗舰机）"
}


# ===================== 2. 销量格式转换核心函数 =====================
def convert_sales_to_number(sales_str):
    """
    转换销量文本为数字：
    - 处理 1000+ → 1000
    - 处理 1.2万 → 12000、1万+ → 10000
    - 处理纯数字/空值 → 原样转换/返回NaN
    """
    if pd.isna(sales_str):
        return pd.NA

    # 转为字符串并去除空格
    sales_str = str(sales_str).strip()

    # 提取数字部分（兼容中文数字、小数点、万）
    # 匹配规则：包含数字、小数点、万的组合
    match = re.search(r'(\d+\.?\d*)(万)?', sales_str)
    if not match:
        return pd.NA  # 无有效数字

    num_part = match.group(1)
    unit = match.group(2)  # 单位是否为"万"

    # 转为浮点数
    try:
        num = float(num_part)
    except:
        return pd.NA

    # 处理万单位
    if unit == "万":
        num *= 10000

    # 去除"+"后，取整（销量为整数）
    return int(num)


# ===================== 3. 读取并清洗数据 =====================
def load_single_product_data(file_path, platform_name):
    """读取单个平台数据，清洗销量字段"""
    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="gbk")
    except Exception as e:
        print(f"❌ 读取{platform_name}商品数据失败：{e}")
        return pd.DataFrame()

    # 检查价格字段是否存在
    if "价格" not in df.columns:
        print(f"❌ {platform_name}数据缺少'价格'字段，无法进行价格分析")
        return pd.DataFrame()

    # 清洗销量字段
    if "销量" in df.columns:
        # 保存原始销量，便于核对
        df["销量_原始"] = df["销量"]
        # 转换销量为数字
        df["销量"] = df["销量"].apply(convert_sales_to_number)
        # 过滤无效销量（非数字/≤0）
        valid_sales_count = df["销量"].notna().sum()
        print(f"⚠️ {platform_name}销量转换：有效数据{valid_sales_count}条 / 总数据{len(df)}条")
    else:
        print(f"⚠️ {platform_name}无销量字段，仅保留价格分析")

    df["平台"] = platform_name
    print(f"✅ {platform_name}商品数据加载完成：{len(df)}条")
    return df


# 读取三大平台
df_jd = load_single_product_data(JD_PRODUCT_PATH, "京东")
df_vip = load_single_product_data(VIP_PRODUCT_PATH, "唯品会")
df_tb = load_single_product_data(TB_PRODUCT_PATH, "淘宝")


# 合并数据
def merge_products():
    all_dfs = []
    for df in [df_jd, df_vip, df_tb]:
        if len(df) > 0:
            all_dfs.append(df)

    if not all_dfs:
        print("❌ 无商品数据可合并！")
        return pd.DataFrame(), pd.DataFrame()

    # 全量数据（用于价格分析）
    df_all = pd.concat(all_dfs, ignore_index=True)
    # 仅含有效销量的数据（用于销量分析）
    df_all_with_sales = df_all[
        df_all["销量"].notna() & (df_all["销量"] > 0)
        ].copy()

    print(f"\n✅ 数据合并完成：")
    print(f"- 总商品数：{len(df_all)}条")
    print(f"- 有效销量商品数：{len(df_all_with_sales)}条")
    return df_all, df_all_with_sales


df_all_products, df_all_with_sales = merge_products()


# ===================== 4. 价格带分析（核心） =====================
def analyze_price_band(df):
    if df.empty:
        print("❌ 无数据，跳过价格带分析")
        return

    # 仅处理有效价格数据
    df_valid_price = df[
        df["价格"].notna() & (df["价格"] > 0)
        ].copy()
    if df_valid_price.empty:
        print("❌ 无有效价格数据，跳过价格带分析")
        return

    # 划分价格带
    def get_band(price):
        for threshold in sorted(PHONE_PRICE_BANDS.keys()):
            if price < threshold:
                return PHONE_PRICE_BANDS[threshold]
        return PHONE_PRICE_BANDS[4000]

    df_valid_price["价格带"] = df_valid_price["价格"].apply(get_band)

    # 统计价格带商品数量
    price_stats = df_valid_price.groupby("价格带").agg({
        "商品ID": "count"
    }).reset_index()
    price_stats.columns = ["价格带", "商品数"]
    price_stats["商品占比(%)"] = price_stats["商品数"] / price_stats["商品数"].sum() * 100

    # 可视化：价格带商品分布
    fig1 = px.pie(
        price_stats,
        values="商品占比(%)",
        names="价格带",
        title="手机品类价格带商品数量分布",
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig1.write_html(os.path.join(CHART_FOLDER, "01_价格带商品分布.html"))

    # 有销量时补充销量分析
    if "销量" in df_valid_price.columns and len(df_all_with_sales) > 0:
        price_sales_stats = df_valid_price.groupby("价格带").agg({
            "销量": "sum",
            "商品ID": "count"
        }).reset_index()
        price_sales_stats.columns = ["价格带", "总销量", "商品数"]
        price_sales_stats["单商品平均销量"] = price_sales_stats["总销量"] / price_sales_stats["商品数"]
        price_sales_stats["销量占比(%)"] = price_sales_stats["总销量"] / price_sales_stats["总销量"].sum() * 100

        # 可视化：价格带销量分析
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Bar(x=price_sales_stats["价格带"], y=price_sales_stats["总销量"], name="总销量"),
            secondary_y=False
        )
        fig2.add_trace(
            go.Line(x=price_sales_stats["价格带"], y=price_sales_stats["单商品平均销量"], name="单商品平均销量",
                    marker_color="red"),
            secondary_y=True
        )
        fig2.update_layout(title="价格带销量分析（已转换销量格式）")
        fig2.write_html(os.path.join(CHART_FOLDER, "02_价格带销量分析.html"))

        print(f"\n📝 价格带销量结论：")
        print(f"- 销量最高价格带：{price_sales_stats.loc[price_sales_stats['总销量'].idxmax(), '价格带']}")
        print(f"- 单商品销量最高：{price_sales_stats.loc[price_sales_stats['单商品平均销量'].idxmax(), '价格带']}")
    else:
        print(f"\n📝 价格带商品结论：")
        print(
            f"- 商品数量最多：{price_stats.loc[price_stats['商品数'].idxmax(), '价格带']}（占比{price_stats['商品占比(%)'].max():.1f}%）")


# ===================== 5. 销量相关分析 =====================
def analyze_sales(df):
    if df.empty:
        print("❌ 无有效销量数据，跳过销量分析")
        return

    # 1. 平台销量对比
    platform_sales = df.groupby("平台").agg({
        "销量": "sum",
        "商品ID": "count"
    }).reset_index()
    platform_sales.columns = ["平台", "总销量", "商品数"]

    # 可视化：平台销量对比
    fig = px.bar(
        platform_sales,
        x="平台",
        y="总销量",
        title="各平台手机销量对比（已转换销量格式）",
        color="平台",
        color_discrete_map={"京东": "red", "淘宝": "orange", "唯品会": "purple"}
    )
    fig.write_html(os.path.join(CHART_FOLDER, "03_平台销量对比.html"))

    # 2. 价格与销量相关性
    corr_data = df[["价格", "销量"]].dropna()  # 修正：商品价格 → 价格
    if len(corr_data) < 2:
        print("❌ 有效数据不足，跳过价格-销量相关性分析")
        return

    corr, _ = pearsonr(corr_data["价格"], corr_data["销量"])  # 修正：商品价格 → 价格
    # 可视化：价格vs销量散点图
    sample_data = corr_data.sample(min(1000, len(corr_data)))
    fig2 = px.scatter(
        sample_data,
        x="价格",  # 修正：商品价格 → 价格
        y="销量",
        trendline="ols",
        title=f"手机价格 vs 销量（相关系数：{corr:.2f}）",
        opacity=0.6
    )
    fig2.write_html(os.path.join(CHART_FOLDER, "04_价格销量相关性.html"))

    print(f"\n📝 销量分析结论：")
    print(
        f"- 销量最高平台：{platform_sales.loc[platform_sales['总销量'].idxmax(), '平台']}（总销量{platform_sales['总销量'].max():,}）")
    print(f"- 价格-销量相关系数：{corr:.2f}（>0正相关，<0负相关）")


# ===================== 6. 执行分析 =====================
if __name__ == "__main__":
    print("========== 开始商品页分析（适配销量+/万格式，字段名：价格） ==========")
    analyze_price_band(df_all_products)
    analyze_sales(df_all_with_sales)
    print(f"\n🎉 分析完成！图表保存至：{CHART_FOLDER}")