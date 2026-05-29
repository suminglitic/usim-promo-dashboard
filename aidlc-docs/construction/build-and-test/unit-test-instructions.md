# Unit Test Execution

## 테스트 프레임워크
- **pytest** (Python 표준 테스트 프레임워크)

## 설치
```bash
pip install pytest pytest-cov
```

## 테스트 실행

### 1. 전체 단위 테스트 실행
```bash
cd crawl-pipeline
pytest tests/ -v
```

### 2. 개별 모듈 테스트
```bash
# 데이터 전처리 테스트
pytest tests/test_processor.py -v

# CSV 저장 테스트
pytest tests/test_store.py -v

# 크롤러 테스트 (mock 사용)
pytest tests/test_crawlers.py -v
```

### 3. 커버리지 확인
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

## 핵심 테스트 케이스

### DataProcessor 테스트
| 테스트 | 입력 | 기대 결과 |
|--------|------|-----------|
| clean_currency("6만9천원") | "6만9천원" | 69000 |
| clean_currency("28만8천원") | "28만8천원" | 288000 |
| clean_currency("5천원") | "5천원" | 5000 |
| clean_currency("69,000원") | "69,000원" | 69000 |
| normalize_plan_name("  너겟  69 ") | "  너겟  69 " | "너겟 69" |
| 체감가 계산 | 월정액 69000, 혜택 288000/12개월 | 45000 |

### CsvStore 테스트
| 테스트 | 검증 항목 |
|--------|-----------|
| store() | latest.csv 생성 확인 |
| store() | history/{date}.csv 생성 확인 |
| store() | metadata.json 업데이트 확인 |
| cleanup_expired() | 90일 초과 파일 삭제 확인 |
| store() 빈 데이터 | 파일 미생성 확인 |

### Crawler 테스트 (Mock)
| 테스트 | 검증 항목 |
|--------|-----------|
| crawl() 정적 파싱 성공 | BS4로 데이터 추출 |
| crawl() 정적 실패 → Selenium | fallback 동작 확인 |
| crawl() 모두 실패 | CrawlFailureError 발생 |
| validate_result() 빈 데이터 | False 반환 |

## 기대 결과
- **총 테스트**: ~20개
- **통과**: 전체
- **커버리지**: 80%+ (크롤러 파싱 로직 제외 — 외부 사이트 의존)
