# ===================== 1. 导入所有需要的库 =====================
import pandas as pd
import os
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import jieba
from collections import Counter
from scipy.stats import pearsonr

# ===================== 2. 核心配置与交互输入 =====================
# 获取当前脚本所在的文件夹路径 → 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"✅ 项目根目录：{BASE_DIR}")


# ===================== 核心函数：交互式选择评论文件夹 =====================
def get_comment_folder():
    """
    交互式获取评论文件夹路径：
    1. 可输入「相对路径」（基于项目根目录）
    2. 可输入「绝对路径」（直接指定完整路径）
    3. 支持模糊提示，避免输错
    """
    print("\n📂 请输入评论文件夹路径（支持2种方式）：")
    print("   方式1：相对路径（基于项目根目录），例如：京东商品/评论页、淘宝评论、全部评论")
    print("   方式2：绝对路径（完整路径），例如：D:/寒假/京东商品/评论页、/Users/xxx/寒假/评论")
    print("   输入示例：京东商品/评论页")

    # 循环直到输入有效路径
    while True:
        # 获取用户输入
        folder_input = input("\n请输入评论文件夹路径：").strip()

        # 处理空输入
        if not folder_input:
            print("❌ 路径不能为空，请重新输入！")
            continue

        # 判断是相对路径还是绝对路径
        if os.path.isabs(folder_input):
            comment_folder = folder_input  # 绝对路径直接使用
        else:
            comment_folder = os.path.join(BASE_DIR, folder_input)  # 相对路径拼接根目录

        # 检查路径是否存在
        if os.path.exists(comment_folder):
            # 检查是否是文件夹
            if os.path.isdir(comment_folder):
                print(f"✅ 评论文件夹验证成功：{comment_folder}")
                return comment_folder
            else:
                print(f"❌ 输入的路径不是文件夹：{comment_folder}")
        else:
            # 提示路径不存在，并询问是否创建
            create_choice = input(f"❌ 文件夹不存在：{comment_folder}，是否创建？(y/n)：").strip().lower()
            if create_choice == "y":
                os.makedirs(comment_folder, exist_ok=True)
                print(f"✅ 已创建文件夹：{comment_folder}")
                return comment_folder
            else:
                print("🔄 请重新输入有效的文件夹路径！")


# ===================== 工具函数：读取单个CSV文件 =====================
def read_single_comment_csv(file_path, platform=None):
    """
    读取单个评论CSV文件，兼容多种编码，自动识别平台
    :param file_path: CSV文件路径
    :param platform: 手动指定平台（可选）
    :return: 单个文件的DataFrame
    """
    try:
        # 兼容中文编码（优先utf-8-sig，失败则用gbk）
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="gbk")

        # 自动从文件名识别平台
        file_name = os.path.basename(file_path).lower()
        if not platform:
            if "京东" in file_name or "jd" in file_name:
                platform = "京东"
            elif "淘宝" in file_name or "tb" in file_name:
                platform = "淘宝"
            elif "唯品会" in file_name or "vip" in file_name:
                platform = "唯品会"
            else:
                platform = "未知平台"

        # 标记平台和来源文件（方便追溯）
        df["平台"] = platform
        df["来源文件"] = os.path.basename(file_path)
        print(f"   ✅ 读取成功：{os.path.basename(file_path)} → {len(df)}条评论")
        return df
    except Exception as e:
        print(f"   ❌ 读取失败：{os.path.basename(file_path)} → 错误：{e}")
        return pd.DataFrame()


# ===================== 核心函数：批量读取评论文件 =====================
def load_all_comment_data(comment_folder):
    """
    批量读取指定文件夹下的所有评论CSV文件
    :param comment_folder: 评论文件夹路径
    :return: 合并后的所有评论DataFrame
    """
    # 筛选文件夹下所有CSV文件（忽略隐藏文件/非CSV）
    csv_files = []
    for file in os.listdir(comment_folder):
        if file.endswith(".csv") and not file.startswith("."):
            csv_files.append(os.path.join(comment_folder, file))

    if len(csv_files) == 0:
        print(f"\n❌ 文件夹中未找到任何CSV文件：{comment_folder}")
        return pd.DataFrame()

    # 打印找到的文件列表
    print(f"\n📁 共找到 {len(csv_files)} 个评论CSV文件：")
    for f in csv_files:
        print(f"   - {os.path.basename(f)}")

    # 逐个读取并合并
    all_comment_dfs = []
    for csv_file in csv_files:
        df_single = read_single_comment_csv(csv_file)
        if len(df_single) > 0:
            all_comment_dfs.append(df_single)

    # 合并所有数据
    if len(all_comment_dfs) == 0:
        print("\n❌ 没有有效的评论数据可合并！")
        return pd.DataFrame()

    df_all_comments = pd.concat(all_comment_dfs, ignore_index=True)
    # 去重（可选，避免重复读取同一文件）
    df_all_comments = df_all_comments.drop_duplicates()

    # 打印汇总信息
    print(f"\n✅ 所有评论数据合并完成 → 总计 {len(df_all_comments)} 条评论（已去重）")
    print("📊 各平台评论数量：")
    platform_count = df_all_comments["平台"].value_counts()
    for platform, count in platform_count.items():
        print(f"   - {platform}：{count}条")

    return df_all_comments


# ===================== 结果保存函数 =====================
def save_comment_data(df_all_comments, comment_folder):
    """保存合并后的评论数据到指定路径"""
    # 结果保存路径（基于项目根目录的「数据分析」文件夹）
    output_folder = os.path.join(BASE_DIR, "数据分析")
    os.makedirs(output_folder, exist_ok=True)

    # 生成保存文件名（包含原文件夹名，避免覆盖）
    folder_name = os.path.basename(comment_folder)
    save_path = os.path.join(output_folder, f"合并后的评论数据_{folder_name}.csv")

    # 保存CSV（utf-8-sig编码，兼容Excel打开）
    df_all_comments.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"\n💾 合并后的数据已保存至：{save_path}")
    return save_path


# ===================== 主程序执行 =====================
if __name__ == "__main__":
    # 1. 交互式获取评论文件夹
    COMMENT_FOLDER = get_comment_folder()

    # 2. 批量读取并合并评论数据
    df_all_comments = load_all_comment_data(COMMENT_FOLDER)

    # 3. 如果有有效数据，保存结果
    if len(df_all_comments) > 0:
        save_comment_data(df_all_comments, COMMENT_FOLDER)

    print("\n🎉 评论数据读取与合并流程完成！")