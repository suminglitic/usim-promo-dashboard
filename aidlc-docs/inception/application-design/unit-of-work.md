# Units of Work

## 시스템 분해 전략

이 프로젝트는 **2개의 독립 배포 단위**로 분해됩니다:
1. **crawl-pipeline** — AWS Lambda 기반 크롤링 파이프라인
2. **dashboard-app** — Streamlit 기반 대시보드 웹 앱

두 단위는 S3를 통해 느슨하게 결합(loosely coupled)되며, 독립적으로 개발/배포 가능합니다.

---

## Unit 1: crawl-pipeline

| 항목 | 내용 |
|------|------|
| **이름** | crawl-pipeline |
| **유형** | AWS Lambda Function |
| **책임** | 3사 웹 크롤링, 데이터 전처리, S3 적재 |
| **트리거** | Amazon EventBridge (매일 KST 10:00) |
| **포함 컴포넌트** | Scheduler, CrawlerEngine, DataProcessor, DataStore(write) |

### 코드 구조
```
crawl-pipeline/
├── handler.py              # Lambda 핸들러 (진입점)
├── crawlers/
│   ├── __init__.py
│   ├── base.py             # BaseCrawler 추상 클래스
│   ├── skt_crawler.py      # SKT T월드 크롤러
│   ├── kt_crawler.py       # KT 요고 크롤러
│   └── lg_crawler.py       # LG U+ 너겟 크롤러
├── processor/
│   ├── __init__.py
│   └── data_processor.py   # 데이터 전처리 로직
├── store/
│   ├── __init__.py
│   └── s3_store.py         # S3 적재 로직
├── models/
│   ├── __init__.py
│   └── plan_data.py        # 데이터 모델 (RawPlanData, ProcessedPlanData)
├── config.py               # 설정 (URL, S3 버킷명 등)
├── requirements.txt        # Python 의존성
└── tests/
    ├── test_crawlers.py
    ├── test_processor.py
    └── test_store.py
```

### 주요 의존성
- beautifulsoup4, requests (정적 크롤링)
- selenium, chromium (동적 크롤링 fallback)
- pandas (데이터 처리)
- boto3 (AWS SDK)
- pyarrow (Parquet 저장)

---

## Unit 2: dashboard-app

| 항목 | 내용 |
|------|------|
| **이름** | dashboard-app |
| **유형** | Streamlit Web Application |
| **책임** | 데이터 조회, 비교 테이블 렌더링, 트렌드 차트 표시, 수집 상태 표시 |
| **배포** | Streamlit Community Cloud (GitHub 연동) |
| **포함 컴포넌트** | Dashboard, DataStore(read) |

### 코드 구조
```
dashboard-app/
├── app.py                  # Streamlit 메인 앱 (진입점)
├── pages/
│   ├── 1_comparison.py     # 3사 비교 테이블 페이지
│   └── 2_trend.py          # 트렌드 차트 페이지
├── data/
│   ├── __init__.py
│   └── data_loader.py      # S3/Athena 데이터 조회
├── config.py               # 설정 (S3 버킷, Athena DB 등)
├── requirements.txt        # Python 의존성
└── .streamlit/
    └── config.toml         # Streamlit 설정
```

### 주요 의존성
- streamlit (대시보드 프레임워크)
- pandas (데이터 처리)
- plotly (차트 라이브러리)
- boto3 (AWS SDK)
- pyarrow (Parquet 읽기)

---

## 코드 조직 전략 (Greenfield)

```
c:\Users\SKTelecom\Desktop\kiro\     # Workspace Root
├── crawl-pipeline/                   # Unit 1: Lambda 크롤링 파이프라인
├── dashboard-app/                    # Unit 2: Streamlit 대시보드
├── infrastructure/                   # (선택) IaC — EventBridge, Lambda, S3 설정
├── aidlc-docs/                       # AI-DLC 문서 (코드 아님)
└── README.md                         # 프로젝트 개요
```
