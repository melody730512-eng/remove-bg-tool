import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

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
    # 設定顯示寬度為 800px (這只是給你看的，不會影響輸出)
    display_width = 800
    
    # 計算縮放倍率 (Scale Factor)
    if orig_w > display_width:
        scale_factor = orig_w / display_width
        display_height = int(orig_h / scale_factor)
        # 產生縮小版圖片放入畫布
        display_image = original_image.resize((display_width, display_height))
    else:
        scale_factor = 1.0
        display_image = original_image
        display_height = orig_h

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

        # --- 建立畫布 (使用縮小版 display_image) ---
        canvas_result = st_canvas(
            fill_color=fill_color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=display_image, # 這裡放替身圖
            update_streamlit=True,
            height=display_height,
            width=display_width, # 固定寬度，保證流暢
            drawing_mode=drawing_mode,
            key=f"canvas_{uploaded_file.name}",
        )

    with col2:
        st.subheader(f"2. 預覽結果 ({orig_w}x{orig_h})")
        
        # --- 核心處理邏輯 (還原倍率) ---
        if canvas_result.image_data is not None:
            # 1. 取得畫布上的操作痕跡 (這是縮小版的遮罩)
            small_mask_data = canvas_result.image_data
            
            # 2. 將遮罩「放大」回原始尺寸
            # 把 canvas 的 array 轉成 Image 物件
            small_mask_img = Image.fromarray(small_mask_data.astype('uint8'), mode="RGBA")
            # 關鍵步驟：重新放大到原始尺寸 (Resample 使用 Nearest 保持邊緣銳利，或 Bilinear 柔和)
            full_size_mask_img = small_mask_img.resize((orig_w, orig_h), resample=Image.NEAREST)
            # 轉回 numpy array
            full_mask_data = np.array(full_size_mask_img)

            # 3. 準備原始高清圖的陣列
            img_array = np.array(original_image)

            # 4. Vibe Logic (跟之前一樣，但這次是用放大後的遮罩)
            # 找出紅色區域 (挖空)
            is_red_area = (full_mask_data[:, :, 0] > 0) & (full_mask_data[:, :, 1] == 0)
            # 找出綠色區域 (救援)
            is_green_area = (full_mask_data[:, :, 1] > 0)

            # 5. 執行動作 (在高清圖上修改)
            img_array[is_red_area, 3] = 0   # 變透明
            img_array[is_green_area, 3] = 255 # 救回來

            # 6. 轉回圖片
            processed_image = Image.fromarray(img_array)
            
            # 為了讓預覽不要撐爆網頁，預覽圖也縮小顯示，但下載的是大圖
            st.image(processed_image, caption="預覽圖 (已縮小顯示)", use_column_width=True)

            # --- 下載按鈕 ---
            st.markdown("---")
            st.success(f"處理完成！圖片尺寸維持：{processed_image.size[0]} x {processed_image.size[1]}")
            
            from io import BytesIO
            buf = BytesIO()
            # 儲存時使用原始的高清圖
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
            
