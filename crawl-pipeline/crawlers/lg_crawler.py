"""LG U+ 너겟 요금제 크롤러"""
import re
import logging
from datetime import datetime

from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from models import RawPlanData
from config import URLS

logger = logging.getLogger(__name__)


class LGCrawler(BaseCrawler):
    """LG U+ 너겟 USIM 주문서 페이지 크롤러"""

    def __init__(self):
        super().__init__(carrier="LG", url=URLS["LG"])

    def _parse(self, html: str) -> list[RawPlanData]:
        """LG U+ 주문서 페이지 중간의 혜택 텍스트 영역 파싱"""
        soup = self._make_soup(html)
        plans = []

        # 전체 텍스트에서 혜택 티어 패턴 탐색
        full_text = soup.get_text(separator="\n")
        tiers = self._parse_benefit_tiers(full_text)

        if tiers:
            for tier in tiers:
                for plan_name in tier["plans"]:
                    plans.append(RawPlanData(
                        carrier="LG",
                        plan_name=plan_name,
                        monthly_fee_text=self._estimate_monthly_fee(plan_name),
                        benefit_text=f"네이버페이 등 너겟쿠폰 {tier['benefit_text']}",
                        benefit_condition=tier["condition"],
                        crawled_at=datetime.now(),
                        source_url=self.url,
                    ))
        else:
            # 대체 파싱: 요금제 카드/리스트 탐색
            plans = self._fallback_parse(soup)

        # 중복 제거
        seen = set()
        unique_plans = []
        for p in plans:
            if p.plan_name not in seen:
                seen.add(p.plan_name)
                unique_plans.append(p)

        return unique_plans

    def _parse_benefit_tiers(self, text: str) -> list[dict]:
        """①②③④⑤ 번호 매김 텍스트에서 혜택 티어 파싱"""
        tiers = []

        # 원문자 번호로 분리
        tier_pattern = r'[①②③④⑤⑥⑦⑧⑨⑩](.+?)(?=[①②③④⑤⑥⑦⑧⑨⑩]|$)'
        matches = re.findall(tier_pattern, text, re.DOTALL)

        for match in matches:
            tier = self._parse_single_tier(match.strip())
            if tier:
                tiers.append(tier)

        return tiers

    def _parse_single_tier(self, text: str) -> dict | None:
        """단일 혜택 티어 파싱"""
        # 혜택 금액 추출: "28만8천원", "24만원", "18만원", "7만5천원", "3만원"
        benefit_match = re.search(
            r'(\d+만\d*천?\s*원|\d+천\s*원|\d[\d,]*\s*원)', text
        )
        if not benefit_match:
            return None

        benefit_text = benefit_match.group(1)

        # 요금제명 추출: "너겟 69", "너겟 59", "너겟 47" 등
        plan_names = re.findall(r'너겟\s*(\d+)', text)
        if not plan_names:
            # "너겟 34~44" 같은 범위 패턴
            range_match = re.search(r'너겟\s*(\d+)\s*[~\-]\s*(\d+)', text)
            if range_match:
                start, end = int(range_match.group(1)), int(range_match.group(2))
                plan_names = [str(n) for n in range(start, end + 1)]

        if not plan_names:
            return None

        # 월 지급 조건 추출: "2만4천원x12개월", "5천원x15개월"
        condition_match = re.search(
            r'(\d+만?\d*천?\s*원)\s*[xX×]\s*(\d+)\s*개월', text
        )
        condition = condition_match.group(0) if condition_match else ""

        return {
            "benefit_text": benefit_text,
            "plans": [f"너겟 {n}" for n in plan_names],
            "condition": condition,
        }

    def _estimate_monthly_fee(self, plan_name: str) -> str:
        """요금제명에서 월정액 추정 (너겟 XX → XX,000원)"""
        match = re.search(r'너겟\s*(\d+)', plan_name)
        if match:
            fee = int(match.group(1)) * 1000
            return f"{fee:,}원"
        return ""

    def _fallback_parse(self, soup: BeautifulSoup) -> list[RawPlanData]:
        """대체 파싱: 너겟 요금제 관련 요소 탐색"""
        plans = []
        text = soup.get_text(separator=" ")

        # "너겟" 키워드 주변에서 요금제 정보 추출
        nugget_matches = re.findall(r'너겟\s*(\d+)', text)
        for plan_num in set(nugget_matches):
            plan_name = f"너겟 {plan_num}"
            plans.append(RawPlanData(
                carrier="LG",
                plan_name=plan_name,
                monthly_fee_text=f"{int(plan_num) * 1000:,}원",
                benefit_text="",
                crawled_at=datetime.now(),
                source_url=self.url,
            ))

        return plans
