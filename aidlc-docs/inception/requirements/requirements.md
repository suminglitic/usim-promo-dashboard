# Requirements Document: 통신 3사 USIM 요금제 프로모션 크롤링 대시보드

## Intent Analysis

| 항목 | 내용 |
|------|------|
| **Request Type** | New Project (신규 프로젝트) |
| **Scope** | Multiple Components (크롤러 + 데이터 파이프라인 + 대시보드) |
| **Complexity** | Moderate (웹 크롤링 + 데이터 처리 + 시각화) |
| **Project Type** | Greenfield |

## 1. Functional Requirements

### FR-01: 웹 크롤링 — SKT
- **대상 URL**: https://shop.tworld.co.kr/exhibition/view?exhibitionId=P00000326
- **수집 데이터**: 요금제명, 기본 월정액, 프로모션 적용 후 체감가, 혜택/사은품 정보
- **크롤링 방식**: BeautifulSoup(정적 파싱) 우선 시도, 실패 시 Selenium(헤드리스 브라우저)으로 전환

### FR-02: 웹 크롤링 — KT
- **대상 URL**: https://shop.kt.com/unify/yogoEvent.do
- **수집 데이터**: 요금제명(요고 61, 요고 69 등), 카카오페이/네이버페이 페이백 금액, 초이스/플러스(OTT) 혜택, 월별 쿠폰팩 할인 금액
- **크롤링 방식**: BeautifulSoup 우선, 실패 시 Selenium 전환
- **특이사항**: 혜택 정보가 이미지처럼 보이나 HTML 텍스트로 존재하는 영역 정상 파싱 필수

### FR-03: 웹 크롤링 — LG U+
- **대상 URL**: https://www.lguplus.com/mobile/self-usim/activate?regType=&selfYn=true&dvicType=U-5G02&usimYn=Y
- **수집 데이터**: 요금제명(너겟47 등), 기본 월정액, 프로모션 적용 후 체감가, 네이버페이/너겟쿠폰 혜택 금액 및 지급 조건
- **크롤링 방식**: BeautifulSoup 우선, 실패 시 Selenium 전환
- **특이사항**: 주문서 페이지 중간에 위치한 한글 텍스트 영역에서 혜택 정보 추출 필요
- **데이터 예시**:
  - ①네이버페이 등 너겟쿠폰 28만8천원 혜택 → 너겟 69 (액션캠), 2만4천원x12개월
  - ②네이버페이 등 너겟쿠폰 24만원 혜택 → 너겟 59/47 (멀티팩), 2만원x12개월
  - ③네이버페이 등 너겟쿠폰 18만원 혜택 → 너겟 69/65/59, 1만2천원x15개월
  - ④네이버페이 7만5천원 혜택 → 너겟 45/46/51, 5천원x15개월
  - ⑤네이버페이 3만원 혜택 → 너겟 34~44, 5천원x6개월

### FR-04: 배치 스케줄링
- **트리거**: 매일 오전 10:00 KST (Amazon EventBridge)
- **대상**: 3사 크롤링 워크플로우 동시 실행
- **실행 환경**: AWS Lambda

### FR-05: 데이터 전처리
- **처리 내용**:
  - 통화 기호(₩, 원) 제거 및 숫자 변환
  - 요금제명 정규화 (공백, 특수문자 통일)
  - 체감가가 명시되지 않은 경우 계산 (월정액 - 할인액)
- **도구**: Python Pandas

### FR-06: 데이터 적재
- **저장소**: Amazon S3 (일별 스냅샷 append)
- **포맷**: Parquet 또는 CSV (Athena 쿼리 가능)
- **파티셔닝**: 날짜별 (year/month/day)
- **쿼리 엔진**: AWS Athena

### FR-07: 대시보드 — 비교 테이블
- **내용**: 3사 USIM 요금제 통합 비교 테이블
- **컬럼**: 통신사, 요금제명, 월정액, 체감가, 페이백 혜택, 최종 수집일
- **데이터 소스**: 최신 크롤링 데이터 기준

