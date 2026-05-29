"""크롤링 파이프라인 설정"""
import os

# 크롤링 대상 URL
URLS = {
    "SKT": "https://shop.tworld.co.kr/exhibition/view?exhibitionId=P00000326",
    "KT": "https://shop.kt.com/unify/yogoEvent.do",
    "LG": "https://www.lguplus.com/mobile/self-usim/activate?regType=&selfYn=true&dvicType=U-5G02&usimYn=Y",
}

# 크롤링 설정
CRAWL_TIMEOUT = 30  # 초
SELENIUM_TIMEOUT = 30  # 초

# 데이터 저장 경로
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LATEST_CSV = os.path.join(DATA_DIR, "latest.csv")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")

# 데이터 보존 기간
RETENTION_DAYS = 90

# User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
