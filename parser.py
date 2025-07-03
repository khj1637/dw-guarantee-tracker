import re
from datetime import datetime

def parse_guarantee_text(text: str) -> dict:
    def extract(pattern, group=1, default=""):
        match = re.search(pattern, text)
        return match.group(group).strip() if match else default

    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y년 %m월 %d일").strftime("%Y-%m-%d")
        except:
            return ""

    # 금액
    계약금액 = extract(r"계.?약.?금.?액.*?(₩[\d,]+)")
    보증금액 = extract(r"보.?증.?금.?액.*?(₩[\d,]+)")

    # 날짜
    계약일자 = parse_date(extract(r"계.?약.?일.?자[:：]?\s*([0-9]{4}년\s*[0-9]{1,2}월\s*[0-9]{1,2}일)"))
    발급일자 = parse_date(extract(r"(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)\s*발급"))

    # 보증기간 or 하자담보책임기간
    기간 = re.search(r"(하자.?담보.?책임.?기간|보.?증.?기.?간).*?(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)[^\d]+(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)", text)
    시작일 = parse_date(기간.group(2)) if 기간 else ""
    종료일 = parse_date(기간.group(3)) if 기간 else ""

    # 계약자, 대표자, 특기사항
    시공사 = extract(r"(계약자|계약자명|시공사)[:：]?\s*(.*?주식회사|.*?\(주\)|.*?주)", 2)
    대표자 = extract(r"대표자[:：]?\s*([^\s\n]+)")
    특기사항 = extract(r"특기사항[:：]?\s*(.*)", 1)
    현장명 = extract(r"(계약명|공사명|현장명)[:：]?\s*(.*?)\s*(계약일자|계약이행기간|보증기간)", 2)
    항목 = extract(r"항목[:：]?\s*(.*)", 1) or extract(r"보증서 종류[:：]?\s*(.*)", 1)

    return {
        "현장명": 현장명 or "추출불가",
        "증권종류": "하자보수증서",
        "항목": 항목 or "하자보수",
        "보증금액": 보증금액 or "미기재",
        "계약금액": 계약금액 or "미기재",
        "보증기간": {
            "시작일": 시작일,
            "종료일": 종료일
        },
        "계약일자": 계약일자,
        "시공사": 시공사 or "미확인",
        "대표자": 대표자 or "미확인",
        "특기사항": 특기사항 or "해당사항없음",
        "발급일자": 발급일자
    }
