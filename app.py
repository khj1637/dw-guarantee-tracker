import streamlit as st
import os
import pandas as pd
from tempfile import NamedTemporaryFile
from datetime import datetime

from ocr_utils import pdf_to_text
from parser import parse_guarantee_text
from calendar_utils import register_calendar_event

# 초기화
st.set_page_config(page_title="하자보수증권 등록 시스템", layout="wide")

# 파일 업로드
st.title("📄 하자보수 증권 PDF 업로드")
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

if 'guarantee_list' not in st.session_state:
    st.session_state.guarantee_list = []

if uploaded_file:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # 1. OCR
        text = pdf_to_text(tmp_path)

        # 2. 파싱
        data = parse_guarantee_text(text)

        # 3. 캘린더 등록
        register_calendar_event(data)

        # 4. 리스트 저장
        st.session_state.guarantee_list.append(data)

        st.success(f"✅ {data['현장명']} 등록 완료")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

    finally:
        # 5. 업로드된 PDF 삭제
        os.remove(tmp_path)

# 6. 테이블 표시
st.subheader("📋 등록된 보증 리스트")

# 날짜 비교로 상태 추가
def get_status(start, end):
    today = datetime.today().date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    return "✅ 유효" if today <= end_date else "❌ 만료"

table_data = []
for i, item in enumerate(st.session_state.guarantee_list):
    status = get_status(item["보증기간"]["시작일"], item["보증기간"]["종료일"])
    table_data.append({
        "No": i + 1,
        "현장명": item["현장명"],
        "증권종류": item["증권종류"],
        "항목": item["항목"],
        "기간": f"{item['보증기간']['시작일']} ~ {item['보증기간']['종료일']}",
        "비고": status
    })

df = pd.DataFrame(table_data)

# 페이지네이션 (안전하게)
page_size = 10
total = len(df)

if total > 0:
    max_page = (total - 1) // page_size + 1
    page_num = st.number_input("페이지 번호", min_value=1, max_value=max_page, step=1)
    
    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size

    st.dataframe(df.iloc[start_idx:end_idx])
else:
    st.info("등록된 보증서가 없습니다.")

# 삭제 기능 (간단 구현)
delete_index = st.number_input("삭제할 No 입력 (선택사항)", min_value=0, max_value=total, step=1)
if st.button("🗑️ 만료 삭제") and delete_index > 0:
    del st.session_state.guarantee_list[delete_index - 1]
    st.experimental_rerun()
