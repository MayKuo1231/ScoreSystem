import streamlit as st
import pandas as pd
import altair as alt

# 1. 網頁基本設定
st.set_page_config(page_title="歷次校排查詢系統", page_icon="📊")

st.title("📊 歷次校排查詢系統")
st.write("請輸入座號與密碼（身分證後四碼）來查詢成績。")

# 讀取資料的函數 (加入快取機制，提升讀取速度)
@st.cache_data
def load_data():
    # 讀取 Excel 檔案，並將座號與密碼強制轉為字串格式，避免比對時發生型別錯誤
    df = pd.read_excel("score_data.xlsx", dtype={"座號": str, "密碼": str})
    return df

# 嘗試讀取資料庫
try:
    df = load_data()
except FileNotFoundError:
    st.error("找不到資料庫檔案 (score_data.xlsx)，請確認檔案是否已上傳至 GitHub。")
    st.stop()

# 2. 建立登入區塊
col1, col2 = st.columns(2)
with col1:
    # 這裡的提示文字已更新為 21
    student_id = st.text_input("座號 (例如: 1, 21)", max_chars=2)
with col2:
    password = st.text_input("密碼 (身分證後4碼)", type="password", max_chars=4)

# 3. 查詢邏輯與畫面顯示
# 使用 type="primary" 讓按鈕變成醒目的紅色
if st.button("查詢", type="primary"):
    if student_id and password:
        # 篩選符合條件的學生資料
        student_data = df[(df["座號"] == student_id) & (df["密碼"] == password)]
        
        if not student_data.empty:
            # 取得該名學生的姓名
            student_name = student_data.iloc[0]["姓名"]
            
            # 這裡的歡迎詞順序已經對調
            st.success(f"{student_name} 同學，登入成功！")
            
            # --- 資料整理與視覺化區塊 ---
            
            # 排除不要畫進折線圖的欄位 (保留後面的所有考試名稱與成績)
            score_cols = df.columns.drop(["座號", "姓名", "密碼"])
            
            # 取出該學生的歷次校排，轉換成適合畫圖的格式，並過濾掉還沒有成績的空值
            chart_data = student_data[score_cols].T.reset_index()
            chart_data.columns = ["考試名稱", "校排"]
            chart_data = chart_data.dropna()
            
            # 如果有成績紀錄，顯示最新成績與折線圖
            if not chart_data.empty:
                latest_exam = chart_data.iloc[-1]["考試名稱"]
                latest_rank = int(chart_data.iloc[-1]["校排"])
                
                # 顯示大大的最新校排數字
                st.subheader(f"🏆 最新校排 ({latest_exam})")
                st.metric(label="校排名次", value=latest_rank)
            
                # 繪製折線圖
                st.markdown("### 📈 歷次校排趨勢圖")
                
                # 使用 Altair 繪製，並設定 Y 軸反轉 (scale=alt.Scale(reverse=True))
                line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                    x=alt.X('考試名稱', sort=None, title='考試次數'), 
                    y=alt.Y('校排', scale=alt.Scale(reverse=True), title='校排名次'), 
                    tooltip=['考試名稱', '校排']
                ).properties(
                    height=400
                )
                
                st.altair_chart(line_chart, use_container_width=True)
            else:
                st.info("目前還沒有任何考試成績紀錄喔！")

        else:
            st.error("座號或密碼錯誤，請確認後重新輸入！")
    else:
        st.warning("請完整輸入座號與密碼！")
