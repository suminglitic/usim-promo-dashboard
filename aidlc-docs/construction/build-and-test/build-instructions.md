# Build Instructions

## Prerequisites
- **Python**: 3.11+
- **pip**: 최신 버전
- **Chrome**: Stable (Selenium 사용 시)
- **Git**: 최신 버전

## Build Steps

### 1. 크롤링 파이프라인 의존성 설치
```bash
cd crawl-pipeline
pip install -r requirements.txt
```

### 2. 대시보드 의존성 설치
```bash
cd dashboard-app
pip install -r requirements.txt
```

### 3. 크롤러 로컬 실행 테스트
```bash
cd crawl-pipeline
python main.py
```

**예상 결과:**
- `data/latest.csv` 생성
- `data/history/YYYY-MM-DD.csv` 생성
- `data/metadata.json` 업데이트
- 콘솔에 3사 크롤링 결과 출력

### 4. 대시보드 로컬 실행 테스트
```bash
cd dashboard-app
streamlit run app.py
```

**예상 결과:**
- 브라우저에서 `http://localhost:8501` 접속 가능
- 비교 테이블 및 트렌드 차트 페이지 정상 표시

## Troubleshooting

### Chrome/Selenium 관련 오류
- **원인**: Chrome 미설치 또는 버전 불일치
- **해결**: `pip install webdriver-manager` 후 재실행

### 크롤링 타임아웃
- **원인**: 대상 사이트 응답 지연 또는 차단
- **해결**: `config.py`의 `CRAWL_TIMEOUT` 값 증가 (기본 30초)

### 데이터 디렉토리 오류
- **원인**: `data/history/` 디렉토리 미존재
- **해결**: `mkdir -p data/history` 실행
