import streamlit as st
import json, os, subprocess, sys
import pandas as pd

st.set_page_config(page_title="AI Autonomous QA Agent Dashboard", layout="wide", page_icon="🤖")

st.title("🤖 AI-Driven Autonomous QA Agent Dashboard")
st.markdown("Hệ thống kiểm thử tự động thông minh tích hợp Google Gemini AI và Playwright cho website thương mại điện tử.")

# Sidebar điều khiển
st.sidebar.header("🕹️ Bảng điều khiển Pipeline")
target_url = st.sidebar.text_input("Website cần Test", "https://www.saucedemo.com")
user_story = st.sidebar.text_area("User Story / Yêu cầu", "Là người dùng, tôi có thể đăng nhập bằng username và password để xem danh sách sản phẩm.")

if st.sidebar.button("🚀 Chạy toàn bộ Pipeline QA"):
    with st.spinner("Đang thực thi quy trình QA tự động (Sinh test -> Chạy Playwright -> Phân tích AI)..."):
        result = subprocess.run(
            [sys.executable, "main.py", user_story, "--url", target_url],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            st.sidebar.success("✅ Chạy pipeline thành công hoàn toàn!")
        else:
            st.sidebar.error("❌ Có lỗi xảy ra trong quá trình chạy!")
            st.sidebar.code(result.stderr or result.stdout)

# Khu vực hiển thị kết quả chính
tab1, tab2, tab3 = st.tabs(["📊 Tổng quan & Biểu đồ", "📋 Danh sách Test Cases", "🐞 Báo cáo Lỗi (Bug Reports)"])

with tab1:
    st.subheader("Trạng thái thực thi Test Cases mới nhất")
    results_path = "output/results.json"
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        
        passed_count = sum(1 for r in results if r["passed"])
        failed_count = len(results) - passed_count
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng số Test Cases", len(results))
        col2.metric("Số lượng Pass", passed_count, delta="Ổn định")
        col3.metric("Số lượng Fail", failed_count, delta="-1" if failed_count > 0 else "0", delta_color="inverse")
        
        df_res = pd.DataFrame(results)
        df_res["Status"] = df_res["passed"].apply(lambda x: "PASS" if x else "FAIL")
        st.bar_chart(df_res["Status"].value_counts())
        
        st.markdown("### Dữ liệu chi tiết thực thi")
        st.dataframe(df_res, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu kết quả test. Hãy bấm nút chạy pipeline ở sidebar bên trái.")

with tab2:
    st.subheader("Bộ Test Cases sinh bởi AI")
    cases_path = "output/cases.json"
    if os.path.exists(cases_path):
        with open(cases_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
        st.json(cases)
    else:
        st.warning("Chưa tìm thấy file cases.json.")

with tab3:
    st.subheader("Báo cáo lỗi chi tiết (Bug Reports từ AI)")
    bug_dir = "output/bug_reports"
    if os.path.exists(bug_dir) and os.listdir(bug_dir):
        bug_files = os.listdir(bug_dir)
        selected_bug = st.selectbox("Chọn báo cáo lỗi để xem:", bug_files)
        if selected_bug:
            with open(os.path.join(bug_dir, selected_bug), "r", encoding="utf-8") as bf:
                st.markdown(bf.read())
            
            img_id = selected_bug.replace(".md", "")
            img_path = f"output/screenshots/{img_id}.png"
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Bằng chứng màn hình cho lỗi: {img_id}")
    else:
        st.success("Tuyệt vời! Không có lỗi nghiêm trọng (real_bug) nào được ghi nhận.")