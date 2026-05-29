# Unit of Work Dependencies

## Dependency Matrix

| Unit | Depends On | Shared Resource | Communication |
|------|-----------|-----------------|---------------|
| crawl-pipeline | 외부 웹사이트 (SKT/KT/LG) | S3 Bucket (write) | HTTP, AWS SDK |
| dashboard-app | S3 Bucket (read) | S3 Bucket (read) | AWS SDK, Athena |

## Inter-Unit Communication

```
+------------------+          +------------------+
|  crawl-pipeline  |  ------> |    Amazon S3     |  <------  | dashboard-app  |
|  (Lambda)        |  writes  | (Parquet files)  |  reads    | (Streamlit)    |
+------------------+          +------------------+           +------------------+
```

### 결합 방식: Loose Coupling via S3
- **crawl-pipeline** → S3에 Parquet 파일 쓰기 (Producer)
- **dashboard-app** → S3에서 Parquet 파일 읽기 (Consumer)
- 두 단위 간 직접 통신 없음
- S3 파일 포맷(Parquet 스키마)이 유일한 계약(Contract)

## 개발 순서

| 순서 | Unit | 이유 |
|------|------|------|
| 1 | crawl-pipeline | 데이터가 있어야 대시보드 개발/테스트 가능 |
| 2 | dashboard-app | crawl-pipeline이 생성한 데이터를 소비 |

### 병렬 개발 가능 여부
- **가능**: 데이터 스키마(ProcessedPlanData)를 먼저 합의하면 병렬 개발 가능
- **방법**: 샘플 Parquet 파일을 생성하여 dashboard-app 개발 시 mock 데이터로 활용

## 공유 리소스

| 리소스 | 용도 | 접근 단위 |
|--------|------|-----------|
| S3 Bucket | 크롤링 데이터 저장소 | crawl-pipeline (RW), dashboard-app (RO) |
| Athena Database | 트렌드 쿼리 | dashboard-app (RO) |
| Athena Table | S3 데이터 위의 스키마 정의 | 인프라 설정 시 생성 |

## 배포 독립성

| 항목 | crawl-pipeline | dashboard-app |
|------|---------------|---------------|
| 배포 환경 | AWS Lambda | Streamlit Community Cloud |
| 배포 방법 | ZIP 업로드 또는 SAM/CDK | GitHub push → 자동 배포 |
| 스케일링 | Lambda 자동 (동시성 1 충분) | Streamlit Cloud 관리 |
| 모니터링 | CloudWatch Logs | Streamlit Cloud 로그 |
