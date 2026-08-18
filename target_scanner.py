import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# 기존 모듈 및 신규 크로스 체크 모듈 임포트
from target_scanner import scan_target_places
from place_hunter import crawl_naver_reviews
from trend_cross_checker import cross_check_with_google_trends

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_already_processed(original_id):
    try:
        response = supabase.table("processed_reviews").select("id").eq("original_id", original_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"⚠️ 중복 조회 중 오류 발생: {e}")
        return False

def save_to_supabase(review_data):
    try:
        supabase.table("processed_reviews").insert(review_data).execute()
        print(f"✅ processed_reviews 적재 완료 (Original ID: {review_data.get('original_id')})")
    except Exception as e:
        print(f"❌ Supabase 적재 실패: {e}")

def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"텔레그램 전송 오류: {e}")

if __name__ == "__main__":
    print("🚀 상용 자동화 파이프라인 (트렌드 검증 + 타겟 스캔 + 리뷰 수집) 가동...")
    
    base_query = "부산 해운대 맛집"
    
    # 1. 구글 트렌드 크로스 체크로 거시적 시장성 및 확장 키워드 확보
    trend_data = cross_check_with_google_trends(base_query)
    
    if not trend_data["is_valid"]:
        print("⚠️ 거시적 검색 수요가 기준치 미달입니다. 파이프라인을 일시 중단합니다.")
    else:
        print(f"🎯 시장성 검증 통과! 활용 키워드 리스트: {trend_data['rising_keywords']}")
        
        # 2. 고가치 타겟 매장 자동 발굴
        targets = scan_target_places(base_query)
        
        for target in targets:
            print(f"🔍 타겟 분석 중: {target['store_name']} (ID: {target['place_id']})")
            
            # 3. 해당 타겟의 리뷰 수집
            raw_reviews = crawl_naver_reviews(target['place_id'])

            for rev in raw_reviews:
                if not is_already_processed(rev["id"]):
                    # 트렌드에서 건진 확장 키워드를 메타데이터에 결합
                    enhanced_keywords = f"{rev['keywords']}, 연관트렌드: {', '.join(trend_data['rising_keywords'])}"
                    
                    payload = {
                        "original_id": rev["id"],
                        "sentiment": rev["sentiment"],
                        "keywords": enhanced_keywords
                    }
                    save_to_supabase(payload)
                    
                    # 4. 부정 리뷰 실시간 알림
                    if rev["rating"] <= 2:
                        notification_text = (
                            f"🚨 **[하이 레버리지 모니터링] 부정 리뷰 탐지**\n\n"
                            f"🏬 **매장명:** {target['store_name']}\n"
                            f"⭐ **평점:** {rev['rating']}점\n"
                            f"📝 **내용:** {rev['content']}\n"
                            f"🏷️ **키워드:** {enhanced_keywords}"
                        )
                        send_to_telegram(notification_text)