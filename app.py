import streamlit as st
import pandas as pd
import altair as alt

# 設定網頁標題與寬度
st.set_page_config(page_title="校排查詢系統", layout="centered")

# 1. 讀取 Excel 資料 (裝甲升級版：自動過濾小數點與空白)
@st.cache_data
def load_data():
    df = pd.read_excel('score_data.xlsx')
    # 強制轉為字串，並且切除所有隱藏的 ".0"，最後再把前後空白消滅
    df['座號'] = df['座號'].astype(str).str.split('.').str[0].str.strip()
    df['密碼'] = df['密碼'].astype(str).str.split('.').str[0].str.strip()
    return df

st.title("📊 歷次校排查詢系統")

try:
    df = load_data()
except FileNotFoundError:
    st.error("找不到資料檔 (score_data.xlsx)，請確認檔案是否放在同一資料夾。")
    st.stop()

st.markdown("請輸入座號與密碼（身分證後四碼）來查詢成績。")

# 2. 建立登入區塊
col1, col2 = st.columns(2)
with col1:
    student_id = st.text_input("座號 (例如: 1, 21)", max_chars=2)
with col2:
    # type="password" 會把輸入內容變成隱藏星號
    password = st.text_input("密碼 (身分證後4碼)", type="password", max_chars=4)

if st.button("查詢", type="primary"):
    if student_id and password:
        # 3. 驗證資料：雙重確保輸入的文字與 Excel 的文字完全一致，不含空白
        target_student = df[(df['座號'].astype(str).str.strip() == student_id.strip()) & (df['密碼'].astype(str).str.strip() == password.strip())]
        
        if not target_student.empty:
            # 取得該名學生的姓名
            student_name = target_student['姓名'].values[0]
            st.success(f"登入成功！歡迎，{student_name} 同學")
            
            # 排除非成績欄位，只留下考試成績
            score_data = target_student.drop(columns=['座號', '姓名', '密碼']).iloc[0]
            
            # 濾除還沒考（空白）的欄位
            valid_scores = score_data.dropna()
            
            if not valid_scores.empty:
                # 抓取最後一筆資料作為「最新校排」
                latest_exam = valid_scores.index[-1]
                latest_rank = valid_scores.iloc[-1]
                
                st.subheader(f"🏆 最新校排 ({latest_exam})")
                st.metric(label="校排名次", value=int(latest_rank))
                
                st.divider()
                
                # 4. 繪製歷次成績趨勢圖
                st.subheader("📈 歷次校排趨勢")
                # 將資料整理成可以畫圖的 DataFrame
                chart_df = pd.DataFrame({
                    "考試次數": valid_scores.index,
                    "校排名": valid_scores.values
                })
                
                # 改用 Altair 繪圖，鎖定 X 軸為 Excel 原始順序，並反轉 Y 軸
                chart = alt.Chart(chart_df).mark_line(point=True).encode(
                    x=alt.X('考試次數', sort=None, title=''), # sort=None 強制不按字母排序
                    y=alt.Y('校排名', scale=alt.Scale(reverse=True), title='校排名'), # reverse=True 讓數字小的在最上方
                    tooltip=['考試次數', '校排名'] # 滑鼠移到點上會顯示詳細資訊
                )
                
                st.altair_chart(chart, use_container_width=True)
                st.caption("提示：折線圖越往上，代表校排成績越好喔！")
            else:
                st.info("目前還沒有任何成績資料。")
        else:
            st.error("❌ 座號或密碼錯誤，請重新確認。")
    else:
        st.warning("⚠️ 請完整輸入座號與密碼。")
