# Code Generation Plan — crawl-pipeline

## Unit Context
- **Unit**: crawl-pipeline
- **Stories**: US-01, US-02, US-03, US-04, US-05, US-06, US-10, US-11
- **실행 환경**: GitHub Actions Runner
- **데이터 저장**: GitHub Repo CSV

## Generation Steps

- [x] Step 1: 프로젝트 구조 생성 (crawl-pipeline/ 디렉토리)
- [x] Step 2: 데이터 모델 생성 (models/plan_data.py)
- [x] Step 3: 설정 파일 생성 (config.py)
- [x] Step 4: 기본 크롤러 추상 클래스 (crawlers/base.py)
- [x] Step 5: SKT 크롤러 구현 (crawlers/skt_crawler.py) — US-01
- [x] Step 6: KT 크롤러 구현 (crawlers/kt_crawler.py) — US-02
- [x] Step 7: LG U+ 크롤러 구현 (crawlers/lg_crawler.py) — US-03
- [x] Step 8: 데이터 전처리 구현 (processor/data_processor.py) — US-05
- [x] Step 9: 데이터 저장 구현 (store/csv_store.py) — US-06
- [x] Step 10: 메인 오케스트레이터 (main.py) — US-04, US-10, US-11
- [x] Step 11: requirements.txt 생성
- [x] Step 12: GitHub Actions 워크플로우 (.github/workflows/crawl.yml) — US-04

## Story Coverage
| Story | Step |
|-------|------|
| US-01 (SKT 크롤링) | Step 5 |
| US-02 (KT 크롤링) | Step 6 |
| US-03 (LG 크롤링) | Step 7 |
| US-04 (배치 스케줄링) | Step 10, 12 |
| US-05 (데이터 전처리) | Step 8 |
| US-06 (데이터 적재) | Step 9 |
| US-10 (실패 시 안전 중단) | Step 10 |
| US-11 (부분 실패 처리) | Step 10 |
