import streamlit as st
import requests
import base64
import time
import random
from datetime import datetime
import json

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="ShowImageWeb - AI图像生成器",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 强制页面从顶部开始 - 在最开始执行
st.markdown("""
<script>
// 页面顶部强制执行
document.documentElement.scrollTop = 0;
document.body.scrollTop = 0;
window.scrollTo(0, 0);
</script>
<style>
html {
    scroll-behavior: auto !important;
    scroll-padding-top: 0 !important;
}
body {
    scroll-behavior: auto !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. 高级CSS样式系统 ---
st.markdown("""
<style>
    /* CSS变量定义 */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #13B497 0%, #59D4A8 100%);
        --warning-gradient: linear-gradient(135deg, #FFA500 0%, #FF6347 100%);
        --glass-bg: rgba(255, 255, 255, 0.25);
        --glass-border: rgba(255, 255, 255, 0.18);
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
        --shadow-xl: 0 20px 40px rgba(0,0,0,0.15);
        --border-radius-sm: 12px;
        --border-radius-md: 16px;
        --border-radius-lg: 24px;
        --transition-fast: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-normal: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* 全局背景设计 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        min-height: 100vh;
        position: relative;
    }

    /* 动态背景粒子效果 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background:
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
        z-index: -1;
        animation: floatGradient 20s ease infinite;
    }

    @keyframes floatGradient {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-20px, -20px) rotate(1deg); }
        66% { transform: translate(20px, -10px) rotate(-1deg); }
    }

    /* 玻璃态容器 */
    .glass-container {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-xl);
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: var(--transition-normal);
    }

    .glass-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }

    .glass-container:hover::before {
        left: 100%;
    }

    .glass-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.25);
    }

    /* 侧边栏超现代化设计 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.1);
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1.5rem !important;
    }

    /* 侧边栏标题发光效果 */
    section[data-testid="stSidebar"] h1 {
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        animation: glow 3s ease-in-out infinite alternate;
        margin-bottom: 2rem !important;
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.3)); }
        to { filter: drop-shadow(0 0 30px rgba(240, 147, 251, 0.5)); }
    }

    /* 侧边栏组件样式 */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 1.1rem !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #e5e7eb !important;
        font-weight: 400 !important;
    }

    /* 输入框样式重设计 */
    .stTextArea > div > textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: var(--border-radius-md) !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px);
        transition: var(--transition-normal) !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }

    .stTextArea > div > textarea:focus {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        outline: none !important;
    }

    .stTextInput > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: var(--border-radius-sm) !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px);
        transition: var(--transition-normal) !important;
    }

    .stTextInput > div > input:focus {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        outline: none !important;
    }

    /* 按钮系统重设计 */
    div.stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-sm) !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 1rem 2rem !important;
        transition: var(--transition-normal) !important;
        box-shadow: var(--shadow-md) !important;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div.stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }

    div.stButton > button:hover::before {
        left: 100%;
    }

    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3) !important;
    }

    div.stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }

    /* Primary按钮特殊样式 */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B6B, #FFE66D, #4ECDC4, #667eea) !important;
        background-size: 300% 300% !important;
        animation: gradientShift 3s ease infinite !important;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 下载按钮样式 */
    div.stDownloadButton > button {
        background: var(--success-gradient) !important;
        border-radius: var(--border-radius-sm) !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: var(--transition-normal) !important;
    }

    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(19, 180, 151, 0.3) !important;
    }

    /* 主标题区域 */
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
    }

    .main-header h1 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 4rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #ffffff, #f0f0f0, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 50px rgba(255,255,255,0.3);
        margin-bottom: 1rem !important;
        animation: titleFloat 6s ease-in-out infinite;
    }

    @keyframes titleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    .main-header p {
        font-size: 1.3rem !important;
        color: rgba(255,255,255,0.9) !important;
        font-weight: 400 !important;
        margin: 0 !important;
    }

    /* 输入区域高级容器 */
    .input-section {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        position: relative;
    }

    /* 图片画廊卡片系统 */
    .gallery-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--border-radius-md);
        overflow: hidden;
        transition: var(--transition-normal);
        position: relative;
        box-shadow: var(--shadow-md);
        margin-bottom: 1rem;
        /* 正方形画框容器 */
        aspect-ratio: 1/1;
    }

    .gallery-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        background: rgba(255, 255, 255, 0.25);
    }

    .gallery-card img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: var(--transition-slow);
        background: rgba(0,0,0,0.1);
        /* 确保图片填满正方形容器 */
        border-radius: var(--border-radius-md);
    }

    .gallery-card:hover img {
        transform: scale(1.05);
    }

    /* 图片信息标签 */
    .image-info {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
        color: white;
        padding: 1rem;
        opacity: 0;
        transform: translateY(20px);
        transition: var(--transition-normal);
    }

    .gallery-card:hover .image-info {
        opacity: 1;
        transform: translateY(0);
    }

    /* 状态指示器美化 */
    .stStatus .stAlert {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: var(--border-radius-md) !important;
        color: white !important;
        font-weight: 500 !important;
    }

    /* 滑块样式 */
    .stSlider {
        margin: 1.5rem 0 !important;
    }

    .stSlider [data-testid="stSliderHandle"] {
        background: var(--primary-gradient) !important;
        border: 2px solid white !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stSlider [data-testid="stSliderTrack"] {
        background: rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
    }

    /* 开关按钮美化 */
    .stCheckbox [data-testid="stMarkdownContainer"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 1rem !important;
        transition: var(--transition-normal) !important;
    }

    .stCheckbox:hover [data-testid="stMarkdownContainer"] {
        background: rgba(255, 255, 255, 0.15) !important;
    }

    /* 度量卡片美化 */
    .stMetric {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-lg) !important;
        transition: var(--transition-normal) !important;
    }

    .stMetric:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        background: rgba(255, 255, 255, 0.2);
    }

    /* 信息提示美化 */
    .stInfo {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(240, 147, 251, 0.2)) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: var(--border-radius-lg) !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 1.5rem !important;
    }

    /* 加载动画美化 */
    .stSpinner > div {
        border-top-color: #667eea !important;
        border-radius: 50% !important;
        animation: spin 1s linear infinite !important;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-gradient);
    }

    /* 禁用平滑滚动 */
    html {
        scroll-behavior: auto !important;
        scroll-padding-top: 0 !important;
    }

    body {
        scroll-behavior: auto !important;
        overflow-x: hidden;
    }

    /* 确保主内容区域可见 */
    .stApp {
        scroll-margin-top: 0 !important;
        min-height: 100vh;
    }

    /* 防止固定定位元素影响滚动 */
    .stSidebar {
        position: sticky !important;
        top: 0;
        height: 100vh;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem !important;
        }

        .glass-container {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .input-section {
            padding: 1.5rem;
        }

        /* 保持正方形比例，但调整画框的缩放效果 */
        .gallery-card:hover img {
            transform: scale(1.03);
        }
    }

    @media (max-width: 480px) {
        /* 小屏幕下略微减小悬停缩放效果 */
        .gallery-card:hover img {
            transform: scale(1.02);
        }

        /* 优化小屏幕下的卡片间距 */
        .gallery-card {
            margin-bottom: 0.75rem;
        }
    }

    /* 特殊效果：霓虹发光 */
    .neon-glow {
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5),
                    0 0 40px rgba(102, 126, 234, 0.3),
                    0 0 60px rgba(102, 126, 234, 0.1);
    }

    /* 悬浮动画 */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }

    .floating {
        animation: float 6s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
# 初始化历史记录
if 'history' not in st.session_state:
    st.session_state.history = []

# 初始化生成状态（用于控制按钮变灰）
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

# 初始化填充提示状态
if 'filled_prompt' not in st.session_state:
    st.session_state.filled_prompt = ""

# 初始化保存的输入内容
if 'saved_prompt' not in st.session_state:
    st.session_state.saved_prompt = ""

# 初始化生成记录状态
if 'has_generated' not in st.session_state:
    st.session_state.has_generated = False

def add_to_history(prompt, image_bytes, seed, duration):
    """将生成的图片添加到历史记录的最前面"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    # 只存储base64编码，节省内存
    base64_image = base64.b64encode(image_bytes).decode()
    st.session_state.history.insert(0, {
        "id": f"{int(time.time())}",
        "prompt": prompt,
        "base64_image": base64_image,  # 只存储base64
        "seed": seed,
        "time": timestamp,
        "duration": f"{duration:.2f}s"
    })
    # 标记已有生成记录
    st.session_state.has_generated = True

def clear_history():
    st.session_state.history = []
    st.session_state.has_generated = False

def start_generating():
    """点击按钮时的回调：设置状态为生成中"""
    st.session_state.is_generating = True

# --- 4. 超现代化侧边栏控制台 ---
with st.sidebar:
    # 动态装饰分隔线
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="height: 3px; background: linear-gradient(90deg, #667eea, #764ba2, #f093fb); border-radius: 5px; margin-bottom: 1rem;"></div>
    </div>
    """, unsafe_allow_html=True)

    # 控制台标题
    st.markdown('<h1 style="text-align: center; font-size: 2rem; margin-bottom: 1.5rem;">控制台</h1>', unsafe_allow_html=True)

    # API配置区域
    st.markdown('<h4 style="color: #667eea; margin-bottom: 0.5rem; font-size: 0.9rem;">🔑 API 配置</h4>', unsafe_allow_html=True)

    api_base_url = st.text_input(
        "🌐 API Endpoint",
        value="https://z-api.aioec.tech/proxy/generate",
        help="完整的API接口地址",
        label_visibility="visible"
    )
    api_key = st.text_input(
        "🔐 API Key",
        type="password",
        placeholder="sk-...",
        help="输入您的API密钥"
    )

    # 分隔线
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, rgba(102, 126, 234, 0.3), rgba(102, 126, 234, 0.1), transparent); margin: 1rem 0;"></div>', unsafe_allow_html=True)

    # 生成参数区域
    st.markdown('<h4 style="color: #764ba2; margin-bottom: 0.5rem; font-size: 0.9rem;">⚙️ 生成参数</h4>', unsafe_allow_html=True)

    seed_input = st.number_input(
        "🎲 随机种子",
        value=42,
        step=1,
        help="控制生成结果的随机性"
    )
    use_random = st.toggle("🎯 随机种子模式", value=True, help="每次生成使用不同的随机种子")

    # 分隔线
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, rgba(118, 75, 162, 0.3), rgba(118, 75, 162, 0.1), transparent); margin: 1rem 0;"></div>', unsafe_allow_html=True)

    # 界面设置区域
    st.markdown('<h4 style="color: #f093fb; margin-bottom: 0.5rem; font-size: 0.9rem;">🎨 界面设置</h4>', unsafe_allow_html=True)

    gallery_cols = st.slider(
        "📐 画廊列数",
        min_value=1,
        max_value=4,
        value=2,
        help="列数越少，单张图片显示越大"
    )

    # 分隔线
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, rgba(240, 147, 251, 0.3), rgba(240, 147, 251, 0.1), transparent); margin: 1rem 0;"></div>', unsafe_allow_html=True)

    # 统计信息区域
    st.markdown('<h4 style="color: #13B497; margin-bottom: 0.5rem; font-size: 0.9rem;">📊 统计信息</h4>', unsafe_allow_html=True)

    history_count = len(st.session_state.history)

    # 高级统计卡片
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "🖼️ 已生成",
            f"{history_count}",
            delta=None,
            help="本次会话生成的图片总数"
        )
    with col2:
        if history_count > 0:
            avg_duration = sum(float(item['duration'].rstrip('s')) for item in st.session_state.history[:5]) / min(5, history_count)
            st.metric(
                "⚡ 平均耗时",
                f"{avg_duration:.1f}s",
                help="最近5张图片的平均生成时间"
            )

    # 操作按钮
    if history_count > 0:
        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        if st.button(
            "🗑️ 清空历史记录",
            use_container_width=True,
            type="secondary",
            help="删除所有生成的历史图片"
        ):
            clear_history()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 底部装饰 - 减小间距
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent); border-radius: 5px;"></div>
        <p style="color: #e5e7eb; font-size: 0.8rem; margin-top: 0.5rem;">✨ Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 超现代化主工作区 ---

