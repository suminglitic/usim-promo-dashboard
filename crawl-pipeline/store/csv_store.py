"""CSV 기반 데이터 저장 모듈 (GitHub Repo)"""
import json
import logging
import os
from datetime import date, datetime, timedelta

import pandas as pd

from config import DATA_DIR, HISTORY_DIR, LATEST_CSV, METADATA_FILE, RETENTION_DAYS
from models import ProcessedPlanData

logger = logging.getLogger(__name__)


class CsvStore:
    """GitHub Repo의 data/ 폴더에 CSV로 데이터 저장"""

    def __init__(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)

    def store(self, data: list[ProcessedPlanData], execution_date: str) -> str:
        """처리된 데이터를 CSV로 저장

        Args:
            data: 정제된 요금제 데이터 리스트
            execution_date: 실행 날짜 (YYYY-MM-DD)

        Returns:
            저장된 history 파일 경로
        """
        if not data:
            logger.warning("저장할 데이터가 없습니다.")
            return ""

        df = pd.DataFrame([d.to_dict() for d in data])

        # latest.csv 덮어쓰기 (대시보드 빠른 로딩용)
        df.to_csv(LATEST_CSV, index=False, encoding="utf-8-sig")
        logger.info(f"latest.csv 저장 완료: {len(data)}개 요금제")

        # history/{date}.csv 추가
        history_path = os.path.join(HISTORY_DIR, f"{execution_date}.csv")
        df.to_csv(history_path, index=False, encoding="utf-8-sig")
        logger.info(f"history/{execution_date}.csv 저장 완료")

        # metadata.json 업데이트
        self._update_metadata(data, execution_date)

        # 90일 초과 파일 삭제
        deleted = self._cleanup_expired()
        if deleted:
            logger.info(f"보존 기간 초과 파일 {deleted}개 삭제")

        return history_path

    def _update_metadata(self, data: list[ProcessedPlanData], execution_date: str):
        """수집 상태 메타데이터 업데이트"""
        metadata = self._load_metadata()

        # 통신사별 상태 업데이트
        carriers_in_data = set(d.carrier for d in data)
        for carrier in carriers_in_data:
            carrier_plans = [d for d in data if d.carrier == carrier]
            metadata["last_crawl"][carrier] = {
                "date": execution_date,
                "success": True,
                "plan_count": len(carrier_plans),
                "updated_at": datetime.now().isoformat(),
            }

        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _load_metadata(self) -> dict:
        """기존 메타데이터 로드"""
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"last_crawl": {"SKT": {}, "KT": {}, "LG": {}}}

    def _cleanup_expired(self) -> int:
        """보존 기간(90일) 초과 파일 삭제"""
        deleted_count = 0
        cutoff_date = date.today() - timedelta(days=RETENTION_DAYS)

        if not os.path.exists(HISTORY_DIR):
            return 0

        for filename in os.listdir(HISTORY_DIR):
            if not filename.endswith(".csv"):
                continue

            # 파일명에서 날짜 추출 (YYYY-MM-DD.csv)
            date_str = filename.replace(".csv", "")
            try:
                file_date = date.fromisoformat(date_str)
                if file_date < cutoff_date:
                    os.remove(os.path.join(HISTORY_DIR, filename))
                    deleted_count += 1
                    logger.debug(f"삭제: {filename} (보존 기간 초과)")
            except ValueError:
                continue

        return deleted_count
