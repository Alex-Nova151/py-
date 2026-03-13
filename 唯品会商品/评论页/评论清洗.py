import pandas as pd
import jieba
import re
from collections import Counter
import os
from pathlib import Path

# ===================== 基础配置（修改为你的路径） =====================
RAW_DATA_FOLDER = "商品评论数据"  # 你的CSV所在文件夹
OUTPUT_FOLDER = "商品评论数据1"  # 结果保存文件夹
MERGED_FILE_NAME = "合并后_所有评论预处理数据.csv"
STOPWORDS_PATH = "stopwords.txt"  # 停用词文件（可选）


# ===================== 工具函数 =====================
def load_stopwords():
    """加载停用词表（兼容无停用词文件的情况）"""
    if not os.path.exists(STOPWORDS_PATH):
        print(f"⚠️ 未找到停用词文件{STOPWORDS_PATH}，使用默认停用词")
        default_stopwords = {"的", "了", "是", "我", "你", "他", "也", "就", "都", "这", "那",
                             "哈", "啊", "呢", "吧", "吗", "在", "有", "和", "还", "个", "又"}
        return default_stopwords

    with open(STOPWORDS_PATH, "r", encoding="utf-8") as f:
        stopwords = [line.strip() for line in f.readlines()]
    stopwords.extend(["的", "了", "是", "我", "你", "他", "也", "就", "都", "这", "那", "哈", "啊"])
    return set(stopwords)


stopwords = load_stopwords()


def preprocess_single_comment_df(df, file_name):
    """单文件评论预处理（适配你的列名：评论内容）"""
    # 1. 确认核心列存在（你的评论列是「评论内容」）
    if "评论内容" not in df.columns:
        print(f"❌ {file_name} 无「评论内容」列，跳过该文件")
        return None

    # 2. 去重（按「评论ID」+「评论内容」去重，优先保留第一条）
    if "评论ID" in df.columns:
        df = df.drop_duplicates(subset=["评论ID"], keep="first")
    df = df.drop_duplicates(subset=["评论内容"], keep="first")

    # 3. 去除无效评论（空内容/纯符号/广告）
    def filter_invalid(content):
        if pd.isna(content) or content.strip() == "":
            return False
        # 去除纯符号/数字的无效评论（只保留中文）
        content_clean = re.sub(r"[^\u4e00-\u9fa5a-zA-Z]", "", content)
        if len(content_clean) < 2:  # 至少保留2个有效字符
            return False
        # 过滤广告类评论
        ad_words = ["刷单", "广告", "微信", "QQ", "加群", "返利", "红包", "代购", "秒杀"]
        if any(word in content for word in ad_words):
            return False
        return True

    # 应用过滤逻辑
    df = df[df["评论内容"].apply(filter_invalid)]
    if len(df) == 0:
        print(f"⚠️ {file_name} 过滤后无有效评论，跳过")
        return None

    # 4. 评论内容清洗（只保留中文和空格，去特殊符号）
    def clean_content(content):
        content = re.sub(r"[^\u4e00-\u9fa5\s]", "", content)  # 过滤非中文
        return content.strip()

    df["清洗后评论"] = df["评论内容"].apply(clean_content)

    # 5. 分词 + 去除停用词（jieba分词）
    def cut_content(content):
        words = jieba.lcut(content)  # 精确分词
        # 过滤停用词+单字（只保留长度>1的有效词）
        words_filtered = [w for w in words if w not in stopwords and len(w) > 1]
        return " ".join(words_filtered)

    df["分词后评论"] = df["清洗后评论"].apply(cut_content)

    # 6. 过滤分词后为空的评论
    df = df[df["分词后评论"].str.len() > 0]

    # 7. 标记来源文件（便于后续分析哪个商品的评论）
    df["来源文件"] = file_name

    print(f"✅ {file_name} 预处理完成：原始{len(df)}条 → 有效{len(df)}条")
    return df


def batch_preprocess_comments():
    """批量处理文件夹下的所有CSV文件"""
    # 创建输出文件夹（不存在则自动创建）
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    # 存储所有预处理后的df，用于合并
    all_clean_dfs = []

    # 遍历原始文件夹下的所有CSV文件
    for file in os.listdir(RAW_DATA_FOLDER):
        if not file.endswith(".csv"):
            continue  # 只处理CSV文件

        file_path = os.path.join(RAW_DATA_FOLDER, file)
        print(f"\n========== 开始处理：{file} ==========")

        # 加载单个CSV（兼容utf-8和gbk编码，解决中文乱码）
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding="gbk")
            except:
                print(f"❌ {file} 编码错误（非utf-8/gbk），无法读取")
                continue
        except Exception as e:
            print(f"❌ {file} 读取失败：{e}")
            continue

        # 预处理单文件
        df_clean = preprocess_single_comment_df(df, file)
        if df_clean is None:
            continue

        # 保存单个预处理后的文件
        output_file_path = os.path.join(OUTPUT_FOLDER, f"预处理_{file}")
        df_clean.to_csv(output_file_path, index=False, encoding="utf-8-sig")
        print(f"💾 已保存：{output_file_path}")

        # 加入总列表，用于后续合并
        all_clean_dfs.append(df_clean)

    # 合并所有预处理后的文件（生成全量数据）
    if all_clean_dfs:
        df_merged = pd.concat(all_clean_dfs, ignore_index=True)

        # ========== 关键：全量去重（完全相同的评论只保留一条） ==========
        print(f"\n📌 合并后原始数据量：{len(df_merged)}条")
        # 按「评论内容」去重（跨文件完全相同的评论只保留第一条）
        df_merged = df_merged.drop_duplicates(subset=["评论内容"], keep="first")
        # 可选：按「清洗后评论」二次去重（避免特殊符号不同但内容相同的重复）
        df_merged = df_merged.drop_duplicates(subset=["清洗后评论"], keep="first")
        print(f"📌 全量去重后数据量：{len(df_merged)}条")

        merged_file_path = os.path.join(OUTPUT_FOLDER, MERGED_FILE_NAME)
        df_merged.to_csv(merged_file_path, index=False, encoding="utf-8-sig")
        print(f"\n📊 合并完成！共{len(df_merged)}条有效评论，保存至：{merged_file_path}")
    else:
        print("\n❌ 无有效文件可合并")


# ===================== 执行批量处理 =====================
if __name__ == "__main__":
    # 检查原始文件夹是否存在
    if not os.path.exists(RAW_DATA_FOLDER):
        print(f"❌ 原始文件夹{RAW_DATA_FOLDER}不存在，请检查路径！")
    else:
        batch_preprocess_comments()
        print("\n🎉 所有文件预处理完成！")