### FR-08: 대시보드 — 트렌드 차트
- **내용**: 시계열 그래프 (Time-series)
- **지표**: 월정액, 체감가 변화 추이
- **범위**: 최근 90일 데이터
- **단위**: 주요 요금제별 라인 차트

### FR-09: 크롤링 실패 처리
- **조건**: 사이트 구조 개편 등으로 데이터를 찾지 못한 경우
- **동작**: 빈 데이터 적재하지 않고 즉시 에러 반환, 배치 처리 중단
- **표시**: 대시보드에 마지막 성공 수집 시간 표시

## 2. Non-Functional Requirements

### NFR-01: 접근성
- 별도 로그인(인증) 없이 URL만으로 즉시 접속 가능
- Open Web(Public) 형태

### NFR-02: 데이터 보존
- 최근 90일 데이터 보존
- 90일 초과 데이터는 자동 삭제 또는 아카이브

### NFR-03: 사용자 규모
- 내부 팀 전용 (5명 이하 동시 접속)
- 고가용성/확장성 요구 낮음

### NFR-04: 알림
- 별도 알림 시스템 불필요
- 대시보드에서 마지막 수집 시간만 표시하여 상태 확인

### NFR-05: 배포 환경
- Streamlit Community Cloud (무료 호스팅)
- GitHub 연동 자동 배포
- 크롤링: GitHub Actions (무료, 월 2,000분 한도)
- 데이터 저장: GitHub Repository 내 CSV 파일

## 3. Technical Architecture Summary

| 컴포넌트 | 기술 스택 |
|----------|-----------|
| 크롤러 | Python, BeautifulSoup4, Selenium (fallback) |
| 스케줄러 | GitHub Actions (cron) |
| 실행 환경 | GitHub Actions Runner |
| 데이터 저장 | GitHub Repository (CSV) |
| 데이터 쿼리 | Python Pandas (메모리 내 처리) |
| 대시보드 | Streamlit |
| 배포 | Streamlit Community Cloud |
| 데이터 처리 | Python Pandas |

## 4. Target URLs

| 통신사 | URL | 비고 |
|--------|-----|------|
| SKT | https://shop.tworld.co.kr/exhibition/view?exhibitionId=P00000326 | T월드 다이렉트 USIM |
| KT | https://shop.kt.com/unify/yogoEvent.do | 요고 이벤트 페이지 |
| LG U+ | https://www.lguplus.com/mobile/self-usim/activate?regType=&selfYn=true&dvicType=U-5G02&usimYn=Y | 너겟 USIM 주문서 (혜택 텍스트 영역) |

## 5. Acceptance Criteria

1. 사용자는 로그인 없이 제공된 URL을 통해 대시보드에 즉시 접속할 수 있어야 한다.
2. KT 요고 페이지의 혜택 정보(이미지처럼 보이나 HTML 텍스트로 존재하는 영역)를 정상적으로 파싱해야 한다.
3. 대시보드는 3사 요금제 직접 비교 테이블(월정액 vs 체감가 vs 페이백 혜택)과 과거 수집 데이터 기반의 트렌드 변화 그래프 두 가지 뷰를 반드시 포함해야 한다.
4. 크롤러가 사이트 구조 개편 등으로 데이터를 찾지 못해 실패할 경우, 빈 데이터를 적재하지 않고 즉시 에러를 반환하여 배치 처리를 중단해야 한다.

## 6. Constraints & Assumptions

- SKT 페이지 URL은 프로모션 기간에 따라 변경될 수 있음 (exhibitionId 파라미터)
- 각 통신사 사이트는 사전 고지 없이 구조가 변경될 수 있음
- Lambda 실행 시간 제한 (15분) 내에 크롤링 완료 필요
- Streamlit Community Cloud의 무료 tier 제한 사항 준수
