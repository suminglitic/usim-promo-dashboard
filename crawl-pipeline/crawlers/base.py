"""기본 크롤러 추상 클래스"""
import abc
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import CRAWL_TIMEOUT, SELENIUM_TIMEOUT, USER_AGENT
from models import RawPlanData

logger = logging.getLogger(__name__)


class CrawlFailureError(Exception):
    """크롤링 실패 시 발생하는 예외"""
    pass


class BaseCrawler(abc.ABC):
    """크롤러 기본 클래스 — BeautifulSoup 우선, Selenium fallback"""

    def __init__(self, carrier: str, url: str):
        self.carrier = carrier
        self.url = url
        self.headers = {"User-Agent": USER_AGENT}

    def crawl(self) -> list[RawPlanData]:
        """크롤링 실행 (fallback 패턴)"""
        # Phase 1: 정적 파싱 시도
        try:
            logger.info(f"[{self.carrier}] 정적 파싱 시도: {self.url}")
            html = self._fetch_static()
            plans = self._parse(html)
            if plans:
                logger.info(f"[{self.carrier}] 정적 파싱 성공: {len(plans)}개 요금제")
                return plans
        except Exception as e:
            logger.warning(f"[{self.carrier}] 정적 파싱 실패: {e}")

        # Phase 2: Selenium 동적 렌더링
        try:
            logger.info(f"[{self.carrier}] Selenium 동적 렌더링 시도")
            html = self._fetch_dynamic()
            plans = self._parse(html)
            if plans:
                logger.info(f"[{self.carrier}] 동적 렌더링 성공: {len(plans)}개 요금제")
                return plans
        except Exception as e:
            logger.warning(f"[{self.carrier}] 동적 렌더링 실패: {e}")

        raise CrawlFailureError(
            f"{self.carrier} 크롤링 실패: 데이터를 추출할 수 없습니다. URL: {self.url}"
        )

    def _fetch_static(self) -> str:
        """requests로 정적 HTML 가져오기"""
        response = requests.get(
            self.url, headers=self.headers, timeout=CRAWL_TIMEOUT
        )
        response.raise_for_status()
        return response.text

    def _fetch_dynamic(self) -> str:
        """Selenium으로 동적 렌더링된 HTML 가져오기"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={USER_AGENT}")

        driver = webdriver.Chrome(options=options)
        try:
            driver.set_page_load_timeout(SELENIUM_TIMEOUT)
            driver.get(self.url)
            # 페이지 로드 대기
            WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return driver.page_source
        finally:
            driver.quit()

    @abc.abstractmethod
    def _parse(self, html: str) -> list[RawPlanData]:
        """HTML에서 요금제 데이터 추출 (하위 클래스에서 구현)"""
        pass

    def _make_soup(self, html: str) -> BeautifulSoup:
        """BeautifulSoup 객체 생성"""
        return BeautifulSoup(html, "html.parser")
