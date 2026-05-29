# Application Components

## Component 1: CrawlerEngine

| 항목 | 내용 |
|------|------|
| **이름** | CrawlerEngine |
| **목적** | 통신사 웹 페이지에서 USIM 요금제 프로모션 데이터 추출 |
| **책임** | URL 접근, HTML 파싱, 데이터 추출, 실패 감지 |

### 인터페이스
- `crawl(carrier: str, url: str) -> RawPlanData[]`
- `validate_result(data: RawPlanData[]) -> bool`

### 하위 모듈
- **SKTCrawler**: T월드 다이렉트 USIM 페이지 크롤링
- **KTCrawler**: KT 요고 이벤트 페이지 크롤링
- **LGCrawler**: LG U+ 너겟 USIM 주문서 페이지 크롤링

---

## Component 2: DataProcessor

| 항목 | 내용 |
|------|------|
| **이름** | DataProcessor |
| **목적** | 원시 크롤링 데이터를 정제하여 통일된 형식으로 변환 |
| **책임** | 통화 기호 제거, 요금제명 정규화, 체감가 계산, 스키마 변환 |

### 인터페이스
- `process(raw_data: RawPlanData[]) -> ProcessedPlanData[]`
- `calculate_perceived_price(plan: RawPlanData) -> int`
- `normalize_plan_name(name: str) -> str`

---

## Component 3: DataStore

| 항목 | 내용 |
|------|------|
| **이름** | DataStore |
| **목적** | 처리된 데이터를 S3에 저장하고 Athena로 쿼리 가능하게 관리 |
| **책임** | S3 업로드, 파티셔닝, 데이터 보존 정책 적용, Athena 쿼리 |

### 인터페이스
- `store(data: ProcessedPlanData[], date: str) -> str`
- `query_latest() -> ProcessedPlanData[]`
- `query_trend(days: int) -> TrendData[]`
- `cleanup_expired(retention_days: int) -> int`

---

## Component 4: Dashboard

| 항목 | 내용 |
|------|------|
| **이름** | Dashboard |
| **목적** | 사용자에게 요금제 비교 테이블과 트렌드 차트를 제공 |
| **책임** | 데이터 조회, 비교 테이블 렌더링, 트렌드 차트 렌더링, 수집 상태 표시 |

### 인터페이스
- `render_comparison_table() -> StreamlitPage`
- `render_trend_chart(metric: str, days: int) -> StreamlitChart`
- `show_collection_status() -> StatusWidget`

---

## Component 5: Scheduler

| 항목 | 내용 |
|------|------|
| **이름** | Scheduler |
| **목적** | 크롤링 워크플로우를 정해진 시간에 자동 트리거 |
| **책임** | EventBridge 스케줄 관리, Lambda 트리거, 실행 상태 관리 |

### 인터페이스
- `trigger_crawl() -> ExecutionResult`
- EventBridge Rule: `cron(0 1 * * ? *)` (UTC 01:00 = KST 10:00)
