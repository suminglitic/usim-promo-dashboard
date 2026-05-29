# Services

## Service 1: CrawlOrchestrationService

| 항목 | 내용 |
|------|------|
| **이름** | CrawlOrchestrationService |
| **목적** | 크롤링 워크플로우 전체 오케스트레이션 |
| **실행 환경** | AWS Lambda |
| **트리거** | Amazon EventBridge (매일 KST 10:00) |

### 오케스트레이션 흐름
1. EventBridge → Lambda 트리거
2. 3사 크롤링 병렬 실행 (SKT, KT, LG 독립적)
3. 각 통신사별 결과 검증 (validate_result)
4. 유효한 데이터만 전처리 (DataProcessor)
5. 전처리 완료 데이터 S3 적재 (DataStore)
6. 실패한 통신사는 에러 로깅 후 나머지 계속 진행

### 에러 처리 전략
- **통신사별 독립 실행**: 1사 실패가 다른 2사에 영향 없음
- **빈 데이터 방지**: validate_result 실패 시 해당 통신사 적재 중단
- **부분 성공 허용**: 성공한 통신사 데이터만 적재

---

## Service 2: DashboardService

| 항목 | 내용 |
|------|------|
| **이름** | DashboardService |
| **목적** | 대시보드 데이터 조회 및 표시 오케스트레이션 |
| **실행 환경** | Streamlit Community Cloud |
| **접근 방식** | Public URL, 인증 없음 |

### 오케스트레이션 흐름
1. 사용자 대시보드 접속
2. S3/Athena에서 최신 데이터 조회
3. 비교 테이블 또는 트렌드 차트 렌더링
4. 수집 상태 표시 (마지막 수집 시간)

### 데이터 접근 패턴
- **비교 테이블**: 최신 1일 데이터 조회 (query_latest)
- **트렌드 차트**: 최근 90일 시계열 조회 (query_trend)
- **캐싱**: Streamlit 내장 캐시 활용 (@st.cache_data, TTL=1시간)
