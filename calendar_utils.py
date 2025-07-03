from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta

# 환경 설정
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "credentials.json"
CALENDAR_ID = "primary"  # 또는 공유 캘린더 ID

# 캘린더 API 클라이언트 생성
def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=creds)
    return service

# 일정 등록 함수
def register_calendar_event(guarantee_data: dict):
    service = get_calendar_service()

    # 일정 제목 및 설명
    title = f"[보증종료] {guarantee_data['현장명']} - {guarantee_data['항목']}"
    description = (
        f"보증종류: {guarantee_data['증권종류']}\n"
        f"계약자: {guarantee_data['시공사']} / 대표: {guarantee_data['대표자']}\n"
        f"보증금액: {guarantee_data['보증금액']} / 계약금액: {guarantee_data['계약금액']}\n"
        f"계약일자: {guarantee_data['계약일자']} / 발급일자: {guarantee_data['발급일자']}\n"
        f"비고: {guarantee_data['특기사항']}"
    )

    # 종료일 변환 (문자열 → 날짜 객체)
    end_date_str = guarantee_data["보증기간"]["종료일"]  # 예: "2025-09-30"
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    end_date_plus_one = end_date + timedelta(days=1)

    # ISO 8601 형식으로 변환
    start_date_formatted = end_date.strftime("%Y-%m-%d")
    end_date_formatted = end_date_plus_one.strftime("%Y-%m-%d")

    # 이벤트 생성
    event = {
        "summary": title,
        "description": description,
        "start": {"date": start_date_formatted},
        "end": {"date": end_date_formatted},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 1 * 24 * 60},   # 하루 전 팝업
                {"method": "email", "minutes": 7 * 24 * 60},   # 일주일 전 이메일
            ],
        },
    }

    # Google Calendar에 등록
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
