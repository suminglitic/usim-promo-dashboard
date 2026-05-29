# 📱 통신 3사 USIM 요금제 프로모션 대시보드

SKT, KT, LG U+의 USIM 단독 요금제 프로모션을 자동으로 크롤링하여 비교/분석하는 대시보드입니다.

## 아키텍처

```
GitHub Actions (매일 KST 10:00)
    → 3사 웹 크롤링 (BeautifulSoup + Selenium)
    → 데이터 전처리 (Pandas)
    → CSV 저장 (data/ 폴더)
    → Git commit & push

Streamlit Community Cloud
    → data/ 폴더에서 CSV 읽기
    → 비교 테이블 + 트렌드 차트 표시
```

## 프로젝트 구조

```
├── .github/workflows/crawl.yml   # 매일 자동 크롤링
├── crawl-pipeline/               # 크롤링 파이프라인
│   ├── main.py                   # 메인 오케스트레이터
│   ├── crawlers/                 # 통신사별 크롤러
│   ├── processor/                # 데이터 전처리
│   ├── store/                    # CSV 저장
│   └── models/                   # 데이터 모델
├── dashboard-app/                # Streamlit 대시보드
│   ├── app.py                    # 메인 앱
│   ├── pages/                    # 비교 테이블, 트렌드 차트
│   └── data/                     # 데이터 로더
├── data/                         # 크롤링 데이터 (자동 생성)
│   ├── latest.csv
│   ├── history/
│   └── metadata.json
└── README.md
```

## 수집 대상

| 통신사 | URL | 수집 항목 |
|--------|-----|-----------|
| SKT | [T월드 다이렉트 USIM](https://shop.tworld.co.kr/exhibition/view?exhibitionId=P00000326) | 요금제명, 월정액, 혜택 |
| KT | [요고 이벤트](https://shop.kt.com/unify/yogoEvent.do) | 요금제명, 페이백, OTT 혜택 |
| LG U+ | [너겟 USIM 주문서](https://www.lguplus.com/mobile/self-usim/activate?regType=&selfYn=true&dvicType=U-5G02&usimYn=Y) | 요금제명, 네이버페이/너겟쿠폰 혜택 |

## 로컬 실행

### 크롤러 실행
```bash
cd crawl-pipeline
pip install -r requirements.txt
cd ..
python -m crawl_pipeline.main
```

### 대시보드 실행
```bash
cd dashboard-app
pip install -r requirements.txt
streamlit run app.py
```

## 배포

### 크롤링 (자동)
- GitHub Actions가 매일 KST 10:00에 자동 실행
- 수동 실행: GitHub > Actions > Daily USIM Crawl > Run workflow

### 대시보드
1. [Streamlit Community Cloud](https://share.streamlit.io/) 접속
2. 이 GitHub repo 연결
3. Main file path: `dashboard-app/app.py`
4. Deploy

## 비용

**$0/월** — 모든 서비스 무료 tier 사용
- GitHub Actions: Public repo 무제한 / Private repo 월 2,000분
- Streamlit Community Cloud: 무료
- 데이터 저장: GitHub repo 내 CSV

## 기술 스택

- **크롤링**: Python, BeautifulSoup4, Selenium
- **스케줄링**: GitHub Actions (cron)
- **데이터 처리**: Pandas
- **대시보드**: Streamlit, Plotly
- **저장소**: GitHub Repository (CSV)
