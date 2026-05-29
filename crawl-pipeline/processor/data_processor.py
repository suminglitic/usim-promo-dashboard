"""데이터 전처리 모듈"""
import re
import logging
from datetime import date

from models import RawPlanData, ProcessedPlanData

logger = logging.getLogger(__name__)


class DataProcessor:
    """원시 크롤링 데이터를 정제된 형식으로 변환"""

    def process(self, raw_data: list[RawPlanData]) -> list[ProcessedPlanData]:
        """원시 데이터 리스트를 정제 데이터로 변환"""
        processed = []
        for raw in raw_data:
            try:
                result = self._process_single(raw)
                if result:
                    processed.append(result)
            except Exception as e:
                logger.warning(f"전처리 실패 [{raw.carrier}] {raw.plan_name}: {e}")
                continue
        return processed

    def _process_single(self, raw: RawPlanData) -> ProcessedPlanData | None:
        """단일 요금제 데이터 전처리"""
        monthly_fee = self.clean_currency(raw.monthly_fee_text)
        if monthly_fee == 0:
            return None

        total_benefit, monthly_benefit, duration = self._parse_benefit(
            raw.benefit_text, raw.benefit_condition
        )

        perceived_price = max(0, monthly_fee - monthly_benefit)

        return ProcessedPlanData(
            carrier=raw.carrier,
            plan_name=self.normalize_plan_name(raw.plan_name),
            monthly_fee=monthly_fee,
            perceived_price=perceived_price,
            total_benefit=total_benefit,
            monthly_benefit=monthly_benefit,
            benefit_duration=duration,
            benefit_detail=raw.benefit_text,
            collected_date=date.today().isoformat(),
            crawled_at=raw.crawled_at.isoformat() if hasattr(raw.crawled_at, 'isoformat') else str(raw.crawled_at),
        )

    @staticmethod
    def clean_currency(text: str) -> int:
        """한국어 통화 표현을 정수(원 단위)로 변환

        Examples:
            "6만9천원" → 69000
            "69,000원" → 69000
            "28만8천원" → 288000
            "5천원" → 5000
            "2만4천원" → 24000
        """
        if not text:
            return 0

        text = text.strip().replace("₩", "").replace("원", "").replace(",", "").replace(" ", "")

        # "X만Y천" 패턴
        man_match = re.search(r'(\d+)만', text)
        cheon_match = re.search(r'(\d+)천', text)

        result = 0
        if man_match:
            result += int(man_match.group(1)) * 10000
        if cheon_match:
            result += int(cheon_match.group(1)) * 1000

        # 순수 숫자 패턴 (만/천 없는 경우)
        if not man_match and not cheon_match:
            digits = re.sub(r'[^\d]', '', text)
            if digits:
                result = int(digits)

        return result

    def _parse_benefit(self, benefit_text: str, condition: str) -> tuple[int, int, int]:
        """혜택 정보에서 총 혜택, 월 혜택, 기간 추출

        Returns:
            (total_benefit, monthly_benefit, duration_months)
        """
        if not benefit_text and not condition:
            return 0, 0, 0

        total_benefit = 0
        monthly_benefit = 0
        duration = 0

        # 조건에서 "X원 x Y개월" 패턴 추출
        if condition:
            cond_match = re.search(
                r'(\d+만?\d*천?\s*원?)\s*[xX×]\s*(\d+)\s*개월', condition
            )
            if cond_match:
                monthly_benefit = self.clean_currency(cond_match.group(1))
                duration = int(cond_match.group(2))
                total_benefit = monthly_benefit * duration
                return total_benefit, monthly_benefit, duration

        # 혜택 텍스트에서 총 금액 추출
        benefit_amount_match = re.search(
            r'(\d+만\d*천?\s*원|\d+천\s*원|\d[\d,]*\s*원)', benefit_text
        )
        if benefit_amount_match:
            total_benefit = self.clean_currency(benefit_amount_match.group(1))

        # 기간 추출
        duration_match = re.search(r'(\d+)\s*개월', benefit_text + " " + condition)
        if duration_match:
            duration = int(duration_match.group(1))
        elif total_benefit > 0:
            duration = 12  # 기본값

        # 월 혜택 계산
        if duration > 0 and total_benefit > 0:
            monthly_benefit = total_benefit // duration

        return total_benefit, monthly_benefit, duration

    @staticmethod
    def normalize_plan_name(name: str) -> str:
        """요금제명 정규화"""
        if not name:
            return ""

        # 앞뒤 공백 제거
        name = name.strip()

        # 연속 공백을 단일 공백으로
        name = re.sub(r'\s+', ' ', name)

        # 통신사 접두사 제거
        prefixes = ['LG U+', 'LG유플러스', 'SKT', 'SK텔레콤', 'KT']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()

        return name
