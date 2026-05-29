# Domain Entities — crawl-pipeline

## Entity 1: RawPlanData

크롤링에서 직접 추출된 원시 데이터

```python
@dataclass
class RawPlanData:
    carrier: str              # "SKT" | "KT" | "LG"
    plan_name: str            # 원시 요금제명 (예: "너겟 69", "요고 61")
    monthly_fee_text: str     # 원시 월정액 텍스트 (예: "69,000원", "6만9천원")
    benefit_text: str         # 원시 혜택 텍스트 (예: "네이버페이 28만8천원")
    benefit_condition: str    # 혜택 조건 (예: "2만4천원x12개월")
    additional_info: str      # 추가 정보 (OTT, 쿠폰팩 등)
    crawled_at: datetime      # 크롤링 시각
    source_url: str           # 크롤링 소스 URL
```

## Entity 2: ProcessedPlanData

전처리 완료된 정제 데이터 (S3 저장 단위)

```python
@dataclass
class ProcessedPlanData:
    carrier: str              # "SKT" | "KT" | "LG"
    plan_name: str            # 정규화된 요금제명
    monthly_fee: int          # 월정액 (원 단위)
    perceived_price: int      # 체감가 (원 단위) = 월정액 - 월환산혜택
    total_benefit: int        # 총 혜택 금액 (원 단위)
    monthly_benefit: int      # 월 환산 혜택 금액 (원 단위)
    benefit_duration: int     # 혜택 지급 기간 (개월)
    benefit_detail: str       # 혜택 상세 설명
    collected_date: str       # 수집 날짜 (YYYY-MM-DD)
    crawled_at: str           # 크롤링 시각 (ISO 8601)
```

## Entity 3: CrawlResult

단일 통신사 크롤링 실행 결과

```python
@dataclass
class CrawlResult:
    carrier: str              # "SKT" | "KT" | "LG"
    success: bool             # 성공 여부
    plans: list[RawPlanData]  # 추출된 요금제 리스트
    error_message: str | None # 실패 시 에러 메시지
    crawled_at: datetime      # 크롤링 시각
```

## Entity 4: PipelineResult

전체 파이프라인 실행 결과 (Lambda 반환값)

```python
@dataclass
class PipelineResult:
    execution_date: str       # 실행 날짜 (YYYY-MM-DD)
    results: dict[str, CrawlResult]  # 통신사별 결과
    total_plans_stored: int   # 저장된 총 요금제 수
    failed_carriers: list[str]  # 실패한 통신사 목록
```

## Entity Relationships

```
PipelineResult
  └── CrawlResult (per carrier: SKT, KT, LG)
        └── RawPlanData[] (per plan)
              └── (processed to) ProcessedPlanData[]
                    └── (stored in) S3 Parquet
```
