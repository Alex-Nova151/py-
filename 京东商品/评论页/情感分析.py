import pandas as pd
from snownlp import SnowNLP
from collections import Counter
import jieba
import os
from pathlib import Path

# ===================== 核心配置（按需修改） =====================
PREPROCESS_FOLDER = "商品评论数据1"  # 预处理文件所在文件夹
MERGED_FILE = "合并后_所有评论预处理数据.csv"  # 合并大文件
OUTPUT_FOLDER = "优化后情感分析结果/"  # 新结果保存文件夹

# ===================== 1. 优化：专属停用词（过滤无意义中性词） =====================
# 新增手机品类、平台、无意义通用词，彻底解决负面词混入无效内容
CUSTOM_STOPWORDS = {
    # 平台/品类通用词
    "手机", "京东", "自营", "红米", "小米", "商家", "快递", "发货", "日期", "第五天",
    # 无意义中性词
    "这个", "两个", "可以", "时间", "收到", "说真的", "操作", "背面", "联网", "个", "天",
    # 原有基础停用词
    "的", "了", "是", "我", "你", "他", "也", "就", "都", "这", "那", "哈", "啊", "呢", "吧", "吗", "在", "有", "和",
    "还", "又"
}

# ===================== 2. 优化：电商领域负面情感词库（只提取真正的负面问题） =====================
# 手机电商评论常用负面词，可按需补充
NEGATIVE_WORDS = {
    # 质量问题
    "卡顿", "发热", "发烫", "掉电", "耗电", "死机", "黑屏", "闪退", "花屏", "断触", "失灵",
    "划痕", "磨损", "瑕疵", "坏了", "故障", "质量差", "品控差", "翻新", "二手",
    # 性能问题
    "卡顿", "延迟", "掉帧", "信号差", "断网", "没信号", "续航差", "充电慢", "不流畅",
    # 外观/配件
    "色差", "缝隙", "歪了", "缺配件", "没充电器", "包装差", "破损",
    # 物流/服务
    "物流慢", "发货慢", "不发货", "拒收", "退货", "退款", "售后差", "客服差", "不理人",
    "推诿", "扯皮", "不解决", "态度差",
    # 体验负面
    "不好", "很差", "垃圾", "失望", "后悔", "踩坑", "不值", "不推荐", "难用", "麻烦",
    "一般", "普通", "不满意", "不太行", "拉胯"
}


# ===================== 工具函数 =====================
def sentiment_analysis_single_file(df, file_name):
    """优化后的单商品情感分析"""
    # --------------------------
    # 优化1：调整情感阈值，解决好评率虚高
    # 正向阈值从0.7调高到0.8，负向阈值从0.3调高到0.4，压缩中性区间，减少误判
    # --------------------------
    POSITIVE_THRESHOLD = 0.8
    NEGATIVE_THRESHOLD = 0.4

    # 情感分值计算（优化异常处理）
    def get_sentiment_score(content):
        if not content or len(content.strip()) < 3:  # 过滤过短的无意义评论
            return 0.5
        try:
            s = SnowNLP(content)
            return round(s.sentiments, 4)
        except:
            return 0.5  # 异常评论默认中性

    df["情感分值"] = df["清洗后评论"].apply(get_sentiment_score)

    # 情感倾向划分（优化后的阈值）
    def get_sentiment_label(score):
        if score >= POSITIVE_THRESHOLD:
            return "正向"
        elif score <= NEGATIVE_THRESHOLD:
            return "负向"
        else:
            return "中性"

    df["情感倾向"] = df["情感分值"].apply(get_sentiment_label)

    # 统计商品核心指标
    total = len(df)
    positive = len(df[df["情感倾向"] == "正向"])
    negative = len(df[df["情感倾向"] == "负向"])
    neutral = len(df[df["情感倾向"] == "中性"])
    positive_rate = round(positive / total * 100, 2) if total > 0 else 0

    # --------------------------
    # 优化2：高频关键词过滤（去掉停用词）
    # --------------------------
    def filter_valid_words(words_list):
        # 只保留非停用词、长度>1的有效词
        return [w for w in words_list if w not in CUSTOM_STOPWORDS and len(w) > 1]

    # 全量高频关键词（过滤后）
    all_words = " ".join(df["分词后评论"]).split()
    valid_all_words = filter_valid_words(all_words)
    top_keywords = Counter(valid_all_words).most_common(10)

    # --------------------------
    # 优化3：负面核心问题只提取负面词（彻底解决无效中性词问题）
    # --------------------------
    # 负向评论分词
    negative_df = df[df["情感倾向"] == "负向"]
    negative_all_words = " ".join(negative_df["分词后评论"]).split()
    # 只保留在负面词库里的词，过滤所有中性词
    valid_negative_words = [w for w in negative_all_words if w in NEGATIVE_WORDS]
    # 统计TOP5负面问题，无负面词则标记
    top_negative_words = Counter(valid_negative_words).most_common(5) if valid_negative_words else ["无明确负面问题"]

    # 组装单品报告
    single_report = {
        "商品名称（来源文件）": file_name.replace("预处理_", "").replace(".csv", ""),
        "评论总数": total,
        "正向评论数": positive,
        "负向评论数": negative,
        "中性评论数": neutral,
        "好评率(%)": positive_rate,
        "高频核心卖点": str(top_keywords),
        "负面核心问题": str(top_negative_words)
    }

    return df, single_report


