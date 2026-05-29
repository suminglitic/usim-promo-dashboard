# Integration Test Instructions

## Purpose
crawl-pipeline과 dashboard-app 간의 데이터 연동을 검증합니다.

## Test Scenarios

### Scenario 1: 크롤링 → CSV 저장 → 대시보드 로딩
- **Description**: 크롤러가 생성한 CSV를 대시보드가 정상적으로 읽는지 확인
- **Setup**: 크롤러 1회 실행하여 data/ 폴더에 CSV 생성
- **Test Steps**:
  1. `python crawl-pipeline/main.py` 실행
  2. `data/latest.csv` 파일 존재 확인
  3. `data/history/YYYY-MM-DD.csv` 파일 존재 확인
  4. `dashboard-app/data/data_loader.py`의 `load_latest_data()` 호출
  5. 반환된 DataFrame이 비어있지 않은지 확인
  6. 컬럼 스키마 일치 확인 (carrier, plan_name, monthly_fee, perceived_price, ...)
- **Expected Results**: 대시보드가 크롤러 출력 CSV를 정상 파싱
- **Cleanup**: 테스트 데이터 삭제 불필요 (실제 데이터로 활용)

### Scenario 2: 부분 실패 시 대시보드 동작
- **Description**: 일부 통신사 크롤링 실패 시 대시보드가 정상 동작하는지 확인
- **Setup**: 의도적으로 1사 URL을 잘못된 값으로 변경 후 크롤링 실행
- **Test Steps**:
  1. config.py에서 SKT URL을 임시로 잘못된 URL로 변경
  2. `python crawl-pipeline/main.py` 실행
  3. KT, LG 데이터만 CSV에 저장되었는지 확인
  4. 대시보드에서 KT, LG 데이터 정상 표시 확인
  5. metadata.json에서 SKT 실패 상태 확인
- **Expected Results**: 실패한 통신사 제외, 나머지 정상 동작
- **Cleanup**: config.py 원복

### Scenario 3: 트렌드 데이터 누적
- **Description**: 여러 날의 데이터가 트렌드 차트에 정상 표시되는지 확인
- **Setup**: history/ 폴더에 샘플 CSV 2~3개 생성
- **Test Steps**:
  1. `data/history/2026-05-27.csv`, `2026-05-28.csv`, `2026-05-29.csv` 생성
  2. `load_trend_data(days=90)` 호출
  3. 3일치 데이터가 합쳐진 DataFrame 반환 확인
  4. 트렌드 차트 페이지에서 라인 차트 정상 렌더링 확인
- **Expected Results**: 복수 날짜 데이터가 시계열로 표시

## 실행 방법

```bash
# 통합 테스트 (수동)
# 1. 크롤러 실행
cd crawl-pipeline
python main.py

# 2. 대시보드 실행 후 데이터 확인
cd ../dashboard-app
streamlit run app.py
# 브라우저에서 비교 테이블, 트렌드 차트 확인
```

## 자동화 (향후)
- GitHub Actions에서 크롤링 후 대시보드 smoke test 추가 가능
- `streamlit run app.py --server.headless true` + curl 헬스체크
