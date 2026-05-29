# Infrastructure Design — dashboard-app (완전 무료)

## 배포 환경: Streamlit Community Cloud

| 항목 | 설정 |
|------|------|
| **Platform** | Streamlit Community Cloud |
| **Cost** | 무료 |
| **Source** | GitHub Repository 연동 (동일 repo) |
| **Auto Deploy** | main 브랜치 push 시 자동 배포 |
| **URL** | https://{app-name}.streamlit.app |
| **Entry Point** | dashboard-app/app.py |

## 데이터 접근 방식 변경

### 이전 (AWS)
- S3에서 Parquet 읽기 (boto3)
- Athena SQL 쿼리

### 변경 (무료)
- **같은 GitHub repo의 `data/` 폴더에서 CSV 직접 읽기**
- Streamlit Cloud가 repo를 클론하므로 로컬 파일처럼 접근 가능
- AWS SDK 불필요, IAM 불필요

### 데이터 로딩 방식
```python
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# 최신 데이터
latest_df = pd.read_csv(os.path.join(DATA_DIR, 'latest.csv'))

# 트렌드 데이터 (history 폴더의 모든 CSV)
history_files = sorted(glob.glob(os.path.join(DATA_DIR, 'history', '*.csv')))
trend_df = pd.concat([pd.read_csv(f) for f in history_files])
```

## Repository 구조 (단일 Monorepo)

```
usim-promo-dashboard/          # GitHub Repository
├── .github/
│   └── workflows/
│       └── crawl.yml          # GitHub Actions 크롤링 워크플로우
├── crawl-pipeline/            # 크롤링 코드
│   ├── main.py
│   ├── crawlers/
│   ├── processor/
│   ├── requirements.txt
│   └── ...
├── dashboard-app/             # Streamlit 대시보드 코드
│   ├── app.py
│   ├── pages/
│   ├── requirements.txt
│   └── .streamlit/
├── data/                      # 크롤링 데이터 (Git 추적)
│   ├── latest.csv
│   ├── history/
│   └── metadata.json
└── README.md
```

## Streamlit Cloud 설정

### App 설정
- **Repository**: github.com/{user}/usim-promo-dashboard
- **Branch**: main
- **Main file path**: dashboard-app/app.py
- **Python version**: 3.11

### 데이터 갱신 메커니즘
1. GitHub Actions가 매일 크롤링 실행
2. 결과를 `data/` 폴더에 커밋 & 푸시
3. Streamlit Cloud가 repo 변경 감지 → 자동 재배포
4. 사용자가 대시보드 접속 시 최신 데이터 표시

### 주의: Streamlit Cloud 캐시
- `@st.cache_data`는 앱 재시작 시 초기화됨
- repo push로 앱이 재배포되면 캐시 자동 갱신
- 수동 새로고침: 사용자가 브라우저 새로고침하면 최신 데이터 로드

## 비용 요약

| 서비스 | 비용 |
|--------|------|
| Streamlit Community Cloud | 무료 |
| GitHub Repository | 무료 |
| **합계** | **$0/월** |

## 제한사항

| 제한 | 영향 | 대응 |
|------|------|------|
| 앱 슬립 (미사용 시) | 접속 시 ~30초 재시작 | 내부 5명 사용, 허용 가능 |
| 1GB RAM | 90일 CSV 데이터 = 수십 KB | 전혀 문제 없음 |
| 재배포 시간 | push 후 1~2분 | 데이터 갱신 지연 허용 가능 |
