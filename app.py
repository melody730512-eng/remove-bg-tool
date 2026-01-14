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
            fill_color = "rgba(255, 0, 0, 0.3)"
            stroke_width = 2
        else:
            drawing_mode = "freedraw"
            stroke_color = "#00ff00"
            fill_color = "rgba(0, 255, 0, 0)"
            stroke_width = st.slider("🟩 綠筆大小", 1, 50, 15)

        # --- 建立畫布 ---
        canvas_result = st_canvas(
            fill_color=fill_color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=canvas_background, # 使用強制顯影的圖片
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode=drawing_mode,
            key=f"canvas_{uploaded_file.name}",
        )

    with col2:
        st.subheader(f"2. 預覽結果 ({orig_w}x{orig_h})")
        
        # --- 核心處理邏輯 ---
        if canvas_result.image_data is not None:
            # 取得畫布操作痕跡
            small_mask_data = canvas_result.image_data
            
            # 放大遮罩回原尺寸
            small_mask_img = Image.fromarray(small_mask_data.astype('uint8'), mode="RGBA")
            full_size_mask_img = small_mask_img.resize((orig_w, orig_h), resample=Image.NEAREST)
            full_mask_data = np.array(full_size_mask_img)

            # 準備原始高清圖
            img_array = np.array(original_image)

            # 執行去背邏輯
            is_red_area = (full_mask_data[:, :, 0] > 0) & (full_mask_data[:, :, 1] == 0)
            is_green_area = (full_mask_data[:, :, 1] > 0)

            img_array[is_red_area, 3] = 0   # 挖空
            img_array[is_green_area, 3] = 255 # 救援

            # 顯示與下載
            processed_image = Image.fromarray(img_array)
            st.image(processed_image, caption="預覽圖 (已縮小顯示)", use_column_width=True)

            st.markdown("---")
            buf = BytesIO()
            processed_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="💎 下載高清原圖 PNG (1920x1080)",
                data=byte_im,
                file_name="hd_transparent.png",
                mime="image/png"
            )
        else:
            st.info("👈 請在左側選擇工具並開始操作")
