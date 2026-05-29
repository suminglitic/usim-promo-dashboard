# Component Methods

## CrawlerEngine

### crawl(carrier: str, url: str) -> list[RawPlanData]
- **목적**: 지정된 통신사 URL에서 요금제 프로모션 데이터 추출
- **입력**: carrier (SKT/KT/LG), url (대상 페이지 URL)
- **출력**: RawPlanData 리스트 (요금제명, 월정액, 혜택 정보 등)
- **전략**: BeautifulSoup 정적 파싱 우선, 실패 시 Selenium fallback

### validate_result(data: list[RawPlanData]) -> bool
- **목적**: 크롤링 결과가 유효한지 검증 (빈 데이터 방지)
- **입력**: 크롤링 결과 데이터
- **출력**: True (유효) / False (무효 → 에러 발생)
- **규칙**: 최소 1개 이상의 요금제 데이터 존재 필수

### _parse_skt(html: str) -> list[RawPlanData]
- **목적**: SKT T월드 페이지 HTML 파싱
- **입력**: HTML 문자열
- **출력**: SKT 요금제 데이터 리스트

### _parse_kt(html: str) -> list[RawPlanData]
- **목적**: KT 요고 이벤트 페이지 HTML 파싱
- **입력**: HTML 문자열
- **출력**: KT 요금제 데이터 리스트 (페이백, OTT 혜택 포함)

### _parse_lg(html: str) -> list[RawPlanData]
- **목적**: LG U+ 너겟 주문서 페이지 한글 텍스트 영역 파싱
- **입력**: HTML 문자열
- **출력**: LG 요금제 데이터 리스트 (네이버페이/너겟쿠폰 혜택 포함)

---

## DataProcessor

### process(raw_data: list[RawPlanData]) -> list[ProcessedPlanData]
- **목적**: 원시 데이터를 정제된 통합 형식으로 변환
- **입력**: 원시 크롤링 데이터
- **출력**: 정제된 데이터 (통일된 스키마)

### calculate_perceived_price(plan: RawPlanData) -> int
- **목적**: 체감가 계산 (월정액 - 월 환산 할인액)
- **입력**: 개별 요금제 원시 데이터
- **출력**: 체감가 (원 단위 정수)

### normalize_plan_name(name: str) -> str
- **목적**: 요금제명 정규화 (공백, 특수문자 통일)
- **입력**: 원시 요금제명
- **출력**: 정규화된 요금제명

### _clean_currency(text: str) -> int
- **목적**: 통화 기호 제거 및 숫자 변환
- **입력**: "2만4천원", "₩24,000" 등
- **출력**: 24000 (정수)

---

## DataStore

### store(data: list[ProcessedPlanData], date: str) -> str
- **목적**: 처리된 데이터를 S3에 일별 스냅샷으로 저장
- **입력**: 정제된 데이터, 수집 날짜 (YYYY-MM-DD)
- **출력**: S3 저장 경로 (s3://bucket/year=YYYY/month=MM/day=DD/data.parquet)

### query_latest() -> list[ProcessedPlanData]
- **목적**: 최신 수집 데이터 조회
- **입력**: 없음
- **출력**: 가장 최근 수집된 3사 요금제 데이터

### query_trend(days: int) -> list[TrendData]
- **목적**: 지정 기간의 트렌드 데이터 조회
- **입력**: 조회 기간 (일 수, 기본 90)
- **출력**: 일별 요금제 지표 시계열 데이터

### cleanup_expired(retention_days: int) -> int
- **목적**: 보존 기간 초과 데이터 삭제
- **입력**: 보존 기간 (기본 90일)
- **출력**: 삭제된 파일 수

---

## Dashboard

### render_comparison_table() -> None
- **목적**: 3사 요금제 비교 테이블 렌더링
- **입력**: 없음 (내부적으로 DataStore.query_latest() 호출)
- **출력**: Streamlit 테이블 위젯

### render_trend_chart(metric: str, days: int) -> None
- **목적**: 시계열 트렌드 차트 렌더링
- **입력**: metric (monthly_fee/perceived_price), days (기본 90)
- **출력**: Streamlit 라인 차트 위젯

### show_collection_status() -> None
- **목적**: 각 통신사별 마지막 수집 시간 및 상태 표시
- **입력**: 없음
- **출력**: Streamlit 상태 위젯 (정상/경고)

---

## Scheduler

### trigger_crawl() -> dict
- **목적**: Lambda 핸들러 — 3사 크롤링 워크플로우 실행
- **입력**: EventBridge 이벤트
- **출력**: 실행 결과 (성공/실패 통신사별 상태)
