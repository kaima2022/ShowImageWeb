import streamlit as st
import requests
import base64
import time
import random
from datetime import datetime

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="Z-Image-Turbo Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 自定义 CSS (美化核心) ---
# 移除了可能导致图片变小的 stImage CSS 样式
st.markdown("""
<style>
    /* 全局字体和背景微调 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 标题样式 */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1e1e1e;
        letter-spacing: -1px;
    }
    
    /* 卡片容器样式 */
    .css-card {
        border-radius: 15px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }

    /* 侧边栏美化 */
    section[data-testid="stSidebar"] {
        background-color: #111827; /* 深色侧边栏 */
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #e5e7eb !important;
    }
    
    /* 按钮美化 */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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

def clear_history():
    st.session_state.history = []

def start_generating():
    """点击按钮时的回调：设置状态为生成中"""
    st.session_state.is_generating = True

# --- 4. 侧边栏配置区 ---
with st.sidebar:
    st.title("🎛️ 控制台")
    st.markdown("---")
    
    st.subheader("API 配置")
    api_base_url = st.text_input(
        "Base URL", 
        value="https://z-api.aioec.tech", 
        help="默认为官方 API 地址"
    )
    api_key = st.text_input("API Key", type="password", placeholder="sk-...")
    
    st.markdown("---")
    st.subheader("生成参数")
    seed_input = st.number_input("Seed (随机种子)", value=42, step=1)
    use_random = st.toggle("使用随机种子", value=True)
    
    st.markdown("---")
    st.subheader("界面设置")
    # 添加列数选择，解决图片太小的问题
    # 默认改回 2，因为修复 CSS 后图片会自动撑满列宽，不需要强制单列
    gallery_cols = st.slider("画廊列数", min_value=1, max_value=4, value=2, help="列数越少，单张图片越大")

    st.markdown("---")
    # 显示历史记录数量
    history_count = len(st.session_state.history)
    st.metric("已生成作品", f"{history_count} 张")
    
    if history_count > 0:
        if st.button("🗑️ 清空历史记录", type="secondary"):
            clear_history()
            st.rerun()

# --- 5. 主工作区 ---
st.title("🎨 Z-Image Studio")
st.markdown("#### High-Performance AI Image Generation")

# 输入区域容器
with st.container():
    # 使用列布局让输入框和按钮看起来更紧凑
    prompt_col, btn_col = st.columns([4, 1])
    
    with prompt_col:
        prompt = st.text_area(
            "Prompt", 
            placeholder="Describe your imagination here... (e.g., A futuristic city in glass bottle, 8k resolution)",
            height=100,
            label_visibility="collapsed",
            disabled=st.session_state.is_generating # 生成时禁用输入
        )
    
    with btn_col:
        st.write("") # 占位符
        st.write("") 
        # 按钮逻辑：
        # 1. on_click=start_generating: 点击瞬间把 session_state.is_generating 设为 True
        # 2. disabled=st.session_state.is_generating: 如果正在生成，按钮变灰
        generate_btn = st.button(
            "✨ 立即生成" if not st.session_state.is_generating else "⏳ 生成中...", 
            type="primary", 
            use_container_width=True, 
            disabled=st.session_state.is_generating,
            on_click=start_generating
        )

# --- 6. 生成逻辑 (通过状态控制) ---
if st.session_state.is_generating:
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
        endpoint = f"{api_base_url.rstrip('/')}/proxy/generate"
        final_seed = int(time.time() * 1000) % 1000000000 if use_random else int(seed_input)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt, "seed": final_seed}
        
        # 显示加载状态
        with st.status("🚀 正在调用 GPU 算力...", expanded=True) as status:
            start_time = time.time()
            try:
                st.write("正在连接 API...")
                response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    st.write("接收数据中...")
                    data = response.json()
                    base64_str = data.get("base64")
                    
                    if base64_str:
                        image_bytes = base64.b64decode(base64_str)
                        duration = time.time() - start_time
                        
                        # ✅ 存入历史记录
                        add_to_history(prompt, image_bytes, final_seed, duration)
                        
                        status.update(label="✅ 生成完成!", state="complete", expanded=False)
                        st.balloons() 
                    else:
                        status.update(label="❌ 数据解析失败", state="error")
                        st.error("API 返回成功但无图片数据")
                else:
                    status.update(label="❌ 请求失败", state="error")
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                status.update(label="❌ 发生异常", state="error")
                st.error(f"Connection Error: {str(e)}")
            
            finally:
                # 无论成功失败，最后都要把按钮恢复
                st.session_state.is_generating = False
                st.rerun()

# --- 7. 画廊展示区 (核心功能) ---
st.markdown("---")
st.subheader(f"🖼️ 作品画廊 ({len(st.session_state.history)})")

if not st.session_state.history:
    st.info("👋 还没有生成的作品，快去输入提示词试试吧！")
else:
    history_items = st.session_state.history
    
    # 使用动态列数布局
    # 将列表切片，每 gallery_cols 个一组
    rows = [history_items[i:i + gallery_cols] for i in range(0, len(history_items), gallery_cols)]
    
    for row_items in rows:
        cols = st.columns(gallery_cols)
        for idx, item in enumerate(row_items):
            with cols[idx]:
                with st.container(border=True):
                    # 使用HTML强制图片撑满容器
                    img_html = f"""
                    <img src="data:image/png;base64,{item['base64_image']}"
                         style="width: 100%; height: auto; object-fit: cover; border-radius: 8px;">
                    """
                    st.markdown(img_html, unsafe_allow_html=True)
                    st.caption(f"⏱️ {item['duration']} | 🌱 {item['seed'] if item['seed'] else 'Random'}")
                    
                    # 下载时将base64转换回字节数据
                    download_data = base64.b64decode(item['base64_image'])
                    st.download_button(
                        label="⬇️ 下载",
                        data=download_data,
                        file_name=f"z-image-{item['id']}.png",
                        mime="image/png",
                        key=f"dl_{item['id']}",
                        use_container_width=True
                    )