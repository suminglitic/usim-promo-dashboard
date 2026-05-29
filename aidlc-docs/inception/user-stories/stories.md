# User Stories

## Epic 1: 데이터 수집 (Data Collection)

### US-01: SKT 요금제 크롤링 [Must]
**As a** 요금제 분석가  
**I want** SKT T월드 다이렉트 USIM 페이지에서 요금제 정보가 자동으로 수집되기를  
**So that** 수동으로 사이트를 방문하지 않아도 최신 SKT 요금제 현황을 파악할 수 있다

**Acceptance Criteria:**
- **Given** 매일 오전 10:00 KST가 되었을 때
- **When** 크롤링 워크플로우가 트리거되면
- **Then** https://shop.tworld.co.kr/exhibition/view?exhibitionId=P00000326 에서 요금제명, 월정액, 체감가, 혜택 정보를 추출한다

- **Given** SKT 페이지가 정상 로드되었을 때
- **When** HTML 파싱을 시도하면
- **Then** BeautifulSoup으로 정적 파싱을 먼저 시도하고, 실패 시 Selenium으로 전환한다

- **Given** 크롤링이 데이터를 찾지 못했을 때
- **When** 파싱 결과가 비어있으면
- **Then** 빈 데이터를 적재하지 않고 에러를 반환하여 배치를 중단한다

---

### US-02: KT 요고 요금제 크롤링 [Must]
**As a** 요금제 분석가  
**I want** KT 요고 이벤트 페이지에서 요금제 및 혜택 정보가 자동으로 수집되기를  
**So that** KT의 페이백, OTT 혜택, 쿠폰팩 할인 정보를 놓치지 않고 추적할 수 있다

**Acceptance Criteria:**
- **Given** 크롤링 워크플로우가 시작되었을 때
- **When** https://shop.kt.com/unify/yogoEvent.do 에 접근하면
- **Then** 요금제명, 카카오페이/네이버페이 페이백 금액, 초이스/플러스(OTT) 혜택, 월별 쿠폰팩 할인 금액을 추출한다

- **Given** KT 페이지의 혜택 정보가 이미지처럼 보이나 HTML 텍스트로 존재할 때
- **When** 파싱을 수행하면
- **Then** 해당 영역의 텍스트 데이터를 정상적으로 추출한다

---

### US-03: LG U+ 너겟 요금제 크롤링 [Must]
**As a** 요금제 분석가  
**I want** LG U+ 너겟 USIM 주문서 페이지에서 요금제 혜택 정보가 자동으로 수집되기를  
**So that** LG U+의 네이버페이/너겟쿠폰 프로모션 변동을 실시간으로 추적할 수 있다

**Acceptance Criteria:**
- **Given** 크롤링 워크플로우가 시작되었을 때
- **When** https://www.lguplus.com/mobile/self-usim/activate?regType=&selfYn=true&dvicType=U-5G02&usimYn=Y 에 접근하면
- **Then** 주문서 페이지 중간의 한글 텍스트 영역에서 요금제명, 혜택 금액, 지급 조건(월 금액x개월수)을 추출한다

- **Given** 정적 파싱이 실패했을 때
- **When** JavaScript 렌더링이 필요한 콘텐츠가 감지되면
- **Then** Selenium 헤드리스 브라우저로 전환하여 데이터를 추출한다

---

### US-04: 배치 스케줄링 [Must]
**As a** 시스템 운영자  
**I want** 크롤링이 매일 정해진 시간에 자동으로 실행되기를  
**So that** 수동 개입 없이 일관된 데이터 수집이 보장된다

**Acceptance Criteria:**
- **Given** Amazon EventBridge 스케줄이 설정되어 있을 때
- **When** 매일 오전 10:00 KST가 되면
- **Then** 3사 크롤링 Lambda 함수가 트리거된다

- **Given** Lambda 함수가 트리거되었을 때
- **When** 실행이 시작되면
- **Then** 15분 이내에 모든 크롤링이 완료된다

---

## Epic 2: 데이터 처리 (Data Processing)

### US-05: 데이터 전처리 [Must]
**As a** 요금제 분석가  
**I want** 수집된 원시 데이터가 자동으로 정제되기를  
**So that** 통일된 형식으로 3사 요금제를 비교할 수 있다

**Acceptance Criteria:**
- **Given** 원시 크롤링 데이터가 수집되었을 때
- **When** 전처리 파이프라인이 실행되면
- **Then** 통화 기호(₩, 원)가 제거되고 숫자로 변환된다
- **And** 요금제명이 정규화된다 (공백, 특수문자 통일)
- **And** 체감가가 명시되지 않은 경우 (월정액 - 할인액)으로 계산된다

---

### US-06: 데이터 적재 [Must]
**As a** 시스템 운영자  
**I want** 전처리된 데이터가 S3에 일별 스냅샷으로 저장되기를  
**So that** 과거 데이터를 Athena로 쿼리하여 트렌드 분석이 가능하다