# 顶部锚点 - 强制页面从这里开始
st.markdown('<div id="top" style="height: 1px; width: 1px; visibility: hidden;"></div>', unsafe_allow_html=True)

# 主标题区域
st.markdown("""
<div class="main-header floating">
    <h1>ShowImageWeb</h1>
    <p>🎨 AI图像生成 - 将您的想象力转化为视觉艺术</p>
</div>
""", unsafe_allow_html=True)

# 输入区域布局
st.markdown('<div style="max-width: 900px; margin: 0 auto 2rem auto;">', unsafe_allow_html=True)

# 主输入区域 - 调整列比例
col1, col2, col3 = st.columns([8, 0.5, 3])

with col1:
    # 确定输入框的默认值
    if st.session_state.filled_prompt:
        # 如果有新的填充内容，使用它
        default_value = st.session_state.filled_prompt
        # 保存到saved_prompt并清空filled_prompt
        st.session_state.saved_prompt = st.session_state.filled_prompt
        st.session_state.filled_prompt = ""
    elif st.session_state.saved_prompt and st.session_state.is_generating:
        # 如果正在生成，使用保存的内容
        default_value = st.session_state.saved_prompt
    else:
        # 否则使用空值
        default_value = ""

    prompt = st.text_area(
        "Prompt",
        value=default_value,
        placeholder="🎯 描述您的创意... 例如：一座漂浮在云端的未来城市，玻璃建筑反射着阳光，8K超高清",
        height=120,
        label_visibility="collapsed",
        disabled=st.session_state.is_generating,
        help="使用详细描述获得更好的生成效果"
    )

    # 实时保存用户输入的内容（仅在不生成时）
    if not st.session_state.is_generating and prompt != st.session_state.saved_prompt:
        st.session_state.saved_prompt = prompt

