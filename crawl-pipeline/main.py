"""크롤링 파이프라인 메인 오케스트레이터

GitHub Actions에서 매일 KST 10:00에 실행됩니다.
3사(SKT, KT, LG) 크롤링을 독립적으로 실행하고,
성공한 데이터만 CSV로 저장합니다.
"""
import logging
import sys
import os
from datetime import date

# 패키지 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawlers import SKTCrawler, KTCrawler, LGCrawler
from crawlers.base import CrawlFailureError
from processor import DataProcessor
from store import CsvStore
from models import CrawlResult, PipelineResult

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_pipeline() -> PipelineResult:
    """메인 파이프라인 실행

    3사 크롤링을 독립적으로 실행하고, 성공한 데이터만 저장합니다.
    1사 실패가 다른 2사에 영향을 주지 않습니다.
    """
    execution_date = date.today().isoformat()
    logger.info(f"=== 크롤링 파이프라인 시작: {execution_date} ===")

    # 크롤러 인스턴스 생성
    crawlers = [
        SKTCrawler(),
        KTCrawler(),
        LGCrawler(),
    ]

    processor = DataProcessor()
    store = CsvStore()

    results = {}
    all_processed = []

    # 3사 독립 실행
    for crawler in crawlers:
        carrier = crawler.carrier
        logger.info(f"--- [{carrier}] 크롤링 시작 ---")

        try:
            # 1. 크롤링
            raw_data = crawler.crawl()

            # 2. 검증 (빈 데이터 방지)
            if not raw_data:
                raise CrawlFailureError(f"{carrier}: 추출된 데이터 없음")

            logger.info(f"[{carrier}] 크롤링 성공: {len(raw_data)}개 요금제 추출")

            # 3. 전처리
            processed = processor.process(raw_data)
            if not processed:
                raise CrawlFailureError(f"{carrier}: 전처리 후 유효 데이터 없음")

            all_processed.extend(processed)
            results[carrier] = CrawlResult(
                carrier=carrier,
                success=True,
                plans=raw_data,
            )
            logger.info(f"[{carrier}] 전처리 완료: {len(processed)}개 요금제")

        except CrawlFailureError as e:
            logger.error(f"[{carrier}] 크롤링 실패: {e}")
            results[carrier] = CrawlResult(
                carrier=carrier,
                success=False,
                error_message=str(e),
            )
            # 다른 통신사는 계속 진행
            continue

        except Exception as e:
            logger.error(f"[{carrier}] 예상치 못한 오류: {e}", exc_info=True)
            results[carrier] = CrawlResult(
                carrier=carrier,
                success=False,
                error_message=f"Unexpected error: {e}",
            )
            continue

    # 4. 성공한 데이터만 저장
    if all_processed:
        stored_path = store.store(all_processed, execution_date)
        logger.info(f"데이터 저장 완료: {stored_path} ({len(all_processed)}개 요금제)")
    else:
        logger.warning("모든 통신사 크롤링 실패 — 데이터 미저장")

    # 결과 요약
    failed_carriers = [c for c, r in results.items() if not r.success]
    pipeline_result = PipelineResult(
        execution_date=execution_date,
        results=results,
        total_plans_stored=len(all_processed),
        failed_carriers=failed_carriers,
    )

    logger.info(f"=== 파이프라인 완료 ===")
    logger.info(f"  성공: {[c for c, r in results.items() if r.success]}")
    logger.info(f"  실패: {failed_carriers}")
    logger.info(f"  저장된 요금제: {len(all_processed)}개")

    # 모든 통신사 실패 시 exit code 1 (GitHub Actions에서 실패로 표시)
    if len(failed_carriers) == len(crawlers):
        logger.error("모든 통신사 크롤링 실패!")
        sys.exit(1)

    return pipeline_result


if __name__ == "__main__":
    run_pipeline()
