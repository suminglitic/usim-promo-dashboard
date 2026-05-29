"""SKT T월드 다이렉트 USIM 크롤러"""
import re
import logging
from datetime import datetime

from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from models import RawPlanData
from config import URLS

logger = logging.getLogger(__name__)


class SKTCrawler(BaseCrawler):
    """SKT T월드 다이렉트 USIM 페이지 크롤러"""

    def __init__(self):
        super().__init__(carrier="SKT", url=URLS["SKT"])

    def _parse(self, html: str) -> list[RawPlanData]:
        """SKT 페이지에서 요금제 정보 추출"""
        soup = self._make_soup(html)
        plans = []

        # SKT 프로모션 페이지 구조에 맞춰 파싱
        # 요금제 카드/리스트 영역 탐색
        plan_elements = soup.select(
            "[class*='plan'], [class*='rate'], [class*='product'], "
            "[class*='item'], [class*='card']"
        )

        if not plan_elements:
            # 대체 탐색: 텍스트 기반
            plan_elements = self._find_plan_sections(soup)

        for elem in plan_elements:
            plan = self._extract_plan_from_element(elem)
            if plan:
                plans.append(plan)

        # 중복 제거 (요금제명 기준)
        seen = set()
        unique_plans = []
        for p in plans:
            if p.plan_name not in seen:
                seen.add(p.plan_name)
                unique_plans.append(p)

        return unique_plans

    def _find_plan_sections(self, soup: BeautifulSoup) -> list:
        """텍스트 패턴으로 요금제 섹션 찾기"""
        sections = []
        # "요금제" 또는 금액 패턴이 포함된 요소 탐색
        for elem in soup.find_all(string=re.compile(r'\d+[,.]?\d*원|월\s*\d+')):
            parent = elem.find_parent(['div', 'li', 'section', 'article'])
            if parent and parent not in sections:
                sections.append(parent)
        return sections

    def _extract_plan_from_element(self, elem) -> RawPlanData | None:
        """요소에서 요금제 정보 추출"""
        text = elem.get_text(separator=" ", strip=True)

        # 요금제명 추출 패턴
        name_patterns = [
            r'(T플랜\s*\w+)',
            r'(다이렉트\s*\w+)',
            r'(5G\s*\w+)',
            r'(LTE\s*\w+)',
        ]

        plan_name = None
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                plan_name = match.group(1).strip()
                break

        if not plan_name:
            return None

        # 월정액 추출
        fee_match = re.search(r'(\d[\d,]*)\s*원', text)
        monthly_fee_text = fee_match.group(0) if fee_match else ""

        if not monthly_fee_text:
            return None

        # 혜택 정보 추출
        benefit_patterns = [
            r'(네이버페이|카카오페이|페이백|할인|혜택).*?(\d[\d,]*\s*원)',
            r'(\d[\d,]*\s*원)\s*(혜택|할인|페이백)',
        ]

        benefit_text = ""
        for pattern in benefit_patterns:
            match = re.search(pattern, text)
            if match:
                benefit_text = match.group(0)
                break

        return RawPlanData(
            carrier="SKT",
            plan_name=plan_name,
            monthly_fee_text=monthly_fee_text,
            benefit_text=benefit_text,
            crawled_at=datetime.now(),
            source_url=self.url,
        )
