# -*- coding: utf-8 -*-
import streamlit as st
import os
import base64

# ===================== 全局配置 & 美化样式 =====================
st.set_page_config(
    page_title="电商手机数据分析仪表盘",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 自定义CSS美化（核心：卡片样式、字体、间距、颜色）
def add_custom_css():
    st.markdown("""
    <style>
    /* 全局样式 */
    .main {padding-top: 1rem;}
    .css-18e3th9 {padding-top: 0; padding-bottom: 0;}
    .css-1d391kg {padding-top: 1rem; padding-bottom: 1rem;}

    /* 标题样式 */
    h1 {color: #2E4057; font-weight: 700; margin-bottom: 0.5rem;}
    h2 {color: #3F6BAA; font-weight: 600; border-left: 4px solid #3F6BAA; padding-left: 0.8rem;}
    h3 {color: #4A7BA7; font-weight: 500;}

    /* 指标卡片样式 */
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* 模块分隔线 */
    .divider {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #3F6BAA, #8EB8E5);
        margin: 1.5rem 0;
    }

    /* 侧边栏样式 */
    .css-1d391kg {background-color: #F8FAFC;}
    .sidebar-title {color: #2E4057; font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)


add_custom_css()

# ===================== 路径配置（按你的文件夹结构修正） =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_CHART_DIR = os.path.join(BASE_DIR, "商品页简化分析图表")
COMMENT_CHART_DIR = os.path.join(BASE_DIR, "数据分析", "评论页核心图表_最终版")


# ===================== 辅助函数 =====================
def embed_html_chart(chart_path, height=600):
    """嵌入本地HTML图表，带容错处理"""
    if not os.path.exists(chart_path):
        st.warning(f"⚠️ 未找到图表文件：{os.path.basename(chart_path)}")
        return
    try:
        with open(chart_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=height, scrolling=True)
    except Exception as e:
        st.error(f"❌ 加载图表失败：{str(e)}")


def get_img_as_base64(file):
    """将图片转为base64（可选：添加logo用）"""
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# ===================== 侧边栏筛选组件（交互式核心） =====================
def sidebar_filters():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">📊 数据筛选</div>', unsafe_allow_html=True)

        # 1. 平台筛选
        platforms = ["全部", "京东", "淘宝", "唯品会"]
        selected_platform = st.selectbox("🔍 选择平台", platforms)

        # 2. 价格带筛选
        price_ranges = ["全部", "0-1000元", "1000-2000元", "2000-3000元", "3000元以上"]
        selected_price = st.selectbox("💰 选择价格带", price_ranges)

        # 3. 视图切换
        view_mode = st.radio("📋 视图模式", ["完整视图", "简洁视图"], index=0)

        # 4. 重置筛选
        if st.button("🔄 重置筛选", use_container_width=True):
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.caption("📅 数据更新时间：2026-03-11")

        return selected_platform, selected_price, view_mode


# 获取筛选参数
selected_platform, selected_price, view_mode = sidebar_filters()

# ===================== 页面主体内容（6大核心模块） =====================
# 顶部标题 + 说明
st.title("📱 电商手机数据分析仪表盘")
st.markdown(f"""
当前筛选：平台={selected_platform} | 价格带={selected_price} | 视图模式={view_mode}
""", unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== 模块1：市场概览（核心指标卡片） ==========
st.subheader("1. 市场概览")
col1, col2, col3, col4 = st.columns(4, gap="medium")

# 指标卡片（模拟数据，可替换为真实数据）
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📦 在售商品数", "286", delta="+12")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💬 有效评论数", "15,892", delta="+876")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 商品均价", "¥1,899", delta="-¥56")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⭐ 平均好评率", "92.3%", delta="+1.2%")
    st.markdown('</div>', unsafe_allow_html=True)

# 市场概览图表（价格-销量分布）
if view_mode == "完整视图":
    st.markdown("### 价格-销量整体分布")
    embed_html_chart(os.path.join(PRODUCT_CHART_DIR, "04_价格销量相关性.html"), height=500)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== 模块2：品牌格局 ==========
st.subheader("2. 品牌格局")
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 品牌销量占比")
    embed_html_chart(os.path.join(PRODUCT_CHART_DIR, "品牌销量占比.html"), height=450)  # 替换为你的品牌占比图表

with col2:
    st.markdown("### 品牌好评率对比")
    embed_html_chart(os.path.join(COMMENT_CHART_DIR, "品牌好评率对比.html"), height=450)  # 替换为你的品牌好评率图表

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== 模块3：价格带分析 ==========
st.subheader("3. 价格带分析")
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 价格带商品分布")
    embed_html_chart(os.path.join(PRODUCT_CHART_DIR, "01_价格带商品分布.html"), height=450)

with col2:
    st.markdown("### 价格带销量分析")
    embed_html_chart(os.path.join(PRODUCT_CHART_DIR, "02_价格带销量分析.html"), height=450)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== 模块4：商品竞争力榜单 ==========
st.subheader("4. 商品竞争力榜单")
# 销量TOP10表格（模拟数据，可替换为真实数据）
top_products = {
    "商品ID": ["JD-001", "TB-005", "VP-003", "JD-008", "TB-012"],
    "品牌": ["小米", "华为", "苹果", "OPPO", "vivo"],
    "价格(元)": [1599, 2899, 5999, 1899, 2199],
    "销量(件)": [12580, 9870, 8560, 7890, 7560],
    "好评率": ["95.2%", "94.8%", "96.5%", "93.7%", "92.9%"]
}
st.dataframe(
    top_products,
    use_container_width=True,
    hide_index=True,
    column_config={
        "商品ID": st.column_config.TextColumn("商品ID", width="small"),
        "品牌": st.column_config.TextColumn("品牌", width="small"),
        "价格(元)": st.column_config.NumberColumn("价格(元)", format="¥%d"),
        "销量(件)": st.column_config.NumberColumn("销量(件)", format="%d"),
        "好评率": st.column_config.ProgressColumn("好评率", format="%f", min_value=0, max_value=100)
    }
)

# 销量TOP10图表
if view_mode == "完整视图":
    st.markdown("### 商品销量TOP10")
    embed_html_chart(os.path.join(PRODUCT_CHART_DIR, "商品销量TOP10.html"), height=450)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== 模块5：竞品平台对比 ==========
st.subheader("5. 竞品平台对比")
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 平台销量对比")
    embed_html_chart(os.path.join(PRODUCT_CHART_DIR, "03_平台销量对比.html"), height=450)

with col2:
    st.markdown("### 平台好评率对比")
    embed_html_chart(os.path.join(COMMENT_CHART_DIR, "平台好评率对比.html"), height=450)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== 模块6：口碑洞察 ==========
st.subheader("6. 口碑洞察")
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 全商品好评率")
    embed_html_chart(os.path.join(COMMENT_CHART_DIR, "01_全商品好评率.html"), height=500)

with col2:
    st.markdown("### 核心亮点TOP20")
    embed_html_chart(os.path.join(COMMENT_CHART_DIR, "02_核心亮点TOP20.html"), height=500)

# 负面问题分析
st.markdown("### 精准负面问题")
embed_html_chart(os.path.join(COMMENT_CHART_DIR, "02_精准负面问题.html"), height=450)

# ===================== 底部信息 =====================
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
📊 电商手机数据分析仪表盘 v1.0 | 数据来源：京东/淘宝/唯品会 | 最后更新：2026-03-11
</div>
""", unsafe_allow_html=True)