**Acceptance Criteria:**
- **Given** 전처리가 완료되었을 때
- **When** 데이터 적재가 실행되면
- **Then** S3 버킷에 날짜별 파티션(year/month/day)으로 저장된다
- **And** Athena에서 즉시 쿼리 가능한 형식(Parquet/CSV)으로 저장된다

- **Given** 90일이 경과한 데이터가 있을 때
- **When** 보존 정책이 적용되면
- **Then** 90일 초과 데이터는 자동 삭제 또는 아카이브된다

---

## Epic 3: 대시보드 (Dashboard)

### US-07: 3사 요금제 비교 테이블 [Must]
**As a** 요금제 분석가  
**I want** 3사 USIM 요금제를 한눈에 비교할 수 있는 테이블을 보기를  
**So that** 경쟁사 대비 자사 요금제의 포지셔닝을 즉시 파악할 수 있다

**Acceptance Criteria:**
- **Given** 사용자가 대시보드 URL에 접속했을 때
- **When** 비교 테이블 뷰를 선택하면
- **Then** SKT, KT, LG U+ 요금제가 통합 테이블로 표시된다
- **And** 컬럼은 통신사, 요금제명, 월정액, 체감가, 페이백 혜택, 최종 수집일을 포함한다
- **And** 최신 크롤링 데이터 기준으로 표시된다

- **Given** 사용자가 로그인 없이 URL에 접속했을 때
- **When** 페이지가 로드되면
- **Then** 별도 인증 없이 즉시 데이터가 표시된다

---

### US-08: 요금제 트렌드 차트 [Must]
**As a** 팀 리더  
**I want** 주요 요금제의 월정액과 체감가 변화 추이를 시계열 그래프로 보기를  
**So that** 경쟁사 프로모션 트렌드를 파악하고 전략적 의사결정을 할 수 있다

**Acceptance Criteria:**
- **Given** 사용자가 대시보드에서 트렌드 뷰를 선택했을 때
- **When** 차트가 렌더링되면
- **Then** 최근 90일간의 월정액 변화 추이가 라인 차트로 표시된다
- **And** 최근 90일간의 체감가 변화 추이가 라인 차트로 표시된다
- **And** 주요 요금제별로 개별 라인이 구분된다

---

### US-09: 데이터 수집 상태 표시 [Should]
**As a** 시스템 운영자  
**I want** 대시보드에서 마지막 데이터 수집 시간을 확인할 수 있기를  
**So that** 크롤링이 정상 동작하는지 빠르게 파악할 수 있다

**Acceptance Criteria:**
- **Given** 사용자가 대시보드에 접속했을 때
- **When** 페이지가 로드되면
- **Then** 각 통신사별 마지막 성공 수집 시간이 표시된다
- **And** 수집 실패 시 해당 통신사에 경고 표시가 나타난다

---

## Epic 4: 에러 처리 (Error Handling)

### US-10: 크롤링 실패 시 안전 중단 [Must]
**As a** 시스템 운영자  
**I want** 크롤링이 실패했을 때 빈 데이터가 저장되지 않기를  
**So that** 잘못된 데이터로 인한 분석 오류를 방지할 수 있다

**Acceptance Criteria:**
- **Given** 크롤러가 대상 사이트에서 데이터를 찾지 못했을 때
- **When** 파싱 결과가 비어있거나 예상 구조와 다르면
- **Then** 빈 데이터를 S3에 적재하지 않는다
- **And** 에러를 즉시 반환하여 해당 통신사의 배치 처리를 중단한다
- **And** 다른 통신사의 크롤링은 독립적으로 계속 진행된다

---

### US-11: 부분 실패 시 기존 데이터 유지 [Should]
**As a** 요금제 분석가  
**I want** 일부 통신사 크롤링이 실패해도 나머지 데이터는 정상 표시되기를  
**So that** 부분적 장애가 전체 분석을 방해하지 않는다

**Acceptance Criteria:**
- **Given** 3사 중 일부 통신사의 크롤링이 실패했을 때
- **When** 대시보드에 접속하면
- **Then** 성공한 통신사의 최신 데이터는 정상 표시된다
- **And** 실패한 통신사는 마지막 성공 데이터를 표시하며 수집 실패 경고를 함께 보여준다

---

## Story-Persona Mapping

| Story | 요금제 분석가 | 팀 리더 | 시스템 운영자 |
|-------|:---:|:---:|:---:|
| US-01 SKT 크롤링 | ● | | ○ |
| US-02 KT 크롤링 | ● | | ○ |
| US-03 LG 크롤링 | ● | | ○ |
| US-04 배치 스케줄링 | | | ● |
| US-05 데이터 전처리 | ● | | ○ |
| US-06 데이터 적재 | | | ● |
| US-07 비교 테이블 | ● | ○ | |
| US-08 트렌드 차트 | ○ | ● | |
| US-09 수집 상태 표시 | | | ● |
| US-10 실패 시 안전 중단 | | | ● |
| US-11 부분 실패 처리 | ● | ○ | ● |

● = Primary User, ○ = Secondary User

## Priority Summary (MoSCoW)

| Priority | Stories |
|----------|---------|
| **Must** | US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10 |
| **Should** | US-09, US-11 |
| **Could** | — |
| **Won't** | — |
