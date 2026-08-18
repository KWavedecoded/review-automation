import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# place_hunter.py에서 수집 기능을 정상적으로 가져옴
from place_hunter import crawl_naver_reviews

load_dotenv()

# 환경변수 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_already_processed(original_id):
    """processed_reviews 테이블에서 이미 처리된 리뷰인지 원본 ID 기준으로 확인"""
    try:
        response = supabase.table("processed_reviews").select("id").eq("original_id", original_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"⚠️ 중복 조회 중 오류 발생: {e}")
        return False

def save_to_supabase(review_data):
    """정제된 리뷰 데이터를 processed_reviews 테이블에 적재"""
    try:
        supabase.table("processed_reviews").insert(review_data).execute()
        print(f"✅ processed_reviews 적재 완료 (Original ID: {review_data.get('original_id')})")
    except Exception as e:
        print(f"❌ Supabase 적재 실패: {e}")

def send_to_telegram(message):
    """텔레그램 봇을 통해 실시간 알림 메시지 전송"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ 텔레그램 설정 누락")
        return
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
    print("🚀 전체 파이프라인(수집 -> 검사 -> 저장 -> 알림) 실행 시작...")
    
    # 1. place_hunter.py를 통해 리뷰 수집
    raw_reviews = crawl_naver_reviews()

    for rev in raw_reviews:
        # 2. 중복 검사 (original_id 기준)
        if not is_already_processed(rev["id"]):
            payload = {
                "original_id": rev["id"],
                "sentiment": rev["sentiment"],
                "keywords": rev["keywords"]
            }
            
            # 3. processed_reviews 테이블에 적재
            save_to_supabase(payload)
            
            # 4. 부정 리뷰일 경우 텔레그램 알림 전송
            if rev["rating"] <= 2:
                notification_text = (
                    f"🚨 **부정 리뷰가 탐지되었습니다.**\n\n"
                    f"🏬 **매장명:** {rev['store_name']}\n"
                    f"⭐ **평점:** {rev['rating']}점\n"
                    f"📝 **내용:** {rev['content']}\n"
                    f"🏷️ **키워드:** {rev['keywords']}"
                )
                send_to_telegram(notification_text)
        else:
            print(f"⏩ 이미 처리된 리뷰입니다. (Original ID: {rev['id']})")