"""KT 요고 요금제 크롤러"""
import re
import logging
from datetime import datetime

from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from models import RawPlanData
from config import URLS

logger = logging.getLogger(__name__)


class KTCrawler(BaseCrawler):
    """KT 요고 이벤트 페이지 크롤러"""

    def __init__(self):
        super().__init__(carrier="KT", url=URLS["KT"])

    def _parse(self, html: str) -> list[RawPlanData]:
        """KT 요고 페이지에서 요금제 및 혜택 정보 추출"""
        soup = self._make_soup(html)
        plans = []

        # 요고 요금제 카드/섹션 탐색
        plan_elements = soup.select(
            "[class*='yogo'], [class*='plan'], [class*='product'], "
            "[class*='benefit'], [class*='rate']"
        )

        if not plan_elements:
            plan_elements = self._find_yogo_sections(soup)

        for elem in plan_elements:
            extracted = self._extract_yogo_plan(elem)
            if extracted:
                plans.extend(extracted) if isinstance(extracted, list) else plans.append(extracted)

        # 중복 제거
        seen = set()
        unique_plans = []
        for p in plans:
            if p.plan_name not in seen:
                seen.add(p.plan_name)
                unique_plans.append(p)

        return unique_plans

    def _find_yogo_sections(self, soup: BeautifulSoup) -> list:
        """요고 관련 텍스트 패턴으로 섹션 찾기"""
        sections = []
        # "요고" 텍스트가 포함된 요소 탐색
        for elem in soup.find_all(string=re.compile(r'요고|yogo', re.IGNORECASE)):
            parent = elem.find_parent(['div', 'li', 'section', 'article'])
            if parent and parent not in sections:
                sections.append(parent)
        return sections

    def _extract_yogo_plan(self, elem) -> RawPlanData | list[RawPlanData] | None:
        """요소에서 요고 요금제 정보 추출"""
        text = elem.get_text(separator=" ", strip=True)

        # 요고 요금제명 추출 (요고 47, 요고 51, 요고 61, 요고 69 등)
        name_matches = re.findall(r'요고\s*(\d+)', text)
        if not name_matches:
            return None

        plans = []
        for plan_num in set(name_matches):
            plan_name = f"요고 {plan_num}"

            # 월정액 추출 (요금제 번호와 가까운 금액)
            fee_pattern = rf'{plan_num}.*?(\d[\d,]*)\s*원'
            fee_match = re.search(fee_pattern, text)
            monthly_fee_text = fee_match.group(1) + "원" if fee_match else f"{plan_num},000원"

            # 페이백 혜택 추출
            benefit_text = self._extract_benefits(text, plan_num)

            plans.append(RawPlanData(
                carrier="KT",
                plan_name=plan_name,
                monthly_fee_text=monthly_fee_text,
                benefit_text=benefit_text,
                additional_info=self._extract_ott_benefits(text),
                crawled_at=datetime.now(),
                source_url=self.url,
            ))

        return plans if plans else None

    def _extract_benefits(self, text: str, plan_num: str) -> str:
        """페이백 혜택 정보 추출"""
        benefits = []

        # 카카오페이/네이버페이 페이백
        payback_patterns = [
            r'(카카오페이|네이버페이)\s*(\d[\d,]*)\s*원',
            r'페이백\s*(\d[\d,]*)\s*원',
            r'(\d[\d,]*)\s*원\s*(페이백|캐시백)',
        ]

        for pattern in payback_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                benefits.append(" ".join(match))

        # 쿠폰팩 할인
        coupon_match = re.search(r'쿠폰팩.*?(\d[\d,]*)\s*원', text)
        if coupon_match:
            benefits.append(f"쿠폰팩 {coupon_match.group(1)}원")

        return ", ".join(benefits) if benefits else ""

    def _extract_ott_benefits(self, text: str) -> str:
        """OTT 혜택 정보 추출"""
        ott_services = []
        ott_patterns = [
            r'(넷플릭스|유튜브\s*프리미엄|디즈니\+|웨이브|티빙|쿠팡플레이)',
            r'(초이스|플러스).*?(OTT|구독)',
        ]

        for pattern in ott_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                ott_services.append(match if isinstance(match, str) else " ".join(match))

        return ", ".join(ott_services) if ott_services else ""