with col2:
    st.markdown("")  # 空白列用于间距

with col3:
    st.markdown('<div style="padding-top: 2.5rem;">', unsafe_allow_html=True)

    # 生成按钮
    button_text = "立即生成" if not st.session_state.is_generating else "⏳ 生成中..."
    button_emoji = "✨" if not st.session_state.is_generating else "🔄"

    if st.button(
        f"{button_emoji} {button_text}",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.is_generating,
        on_click=start_generating,
        help="点击开始AI图像生成"
    ):
        pass

  
    st.markdown('</div>', unsafe_allow_html=True)

# 分隔线
st.markdown('<div style="height: 1px; background: linear-gradient(90deg, rgba(102, 126, 234, 0.3), rgba(240, 147, 251, 0.1), transparent); margin: 1rem 0;"></div>', unsafe_allow_html=True)

# 快速示例提示 - 只在非生成状态、没有输入内容且从未生成时显示
if not st.session_state.is_generating and not st.session_state.saved_prompt and not st.session_state.has_generated:
    st.markdown('<div style="margin-top: 0.5rem; text-align: center;"><h4 style="color: rgba(255,255,255,0.9); margin-bottom: 0.8rem;">💡 灵感示例</h4>', unsafe_allow_html=True)

    # 使用列布局创建灵感按钮
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

    with col1:
        if st.button("🏰 童话城堡", key="inspiration_1", help="点击填充童话城堡描述", use_container_width=True):
            st.session_state.filled_prompt = "一座宏伟的童话城堡坐落在云朵之上，高耸的塔楼闪烁着金色的光芒"
            st.rerun()

    with col2:
        if st.button("🌸 樱花庭院", key="inspiration_2", help="点击填充樱花庭院描述", use_container_width=True):
            st.session_state.filled_prompt = "春日樱花盛开的日式庭院，粉色花瓣飘落在青石板上"
            st.rerun()

    with col3:
        if st.button("🚀 科幻太空站", key="inspiration_3", help="点击填充科幻太空站描述", use_container_width=True):
            st.session_state.filled_prompt = "未来主义科幻太空站，巨大的环形结构悬浮在星空之中"
            st.rerun()

    with col4:
        if st.button("🐉 巨龙守护者", key="inspiration_4", help="点击填充巨龙守护者描述", use_container_width=True):
            st.session_state.filled_prompt = "古老的巨龙守护着神秘的森林入口，鳞片在月光下闪闪发亮"
            st.rerun()

    with col5:
        if st.button("🌆 赛博都市", key="inspiration_5", help="点击填充赛博都市描述", use_container_width=True):
            st.session_state.filled_prompt = "赛博朋克风格的未来都市，霓虹灯闪烁的摩天大楼"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 生成逻辑 (通过状态控制) ---
