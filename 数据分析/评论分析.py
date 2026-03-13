# ===================== 评论页核心分析（最终版：强制精准负面词） =====================
import pandas as pd
import plotly.express as px
import os

# ===================== 1. 路径配置 =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "数据分析")  # 评论CSV所在文件夹
CHART_FOLDER = os.path.join(DATA_DIR, "评论页核心图表_最终版")
os.makedirs(CHART_FOLDER, exist_ok=True)

# --------------------------
# 【最终版】严格限定负面关键词（只认这些，其他一律不算负面）
# --------------------------
NEGATIVE_KEYWORDS = {
    # 性能/硬件问题
    "发热", "发烫", "过热", "烧手", "卡顿", "卡慢", "卡死", "死机", "重启", "闪退",
    "耗电快", "耗电", "掉电快", "续航差", "不耐用", "碎屏", "漏液", "花屏", "闪屏", "烧屏",
    "信号差", "无信号", "断网", "断流", "噪音大", "杂音", "破音",
    # 服务/物流问题
    "客服差", "不理人", "不回复", "推诿", "物流慢", "延迟", "不发货", "丢件",
    # 其他负面
    "假货", "翻新机", "二手", "故障", "坏了", "失灵"
}

# ===================== 2. 读取并预处理数据 =====================
def load_and_preprocess():
    all_dfs = []
    for file in os.listdir(DATA_DIR):
        if not file.endswith(".csv") or "评论" not in file:
            continue
        # 识别平台
        if "京东" in file:
            platform = "京东"
        elif "淘宝" in file:
            platform = "淘宝"
        elif "唯品会" in file:
            platform = "唯品会"
        else:
            platform = "未知平台"
        # 读取文件
        file_path = os.path.join(DATA_DIR, file)
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="gbk")
        # 统一列名
        df = df.rename(columns={"评论": "评论内容", "分数": "评分", "商品编号": "商品ID"})
        # 过滤空评论
        df = df[df["评论内容"].notna() & (df["评论内容"] != "")].copy()
        df["平台"] = platform
        # 生成商品ID（无则自动分配）
        if "商品ID" not in df.columns:
            df["商品ID"] = df.groupby("平台").cumcount() // 50 + 1
        # 生成【平台-商品】标识
        df["平台-商品"] = df["平台"] + "-商品" + df["商品ID"].astype(str)
        all_dfs.append(df)
        print(f"✅ 读取{platform}评论：{len(df)}条，商品数：{df['商品ID'].nunique()}")
    if not all_dfs:
        print("❌ 未找到评论数据！")
        return pd.DataFrame()
    df_all = pd.concat(all_dfs, ignore_index=True)
    print(f"\n✅ 合并完成：总评论{len(df_all)}条，涉及{df_all['平台-商品'].nunique()}个商品")
    return df_all

df_all = load_and_preprocess()

# ===================== 3. 图表1：完整好评率（所有有评论的商品） =====================
def plot_full_good_rate():
    if df_all.empty:
        return
    # 统计好评率
    good_rate_stats = []
    for product in df_all["平台-商品"].unique():
        product_df = df_all[df_all["平台-商品"] == product]
        total = len(product_df)
        if total < 1:
            continue
        if "评分" in product_df.columns:
            good = len(product_df[product_df["评分"] >= 4])
            good_rate = (good / total) * 100
        else:
            good = total
            good_rate = 100.0
        good_rate_stats.append({
            "平台-商品": product,
            "好评数": good,
            "总评论数": total,
            "好评率(%)": round(good_rate, 1)
        })
    df_good_rate = pd.DataFrame(good_rate_stats)
    # 按平台分组排序
    df_good_rate = df_good_rate.sort_values("平台-商品", ascending=True)
    # 生成条形图
    fig = px.bar(
        df_good_rate,
        x="平台-商品",
        y="好评率(%)",
        title="全平台所有商品好评率对比",
        color="好评率(%)",
        color_continuous_scale=px.colors.sequential.Greens,
        hover_data={"好评数": True, "总评论数": True}
    )
    # 优化可读性
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="平台-商品",
        yaxis_title="好评率(%)",
        yaxis_range=[0, 105],
        width=1600,
        height=700
    )
    fig.write_html(os.path.join(CHART_FOLDER, "01_全商品好评率.html"))
    print(f"📊 生成：01_全商品好评率.html")

# ===================== 4. 图表2：精准负面问题（只认预设词，无则跳过） =====================
def plot_strict_negative():
    if df_all.empty:
        print("❌ 无评论数据，跳过负面分析")
        return
    # 【严格版】只统计在 NEGATIVE_KEYWORDS 里的词
    negative_records = []
    for idx, row in df_all.iterrows():
        comment = str(row["评论内容"])
        product = row["平台-商品"]
        # 只匹配预设负面词
        found_neg_words = [kw for kw in NEGATIVE_KEYWORDS if kw in comment]
        if found_neg_words:
            for w in found_neg_words:
                negative_records.append({
                    "负面关键词": w,
                    "平台-商品": product
                })
    if not negative_records:
        print("⚠️ 未发现任何明确负面问题，跳过负面分析")
        return
    # 统计
    df_negative = pd.DataFrame(negative_records)
    negative_count = df_negative["负面关键词"].value_counts().reset_index()
    negative_count.columns = ["负面关键词", "出现次数"]
    # 生成图表
    fig = px.bar(
        negative_count,
        y="负面关键词",
        x="出现次数",
        orientation="h",
        title="全平台商品精准负面问题TOP10（仅含明确负面词）",
        color="出现次数",
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig.update_layout(width=900, height=600)
    fig.write_html(os.path.join(CHART_FOLDER, "02_精准负面问题.html"))
    print(f"📊 生成：02_精准负面问题.html")
    # 打印结果
    print("\n📝 明确负面问题TOP5：")
    for i, row in negative_count.head(5).iterrows():
        print(f"{i+1}. {row['负面关键词']}（出现{row['出现次数']}次）")

# ===================== 5. 执行分析 =====================
if __name__ == "__main__":
    print("========== 开始最终版评论分析 ==========")
    plot_full_good_rate()    # 好评率图表（保留）
    plot_strict_negative()    # 精准负面问题（只认预设词，无则跳过）
    print(f"\n🎉 最终版分析完成！图表保存在：{CHART_FOLDER}")