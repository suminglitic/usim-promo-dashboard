# Domain Entities — dashboard-app

## Entity 1: PlanComparisonRow

비교 테이블에 표시되는 단일 행

```python
@dataclass
class PlanComparisonRow:
    carrier: str              # 통신사 (SKT, KT, LG)
    plan_name: str            # 요금제명
    monthly_fee: int          # 월정액 (원)
    perceived_price: int      # 체감가 (원)
    total_benefit: int        # 총 혜택 금액 (원)
    benefit_detail: str       # 혜택 상세 설명
    collected_date: str       # 최종 수집일
```

## Entity 2: TrendDataPoint

트렌드 차트의 단일 데이터 포인트

```python
@dataclass
class TrendDataPoint:
    date: str                 # 날짜 (YYYY-MM-DD)
    carrier: str              # 통신사
    plan_name: str            # 요금제명
    monthly_fee: int          # 월정액
    perceived_price: int      # 체감가
```

## Entity 3: CollectionStatus

통신사별 수집 상태 정보

```python
@dataclass
class CollectionStatus:
    carrier: str              # 통신사
    last_success_date: str    # 마지막 성공 수집일
    is_stale: bool            # 데이터 오래됨 여부 (24시간 초과)
    plan_count: int           # 수집된 요금제 수
```