if st.session_state.is_generating or (hasattr(st.session_state, 'is_processing') and st.session_state.is_processing):
    # 检查输入有效性
    if not api_key:
        st.toast("🚫 请先在左侧侧边栏配置 API Key", icon="🔒")
        st.session_state.is_generating = False # 重置状态
        st.rerun()
    elif not prompt:
        st.toast("⚠️ 请输入提示词", icon="✏️")
        st.session_state.is_generating = False # 重置状态
        st.rerun()
    else:
        # 准备参数
        endpoint = api_base_url.rstrip('/')
        final_seed = int(time.time() * 1000) % 1000000000 if use_random else int(seed_input)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt, "seed": final_seed}
        
        # 高级加载状态显示
        with st.status(
            "🚀 AI 正在处理您的请求..." if not st.session_state.is_generating else "⚡ GPU 算力运行中...",
            expanded=True
        ) as status:
            start_time = time.time()

            # 进度指示器
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # 步骤1：验证参数
                progress_bar.progress(0.1)
                status_text.text("🔍 验证生成参数...")
                time.sleep(0.5)

                # 步骤2：连接API
                progress_bar.progress(0.3)
                status_text.text("🌐 连接AI服务器...")
                time.sleep(0.5)

                # 步骤3：发送请求
                progress_bar.progress(0.5)
                status_text.text("📤 发送创作指令...")
                time.sleep(0.5)

                # 步骤4：处理请求
                progress_bar.progress(0.7)
                status_text.text("🎨 AI 创作中...")

                response = requests.post(endpoint, headers=headers, json=payload, timeout=60)

                if response.status_code == 200:
                    progress_bar.progress(0.9)
                    status_text.text("📥 接收作品数据...")

                    data = response.json()
                    base64_str = data.get("base64")

                    if base64_str:
                        progress_bar.progress(1.0)
                        status_text.text("✨ 作品完成!")

                        image_bytes = base64.b64decode(base64_str)
                        duration = time.time() - start_time

                        # ✅ 存入历史记录
                        add_to_history(prompt, image_bytes, final_seed, duration)

                        # 成功提示
                        status.update(
                            label=f"🎉 成功生成! 耗时 {duration:.2f} 秒",
                            state="complete",
                            expanded=False
                        )

                        # 成功庆祝动画
                        st.markdown("""
                        <div style="text-align: center; margin: 1rem 0;">
                            <h3 style="color: #13B497;">🎊 作品创作完成!</h3>
                            <p style="color: rgba(255,255,255,0.9);">
                                您的AI作品已添加到画廊中
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        # 启动彩纸效果
                        st.balloons()
                    else:
                        progress_bar.empty()
                        status.update(label="❌ 数据解析失败", state="error")
                        st.error("🔍 服务器返回成功但缺少图片数据")
                else:
                    progress_bar.empty()
                    status.update(label="❌ 请求失败", state="error")
                    st.error(f"🌐 API 错误 {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                progress_bar.empty()
                status.update(label="⏰ 请求超时", state="error")
                st.error("⏱️ 服务器响应超时，请稍后重试")

            except requests.exceptions.ConnectionError:
                progress_bar.empty()
                status.update(label="🔌 连接失败", state="error")
                st.error("🌐 无法连接到AI服务器，请检查网络连接")

            except Exception as e:
                progress_bar.empty()
                status.update(label="❌ 系统异常", state="error")
                st.error(f"💥 系统错误: {str(e)}")

            finally:
                # 清理进度组件
                time.sleep(2)
                progress_bar.empty()
                if 'status_text' in locals():
                    status_text.empty()

                # 无论成功失败，最后都要把按钮恢复
                st.session_state.is_generating = False
                st.session_state.saved_prompt = ""  # 清空保存的prompt，让用户可以重新开始
                st.rerun()

# --- 7. 超现代化画廊展示区 ---

# 画廊标题和装饰
st.markdown("""
<div style="text-align: center; margin: 3rem 0 2rem 0;">
    <h2 style="color: white; font-size: 2.5rem; margin-bottom: 1rem;">
        🎨 AI 作品画廊
    </h2>
    <div style="height: 3px; background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #667eea);
                background-size: 300% 100%; animation: gradientShift 3s ease infinite;
                border-radius: 5px; margin: 0 auto; width: 200px;"></div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.history:
    # 空状态精美提示
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; margin: 2rem 0;">
        <div style="font-size: 5rem; margin-bottom: 2rem;">🎨</div>
        <h3 style="color: #667eea; font-size: 1.8rem; margin-bottom: 1rem;">
            开始您的创作之旅
        </h3>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; line-height: 1.6;">
            还没有生成的图像，<br>
            在上方描述您的创意，让AI为您创作独特的艺术作品吧！
        </p>
        <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <span style="background: rgba(102, 126, 234, 0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                ✨ 高质量生成
            </span>
            <span style="background: rgba(240, 147, 251, 0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                🚀 秒级出图
            </span>
            <span style="background: rgba(19, 180, 151, 0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                💾 一键下载
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    history_items = st.session_state.history

    # 获取统计信息但不立即显示
    total_images = len(history_items)
    total_duration = sum(float(item['duration'].rstrip('s')) for item in history_items)
    avg_duration = total_duration / total_images if total_images > 0 else 0

    # 动态列数布局
    rows = [history_items[i:i + gallery_cols] for i in range(0, len(history_items), gallery_cols)]

    for row_idx, row_items in enumerate(rows):
        cols = st.columns(gallery_cols)
        for idx, item in enumerate(row_items):
            with cols[idx]:
                # 创建画廊卡片
                st.markdown(f"""
                <div class="gallery-card">
                    <img src="data:image/png;base64,{item['base64_image']}"
                         alt="AI Generated Image"
                         loading="lazy">
                    <div class="image-info">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.9rem;">⏱️ {item['duration']}</span>
                            <span style="font-size: 0.9rem;">🌱 {item['seed']}</span>
                        </div>
                        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">
                            {item['time']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 下载按钮
                download_data = base64.b64decode(item['base64_image'])
                st.download_button(
                    label=f"💾 下载作品 #{item['id'][-6:]}",
                    data=download_data,
                    file_name=f"AI-Art-{item['id']}.png",
                    mime="image/png",
                    key=f"dl_{item['id']}",
                    use_container_width=True,
                    help="下载此AI生成的艺术作品"
                )

                # 分隔线
                if idx < len(row_items) - 1 or row_idx < len(rows) - 1:
                    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)

    # 分隔线
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, rgba(102, 126, 234, 0.3), rgba(240, 147, 251, 0.1), transparent); margin: 3rem 0;"></div>', unsafe_allow_html=True)

    # 统计信息区域 - 移到图片下方
    st.markdown('<h4 style="color: #667eea; margin-bottom: 1rem; text-align: center;">📊 创作统计</h4>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "🖼️ 作品总数",
            f"{total_images}",
            delta=None,
            help="本次会话生成的图片总数"
        )
    with col2:
        st.metric(
            "⚡ 平均耗时",
            f"{avg_duration:.1f}s",
            delta=None,
            help="所有图片的平均生成时间"
        )
    with col3:
        st.metric(
            "🕐 总时间",
            f"{total_duration:.0f}s",
            delta=None,
            help="累计创作时间"
        )

    # 底部装饰和更多功能
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem;">
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent);
                    border-radius: 5px; margin-bottom: 2rem;"></div>
        <p style="color: rgba(255,255,255,0.7); font-size: 1rem;">
            🎯 继续创作更多精彩作品<br>
            <span style="font-size: 0.9rem; opacity: 0.7;">每一张都是独一无二的AI艺术</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# 页脚区域
st.markdown("""
<footer style="margin-top: 4rem; padding: 2rem 0; border-top: 1px solid rgba(255,255,255,0.1);">
    <div style="text-align: center; color: rgba(255,255,255,0.6);">
        <p style="margin-bottom: 1rem;">
            <span style="display: inline-block; margin: 0 1rem;">
                🚀 <strong>极速生成</strong> - 秒级出图
            </span>
            <span style="display: inline-block; margin: 0 1rem;">
                🎨 <strong>高品质</strong> - 专业AI算法
            </span>
            <span style="display: inline-block; margin: 0 1rem;">
                💾 <strong>无限存储</strong> - 永久保存
            </span>
        </p>
        <p style="font-size: 0.9rem; opacity: 0.7;">
            Powered by Advanced AI Technology |
            <span style="color: #667eea;">ShowImageWeb</span> © 2025
        </p>
    </div>
</footer>
""", unsafe_allow_html=True)

# 性能优化：添加预加载和延迟加载
st.markdown("""
<script>
// 图片延迟加载优化
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.gallery-card img');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '0';
                setTimeout(() => {
                    img.style.transition = 'opacity 0.5s ease-in-out';
                    img.style.opacity = '1';
                }, 100);
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
});
</script>
""", unsafe_allow_html=True)

# 强制页面从顶部开始显示
st.markdown("""
<script>
// 激进的强制滚动到顶部
(function forceScrollToTop() {
    // 立即重置到顶部锚点
    function scrollToTopNow() {
        var topElement = document.getElementById('top');
        if (topElement) {
            topElement.scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'instant' });
        }
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        document.documentElement.scrollIntoView({ block: 'start', behavior: 'instant' });
    }

    // 立即执行
    scrollToTopNow();

    // DOM准备完成后
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', scrollToTopNow);
    } else {
        scrollToTopNow();
    }

    // 页面完全加载后多次执行
    window.addEventListener('load', function() {
        scrollToTopNow();
        setTimeout(scrollToTopNow, 10);
        setTimeout(scrollToTopNow, 100);
        setTimeout(scrollToTopNow, 500);
        setTimeout(scrollToTopNow, 1000);
    });

    // 覆盖所有可能的滚动方法
    var originalScrollTo = window.scrollTo;
    window.scrollTo = function() {
        scrollToTopNow();
        return originalScrollTo.apply(window, [0, 0]);
    };

    var originalScrollToOptions = window.scrollTo;
    window.scrollTo = function(options) {
        scrollToTopNow();
        return originalScrollToOptions.call(window, { top: 0, left: 0, behavior: 'instant' });
    };

    var originalScrollBy = window.scrollBy;
    window.scrollBy = function() {
        scrollToTopNow();
        return originalScrollBy.apply(window, [0, 0]);
    };

    var originalScrollIntoView = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = function() {
        if (this.id !== 'top') {
            scrollToTopNow();
        } else {
            return originalScrollIntoView.apply(this, [{ block: 'start', behavior: 'instant' }]);
        }
    };

    // 监听并阻止任何滚动
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 5 || document.documentElement.scrollTop > 5) {
            scrollToTopNow();
        }
    });

    // 监听并阻止任何DOM滚动
    document.documentElement.addEventListener('scroll', function() {
        if (document.documentElement.scrollTop > 5) {
            scrollToTopNow();
        }
    });

    document.body.addEventListener('scroll', function() {
        if (document.body.scrollTop > 5) {
            scrollToTopNow();
        }
    });

    // 页面可见性变化时
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setTimeout(scrollToTopNow, 100);
        }
    });
})();

// 防止浏览器记住滚动位置
window.addEventListener('beforeunload', function() {
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
});
</script>
""", unsafe_allow_html=True)