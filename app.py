import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

# --- 頁面設定 ---
st.set_page_config(page_title="高清去背神器", layout="wide")
st.title("💎 Vibe Coding: 高清去背神器 (替身模式)")
st.markdown("""
**特點：**
* 即使原圖是 **4K 或 1920x1080**，操作依然絲滑流暢。
* **下載結果保證 100% 原解析度**，絕不壓縮！
""")

# --- 主畫面 ---
uploaded_file = st.file_uploader("請將圖片拖曳到這裡 (JPG/PNG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # 1. 讀取原始圖片 (這是高清原檔，絕對不動它)
    original_image = Image.open(uploaded_file).convert("RGBA")
    orig_w, orig_h = original_image.size

    # 2. 製作「替身」圖片 (Proxy)
    display_width = 800
    
    # 計算縮放倍率
    if orig_w > display_width:
        scale_factor = orig_w / display_width
        display_height = int(orig_h / scale_factor)
        display_image = original_image.resize((display_width, display_height))
    else:
        scale_factor = 1.0
        display_image = original_image
        display_height = orig_h

    # === 關鍵修正：強制顯影魔法 ===
    # 將顯示用的圖片強制轉為 RGB (不透明)，解決 PNG 變白的問題
    # 這只會影響「螢幕上看到的」，不會影響「下載的去背結果」
    canvas_background = display_image.convert("RGB")

    # 建立兩欄佈局
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. 工具操作區")
        
        # --- 工具選擇 ---
        tool_mode = st.radio("選擇你的武器：", ("🟥 紅框 (拉框挖空)", "🟩 綠筆 (塗抹救援)"), horizontal=True)
        
        # --- 動態設定畫布參數 ---
        if tool_mode == "🟥 紅框 (拉框挖空)":
            drawing_mode = "rect"
            stroke_color = "#ff0000"
            fill_color = "rgba(255, 0
