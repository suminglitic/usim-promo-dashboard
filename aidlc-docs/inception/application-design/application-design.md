# Application Design Summary

## 시스템 개요

통신 3사 USIM 요금제 프로모션 크롤링 대시보드는 2개의 독립 배포 단위로 구성됩니다:

1. **크롤링 파이프라인** (AWS Lambda) — 매일 자동 실행, 데이터 수집/처리/적재
2. **대시보드 앱** (Streamlit) — 사용자 접속 시 데이터 조회/시각화

## 아키텍처 다이어그램

```
+-------------------------------------------------------------------+
|                    AWS Cloud                                        |
|                                                                    |
|  +-------------+     +----------------------------------------+   |
|  | EventBridge | --> |         Lambda Function                 |   |
|  | (Daily 10AM)|     |                                        |   |
|  +-------------+     |  +------------+  +---------------+     |   |
|                      |  | Crawler    |  | DataProcessor |     |   |
|                      |  | Engine     |->|               |     |   |
|                      |  | (SKT/KT/LG)|  | (clean/calc)  |     |   |
|                      |  +------------+  +---------------+     |   |
|                      |                         |              |   |
|                      +-------------------------|------ --------+   |
|                                                |                   |
|                                                v                   |
|                      +----------------------------------------+   |
|                      |              Amazon S3                   |   |
|                      |  s3://bucket/year=.../month=.../day=../ |   |
|                      +----------------------------------------+   |
|                                                |                   |
|                                                v                   |
|                      +----------------------------------------+   |
|                      |            AWS Athena                    |   |
|                      |         (SQL Query Engine)               |   |
|                      +----------------------------------------+   |
+-------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------+
|                 Streamlit Community Cloud                           |
|                                                                    |
|  +------------------------------------------------------------+  |
|  |                    Dashboard App                             |  |
|  |                                                             |  |
|  |  +------------------+  +------------------+  +-----------+ |  |
|  |  | Comparison Table |  |  Trend Chart     |  | Status    | |  |
|  |  | (3사 비교)        |  | (90일 추이)      |  | (수집상태)| |  |
|  |  +------------------+  +------------------+  +-----------+ |  |
|  +------------------------------------------------------------+  |
+-------------------------------------------------------------------+
                                     |
                                     v
                              +-------------+
                              |    User     |
                              | (Browser)   |
                              +-------------+
```

## 컴포넌트 요약

| # | Component | 책임 | 배포 환경 |
|---|-----------|------|-----------|
| 1 | CrawlerEngine | 3사 웹 크롤링 (BS4 + Selenium fallback) | Lambda |
| 2 | DataProcessor | 데이터 정제, 체감가 계산, 정규화 | Lambda |
| 3 | DataStore | S3 저장/조회, Athena 쿼리, 보존 정책 | Lambda + Streamlit |
| 4 | Dashboard | 비교 테이블, 트렌드 차트, 수집 상태 | Streamlit Cloud |
| 5 | Scheduler | EventBridge 트리거, 워크플로우 오케스트레이션 | Lambda |

## 핵심 설계 결정

1. **단일 Lambda 함수**: 크롤링+전처리+적재를 하나의 Lambda에서 실행 (15분 제한 내 충분)
2. **통신사별 독립 실행**: 1사 실패가 다른 2사에 영향 없음
3. **Parquet 포맷**: Athena 쿼리 최적화, 컬럼 기반 압축
4. **Streamlit 캐시**: @st.cache_data로 반복 쿼리 최소화 (TTL 1시간)
5. **BeautifulSoup 우선**: 가벼운 정적 파싱 먼저 시도, JS 렌더링 필요 시에만 Selenium

## 데이터 모델 (High-Level)

### RawPlanData
```python
{
    "carrier": str,          # SKT, KT, LG
    "plan_name": str,        # 원시 요금제명
    "monthly_fee": str,      # 원시 월정액 텍스트
    "benefits": str,         # 원시 혜택 텍스트
    "crawled_at": str        # 크롤링 시각 (ISO 8601)
}
```

### ProcessedPlanData
```python
{
    "carrier": str,          # SKT, KT, LG
    "plan_name": str,        # 정규화된 요금제명
    "monthly_fee": int,      # 월정액 (원)
    "perceived_price": int,  # 체감가 (원)
    "benefit_amount": int,   # 총 혜택 금액 (원)
    "benefit_detail": str,   # 혜택 상세 설명
    "collected_date": str    # 수집 날짜 (YYYY-MM-DD)
}
```

## 상세 설계 문서 참조
- [components.md](components.md) — 컴포넌트 정의 및 인터페이스
- [component-methods.md](component-methods.md) — 메서드 시그니처
- [services.md](services.md) — 서비스 오케스트레이션
- [component-dependency.md](component-dependency.md) — 의존성 및 데이터 흐름
