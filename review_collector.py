import os
import requests
from supabase import create_client

# .env 로드 없이 직접 하드코딩 방식으로 확실하게 설정 (테스트용)
SUPABASE_URL = "https://vbyevgwsxyklcgfmirsm.supabase.co"
SUPABASE_KEY = "sb_publishable_-qIm2UGJ4wbf9sTTipnIcA_3JHiQKLH"
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/review-webhook"

# Supabase 클라이언트 초기화
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_supabase(data):
    try:
        response = supabase.table("reviews").insert(data).execute()
        print("Supabase 저장 완료")
    except Exception as e:
        print(f"Supabase 저장 실패 (테이블 확인 필요): {e}")

def send_to_n8n(data):
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