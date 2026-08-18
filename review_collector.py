import os
import requests
from supabase import create_client
from dotenv import load_dotenv

# .env 파일 로드 시도
load_dotenv()

# 환경변수 가져오기 (없을 경우 직접 입력한 기본값 fallback 적용)
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://vbyevgwsxykclgfmirsm.supabase.co"
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") or "sb_publishable_-qIm2UGJ4wbf9sTTipnIcA_3JHiQKLH"

# 텔레그램 설정 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8744300114:AAEv7F2S9zmPk5Xe9Ui5p5cZland3JzZcrw"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "8752082139"

# Supabase 클라이언트 초기화
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def save_to_supabase(data):
    """
    Supabase의 store_reviews 테이블에 데이터를 삽입합니다.
    """
    try:
        response = supabase.table("store_reviews").insert(data).execute()
        print("Supabase 저장 완료")
    except Exception as e:
        print(f"Supabase 저장 실패: {e}")

def send_to_telegram(message):
    """
    텔레그램 봇을 통해 실시간 알림 메시지를 직접 전송합니다.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("텔레그램 전송 완료")
        else:
            print(f"텔레그램 전송 실패: {response.text}")
    except Exception as e:
        print(f"텔레그램 전송 오류: {e}")

if __name__ == "__main__":
    dummy_review = {
        "store_name": "테스트 매장",
        "review_text": "Supabase 및 텔레그램 직결 연동 테스트 완료.",
        "rating": 5
    }
    
    print("데이터 처리 시작...")
    
    # 1. Supabase 적재
    save_to_supabase(dummy_review)
    
    # 2. 텔레그램 직발송 메시지 구성 및 전송
    notification_text = (
        f"🚨 **새로운 리뷰가 등록되었습니다.**\n\n"
        f"🏬 **매장명:** {dummy_review['store_name']}\n"
        f"⭐ **평점:** {dummy_review['rating']}점\n"
        f"📝 **내용:** {dummy_review['review_text']}"
    )
    send_to_telegram(notification_text)