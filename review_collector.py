import os
import requests
from supabase import create_client
from dotenv import load_dotenv

# .env 파일 로드 시도
load_dotenv()

# 환경변수 가져오기 (없을 경우 직접 입력한 기본값 fallback 적용)
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://vbyevgwsxykclgfmirsm.supabase.co"
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") or "sb_publishable_-qIm2UGJ4wbf9sTTipnIcA_3JHiQKLH"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL") or "http://localhost:5678/webhook-test/review-webhook"

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

def send_to_n8n(data):
    """
    데이터를 n8n 웹훅으로 전송합니다.
    """
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=data)
        print(f"n8n 전송 결과: {response.status_code}")
    except Exception as e:
        print(f"n8n 전송 실패: {e}")

if __name__ == "__main__":
    dummy_review = {
        "store_name": "테스트 매장",
        "review_text": "Supabase 및 n8n 연동 직결 테스트 완료.",
        "rating": 5
    }
    
    print("데이터 처리 시작...")
    save_to_supabase(dummy_review)
    send_to_n8n(dummy_review)