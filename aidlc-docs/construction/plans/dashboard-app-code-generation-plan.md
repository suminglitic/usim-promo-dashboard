# Code Generation Plan — dashboard-app

## Unit Context
- **Unit**: dashboard-app
- **Stories**: US-07, US-08, US-09, US-11
- **실행 환경**: Streamlit Community Cloud
- **데이터 소스**: GitHub Repo CSV (data/ 폴더)

## Generation Steps

- [x] Step 1: 프로젝트 구조 생성 (dashboard-app/ 디렉토리)
- [x] Step 2: 데이터 로더 구현 (data/data_loader.py) — US-07, US-08
- [x] Step 3: 메인 앱 (app.py) — US-09
- [x] Step 4: 비교 테이블 페이지 (pages/1_comparison.py) — US-07
- [x] Step 5: 트렌드 차트 페이지 (pages/2_trend.py) — US-08
- [x] Step 6: Streamlit 설정 (.streamlit/config.toml)
- [x] Step 7: requirements.txt 생성

## Story Coverage
| Story | Step |
|-------|------|
| US-07 (비교 테이블) | Step 2, 4 |
| US-08 (트렌드 차트) | Step 2, 5 |
| US-09 (수집 상태 표시) | Step 3 |
| US-11 (부분 실패 처리) | Step 3, 4 |
