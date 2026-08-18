from pytrends.request import TrendReq
import pandas as pd

def cross_check_with_google_trends(keyword="해운대 맛집"):
    """
    상업적 이용이 가능한 Apache 2.0 라이선스의 pytrends를 활용하여
    구글 트렌드 거시적 검색 수요와 연관 급상승 키워드를 크로스 체크합니다.
    """
    print(f"📊 [Trend Cross-Check] '{keyword}' 키워드 거시 시장성 분석 중...")
    
    try:
        # pytrends 객체 생성 (한국 지역 및 타임존 설정)
        pytrends = TrendReq(hl='ko-KR', tz=540)
        
        # 페이로드 빌드 (최근 1개월 기준)
        pytrends.build_payload([keyword], timeframe='today 1-m', geo='KR')
        
        # 시간대별 관심도 데이터 수집
        data = pytrends.interest_over_time()
        
        if data.empty or keyword not in data.columns:
            print("⚠️ 구글 트렌드 데이터가 비어 있습니다.")
            return {"score": 0, "rising_keywords": [], "is_valid": False}
        
        # 최근 7일간 평균 검색 관심도 점수 산출 (0 ~ 100 스케일)
        recent_interest = float(data[keyword].tail(7).mean())
        
        # 연관 급상승 검색어(Related Queries) 추출
        related_queries = pytrends.related_queries()
        rising_keywords = []
        if keyword in related_queries and 'rising' in related_queries[keyword]:
            df_rising = related_queries[keyword]['rising']
            if df_rising is not None and not df_rising.empty:
                rising_keywords = df_rising['query'].head(3).tolist()

        # 하이 레버리지 기준 판정 (관심도 40 이상 또는 급상승어 존재 시 유효 타겟)
        is_high_leverage = recent_interest >= 40.0 or len(rising_keywords) > 0

        result = {
            "keyword": keyword,
            "google_interest_score": round(recent_interest, 2),
            "rising_keywords": rising_keywords,
            "is_valid": is_high_leverage
        }
        
        print(f"✨ [검증 완료] 관심도 점수: {result['google_interest_score']}점 | 확장 키워드: {rising_keywords} | 타겟 유효성: {is_high_leverage}")
        return result

    except Exception as e:
        print(f"❌ 구글 트렌드 API 호출 중 예외 발생 (Rate Limit 등): {e}")
        return {"keyword": keyword, "google_interest_score": 0.0, "rising_keywords": [], "is_valid": False}

if __name__ == "__main__":
    # 테스트 실행
    res = cross_check_with_google_trends("해운대 맛집")
    print(res)