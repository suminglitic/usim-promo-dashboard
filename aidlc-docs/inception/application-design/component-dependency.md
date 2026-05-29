# Component Dependencies

## Dependency Matrix

| Component | Depends On | Communication |
|-----------|-----------|---------------|
| Scheduler | CrawlerEngine, DataProcessor, DataStore | 직접 호출 (동일 Lambda 내) |
| CrawlerEngine | (외부 웹사이트) | HTTP GET |
| DataProcessor | — | 순수 데이터 변환 (의존성 없음) |
| DataStore | AWS S3, AWS Athena | AWS SDK (boto3) |
| Dashboard | DataStore | S3/Athena 쿼리 |

## Data Flow

```
+------------------+     +------------------+     +------------------+
|   EventBridge    | --> |    Scheduler     | --> |  CrawlerEngine   |
|  (cron trigger)  |     |   (Lambda)       |     | (SKT/KT/LG)     |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |  DataProcessor   |
                                                  | (clean/normalize)|
                                                  +------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |    DataStore     |
                                                  |  (S3 + Athena)   |
                                                  +------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |    Dashboard     |
                                                  |   (Streamlit)    |
                                                  +------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |      User        |
                                                  | (Web Browser)    |
                                                  +------------------+
```

## Communication Patterns

### 1. Scheduler → CrawlerEngine (동기 호출)
- Lambda 핸들러 내에서 직접 함수 호출
- 3사 크롤링은 순차 또는 ThreadPoolExecutor 병렬 실행

### 2. CrawlerEngine → 외부 웹사이트 (HTTP)
- requests 라이브러리 (정적 파싱)
- Selenium WebDriver (동적 렌더링 fallback)
- 타임아웃: 30초

### 3. Scheduler → DataProcessor (동기 호출)
- 동일 Lambda 내 직접 함수 호출
- 크롤링 결과를 인자로 전달

### 4. Scheduler → DataStore (AWS SDK)
- boto3 S3 client로 Parquet 파일 업로드
- 동일 Lambda 실행 컨텍스트 내

### 5. Dashboard → DataStore (AWS SDK / Athena)
- boto3로 S3에서 직접 Parquet 읽기 (최신 데이터)
- 또는 Athena 쿼리 (트렌드 데이터)
- Streamlit 캐시로 반복 쿼리 최소화

## Deployment Boundary

| 배포 단위 | 컴포넌트 | 환경 |
|-----------|----------|------|
| GitHub Actions Job | Scheduler + CrawlerEngine + DataProcessor + DataStore(write) | GitHub Actions Runner |
| Streamlit App | Dashboard + DataStore(read) | Streamlit Community Cloud |
