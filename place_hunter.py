import time

def crawl_naver_reviews():
    """
    네이버 플레이스에서 리뷰를 긁어오는 크롤링 로직 (예시 데이터 반환)
    실제 크롤링 코드나 API 호출 코드를 이 안에 구현하시면 됩니다.
    """
    print("🔍 네이버 플레이스 리뷰 크롤링 시작...")
    
    # 크롤링으로 수집했다고 가정하는 원본 리뷰 리스트
    collected_reviews = [
        {
            "id": 2001, # 원본 리뷰 고유 ID (original_id로 매칭됨)
            "store_name": "우리 매장 1호점",
            "content": "웨이팅이 너무 길고 직원이 불친절해요.",
            "sentiment": "negative",
            "keywords": "대기시간, 불친절",
            "rating": 1
        },
        {
            "id": 2002,
            "store_name": "우리 매장 1호점",
            "content": "음식이 정말 맛있고 친절합니다!",
            "sentiment": "positive",
            "keywords": "맛있다, 친절",
            "rating": 5
        }
    ]
    
    print(f"✨ 총 {len(collected_reviews)}개의 리뷰를 수집했습니다.")
    return collected_reviews

if __name__ == "__main__":
    reviews = crawl_naver_reviews()
    print(reviews)