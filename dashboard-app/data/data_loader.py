"""데이터 로딩 모듈 — GitHub Repo의 data/ 폴더에서 CSV 읽기"""
import glob
import json
import os

import pandas as pd
import streamlit as st

# 데이터 디렉토리 경로 (repo 루트 기준)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
LATEST_CSV = os.path.join(DATA_DIR, "latest.csv")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")


@st.cache_data(ttl=3600)
def load_latest_data() -> pd.DataFrame:
    """최신 수집 데이터 로드

    Returns:
        최신 요금제 데이터 DataFrame. 데이터 없으면 빈 DataFrame.
    """
    if os.path.exists(LATEST_CSV):
        try:
            df = pd.read_csv(LATEST_CSV, encoding="utf-8-sig")
            return df
        except Exception:
            pass

    # latest.csv 없으면 history에서 가장 최근 파일 로드
    history_files = sorted(glob.glob(os.path.join(HISTORY_DIR, "*.csv")), reverse=True)
    if history_files:
        try:
            return pd.read_csv(history_files[0], encoding="utf-8-sig")
        except Exception:
            pass

    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_trend_data(days: int = 90) -> pd.DataFrame:
    """트렌드 데이터 로드 (최근 N일)

    Args:
        days: 로드할 일수 (기본 90일)

    Returns:
        일별 요금제 데이터가 합쳐진 DataFrame
    """
    history_files = sorted(glob.glob(os.path.join(HISTORY_DIR, "*.csv")))

    # 최근 N개 파일만 로드
    recent_files = history_files[-days:] if len(history_files) > days else history_files

    if not recent_files:
        return pd.DataFrame()

    all_data = []
    for filepath in recent_files:
        try:
            df = pd.read_csv(filepath, encoding="utf-8-sig")
            all_data.append(df)
        except Exception:
            continue

    if all_data:
        return pd.concat(all_data, ignore_index=True)

    return pd.DataFrame()


def load_metadata() -> dict:
    """수집 상태 메타데이터 로드"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_crawl": {"SKT": {}, "KT": {}, "LG": {}}}
