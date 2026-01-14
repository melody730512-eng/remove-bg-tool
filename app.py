import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# --- 頁面設定 ---
st.set_page_config(page_title="混合去背神器", layout="wide")
st.title("🛠️ Vibe Coding: 混合去背神器 (紅框+綠筆)")
st.markdown("""
**終極操作指南：**
1. 🟥 **紅色框 (挖空)**：切換到此模式，快速拉框框挖掉大背景。
2. 🟩 **綠色筆 (救援)**：切換到此模式，用塗抹的方式，精細地把誤刪的地方補回來！
**Vibe Logic：** 綠筆塗過的地方擁有最高優先權 (救援成功)。
""")

# --- 主畫面 ---
uploaded_file = st.file_uploader("請將圖片拖曳到這裡 (JPG/PNG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # 讀取原始圖片
    original_image = Image.open(uploaded_file).convert("RGBA")
    img_width, img_height = original_image.size

    # 建立兩欄佈局
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. 工具操作區")
        
        # --- 工具選擇 (關鍵修改) ---
        tool_mode = st.radio("選擇你的武器：", ("🟥 紅框 (拉框挖空)", "🟩 綠筆 (塗抹救援)"), horizontal=True)
        
        # --- 動態設定畫布參數 ---
        if tool_mode == "🟥 紅框 (拉框挖空)":
            # 紅框模式設定
            drawing_mode = "rect"       # 矩形模式
            stroke_color = "#ff0000"    # 紅色邊框
            fill_color = "rgba(255, 0, 0, 0.3)" # 半透明紅填充
            stroke_width = 2            # 框框線條固定細一點
            st.caption("目前模式：拉出矩形框框")
        else:
            # 綠筆模式設定
            drawing_mode = "freedraw"   # 自由塗抹模式
            stroke_color = "#00ff00"    # 純綠色筆觸
            fill_color = "rgba(0, 255, 0, 0)" # 塗抹不需要填充色
            # 只有在綠筆模式才需要調整筆刷大小
            stroke_width = st.slider("🟩 綠筆大小", 1, 50, 15)
            st.caption("目前模式：自由塗抹救援")

        # --- 建立畫布 (參數是動態的) ---
        canvas_result = st_canvas(
            fill_color=fill_color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=original_image,
            update_streamlit=True,
            height=img_height,
            width=img_width,
            drawing_mode=drawing_mode, # 這裡會根據上面的選擇變動
            key="canvas_hybrid",
        )

    with col2:
        st.subheader("2. 預覽結果")
        
        # --- 核心處理邏輯 (使用影像遮罩法) ---
        # 檢查畫布上是否有內容
        if canvas_result.image_data is not None:
            # 1. 取得畫布的作畫結果 (這是一張 RGBA 圖片，上面有你畫的紅框和綠筆跡)
            mask_data = canvas_result.image_data
            
            # 2. 把原始圖片轉成陣列準備處理
            img_array = np.array(original_image)

            # 3. Vibe Logic: 分析畫布顏色
            # 找出哪些地方有畫紅色 (R通道 > 0 且 G通道沒有東西)
            is_red_area = (mask_data[:, :, 0] > 0) & (mask_data[:, :, 1] == 0)
            # 找出哪些地方有畫綠色 (G通道 > 0)
            is_green_area = (mask_data[:, :, 1] > 0)

            # 4. 執行動作
            # 動作 A: 把紅色區域變透明 (Alpha = 0)
            img_array[is_red_area, 3] = 0
            
            # 動作 B (救援): 把綠色區域變回不透明 (Alpha = 255)，這會覆蓋掉動作 A
            img_array[is_green_area, 3] = 255

            # 5. 轉回圖片
            processed_image = Image.fromarray(img_array)
            
            # 顯示結果
            st.image(processed_image, use_column_width=True)

            # --- 下載按鈕 ---
            st.markdown("---")
            from io import BytesIO
            buf = BytesIO()
            processed_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="📥 下載處理好的 PNG",
                data=byte_im,
                file_name="hybrid_transparent.png",
                mime="image/png"
            )
        else:
            st.info("👈 請在左側選擇工具並開始操作")