def batch_sentiment_analysis():
    """批量处理10个单品情感分析"""
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    all_single_reports = []

    for file in os.listdir(PREPROCESS_FOLDER):
        if file.startswith("预处理_") and file.endswith(".csv"):
            file_path = os.path.join(PREPROCESS_FOLDER, file)
            print(f"\n========== 分析商品：{file.replace('预处理_', '')} ==========")

            df = pd.read_csv(file_path, encoding="utf-8-sig")
            df_with_sentiment, single_report = sentiment_analysis_single_file(df, file)

            # 保存单品情感数据
            output_file = os.path.join(OUTPUT_FOLDER, f"优化情感分析_{file}")
            df_with_sentiment.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"💾 已保存：{output_file}")

            all_single_reports.append(single_report)

    # 生成单品对比报告
    report_df = pd.DataFrame(all_single_reports)
    report_df.to_excel(os.path.join(OUTPUT_FOLDER, "优化后单品口碑对比报告.xlsx"), index=False)
    print(f"\n📊 单品对比报告已生成：{OUTPUT_FOLDER}优化后单品口碑对比报告.xlsx")

    return report_df


def global_sentiment_analysis():
    """优化后的全局情感分析"""
    if not os.path.exists(MERGED_FILE):
        print(f"❌ 未找到合并大文件：{MERGED_FILE}")
        return None

    df = pd.read_csv(MERGED_FILE, encoding="utf-8-sig")
    total = len(df)
    POSITIVE_THRESHOLD = 0.8
    NEGATIVE_THRESHOLD = 0.4

    # 全局情感计算
    def get_sentiment_score(content):
        if not content or len(content.strip()) < 3:
            return 0.5
        try:
            return round(SnowNLP(content).sentiments, 4)
        except:
            return 0.5

    df["情感分值"] = df["清洗后评论"].apply(get_sentiment_score)
    df["情感倾向"] = df["情感分值"].apply(
        lambda x: "正向" if x >= POSITIVE_THRESHOLD else "负向" if x <= NEGATIVE_THRESHOLD else "中性")

    # 全局统计
    positive_total = len(df[df["情感倾向"] == "正向"])
    negative_total = len(df[df["情感倾向"] == "负向"])
    neutral_total = len(df[df["情感倾向"] == "中性"])
    global_positive_rate = round(positive_total / total * 100, 2) if total > 0 else 0

    # 过滤后的全局高频词
    def filter_valid_words(words_list):
        return [w for w in words_list if w not in CUSTOM_STOPWORDS and len(w) > 1]

    all_words = " ".join(df["分词后评论"]).split()
    global_top_keywords = Counter(filter_valid_words(all_words)).most_common(15)

    # 全局负面核心问题（只保留负面词）
    negative_all_words = " ".join(df[df["情感倾向"] == "负向"]["分词后评论"]).split()
    valid_negative_words = [w for w in negative_all_words if w in NEGATIVE_WORDS]
    global_top_negative = Counter(valid_negative_words).most_common(8) if valid_negative_words else ["无明确负面问题"]

    # 全局报告
    global_report = {
        "全局评论总数": total,
        "全局正向评论数": positive_total,
        "全局负向评论数": negative_total,
        "全局中性评论数": neutral_total,
        "全局好评率(%)": global_positive_rate,
        "全局核心卖点": str(global_top_keywords),
        "全局负面核心问题": str(global_top_negative)
    }

    # 保存结果
    global_df = pd.DataFrame([global_report])
    global_df.to_excel(os.path.join(OUTPUT_FOLDER, "优化后全局情感分析报告.xlsx"), index=False)
    df.to_csv(os.path.join(OUTPUT_FOLDER, "优化后全局带情感评论数据.csv"), index=False, encoding="utf-8-sig")

    print(f"\n🌍 全局分析完成：")
    print(f"   总评论数：{total} | 全局好评率：{global_positive_rate}%")
    print(f"   全局负面核心问题：{global_top_negative}")
    return global_report


# ===================== 执行全流程 =====================
if __name__ == "__main__":
    print("===== 开始优化版单品情感分析 =====")
    single_report_df = batch_sentiment_analysis()

    print("\n===== 开始优化版全局情感分析 =====")
    global_report = global_sentiment_analysis()

    # 打印核心结果
    print("\n===== 核心分析结果汇总 =====")
    print("【单品好评率排序】")
    print(
        single_report_df.sort_values("好评率(%)", ascending=False)[["商品名称（来源文件）", "好评率(%)", "负面核心问题"]])