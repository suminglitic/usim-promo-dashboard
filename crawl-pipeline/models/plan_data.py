"""데이터 모델 정의"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class RawPlanData:
    """크롤링에서 직접 추출된 원시 데이터"""
    carrier: str
    plan_name: str
    monthly_fee_text: str
    benefit_text: str
    benefit_condition: str = ""
    additional_info: str = ""
    crawled_at: datetime = field(default_factory=datetime.now)
    source_url: str = ""


@dataclass
class ProcessedPlanData:
    """전처리 완료된 정제 데이터"""
    carrier: str
    plan_name: str
    monthly_fee: int
    perceived_price: int
    total_benefit: int
    monthly_benefit: int
    benefit_duration: int
    benefit_detail: str
    collected_date: str
    crawled_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CrawlResult:
    """단일 통신사 크롤링 실행 결과"""
    carrier: str
    success: bool
    plans: list = field(default_factory=list)
    error_message: Optional[str] = None
    crawled_at: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineResult:
    """전체 파이프라인 실행 결과"""
    execution_date: str
    results: dict = field(default_factory=dict)
    total_plans_stored: int = 0
    failed_carriers: list = field(default_factory=list)
