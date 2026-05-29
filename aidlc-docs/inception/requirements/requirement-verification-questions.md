# Requirements Verification Questions

통신 3사 USIM 요금제 프로모션 크롤링 대시보드 프로젝트의 요구사항을 명확히 하기 위한 질문입니다.
각 질문의 [Answer]: 태그 뒤에 선택한 옵션 문자를 입력해 주세요.

---

## Question 1
SKT 데이터 수집 방식은 어떻게 구성하시겠습니까? (자사 데이터라고 언급하셨는데 구체적으로 어떤 소스인지 확인이 필요합니다)

A) SKT 공식 온라인몰 특정 URL에서 크롤링 (URL을 제공해 주세요)

B) 내부 DB 또는 API에서 직접 조회

C) 수동 입력(관리자가 직접 데이터 입력)

D) 1차 버전에서는 SKT 제외, KT/LG만 먼저 구현

X) Other (please describe after [Answer]: tag below)

[Answer]: A
https://shop.tworld.co.kr/exhibition/view?exhibitionId=P00000326

---

## Question 2
대시보드 프레임워크로 Streamlit을 언급하셨는데, 배포 환경은 어떻게 구성하시겠습니까?

A) AWS EC2/ECS에 Streamlit 앱 직접 배포 (항상 실행 상태)

B) AWS Lambda + API Gateway + 정적 프론트엔드 (서버리스)

C) Streamlit Community Cloud (무료 호스팅)

D) AWS Fargate 컨테이너로 배포

X) Other (please describe after [Answer]: tag below)

[Answer]: X
각 옵션을 비교하고 추천해줘 

---

## Question 3
크롤링 실패 시 알림(Notification) 방식은 어떻게 하시겠습니까?

A) Amazon SNS를 통한 이메일 알림

B) Slack/Teams 웹훅 알림

C) CloudWatch Alarm만 설정 (AWS 콘솔에서 확인)

D) 알림 불필요 — 대시보드에서 마지막 수집 시간만 표시

X) Other (please describe after [Answer]: tag below)

[Answer]: D

---

## Question 4
데이터 보존 기간(Retention)은 어떻게 설정하시겠습니까?

A) 최근 30일만 보존

B) 최근 90일 보존

C) 최근 1년 보존

D) 무기한 보존 (모든 히스토리 유지)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 5
대시보드 사용자 규모와 동시 접속 예상치는 어떻게 되나요?

A) 내부 팀 전용 (5명 이하)

B) 부서 단위 (10~30명)

C) 회사 전체 (100명 이상)

D) 외부 공개 (불특정 다수)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 6
KT/LG 사이트가 JavaScript 렌더링(SPA)으로 구성되어 있을 경우 크롤링 방식은 어떻게 하시겠습니까?

A) Selenium/Playwright (헤드리스 브라우저) — Lambda에서 실행

B) Selenium/Playwright — EC2에서 실행

C) 먼저 BeautifulSoup(정적 파싱)으로 시도하고, 실패 시 Selenium으로 전환

D) API 호출 방식 우선 탐색 (네트워크 탭에서 실제 API 엔드포인트 확인)

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 7
트렌드 차트에서 비교하고 싶은 핵심 지표는 무엇인가요? (복수 선택 가능 — 해당 문자를 모두 기입)

A) 월정액 (기본 요금)

B) 체감가 (프로모션 적용 후 실질 부담액)

C) 페이백/사은품 금액

D) 데이터 제공량 대비 가격 (GB당 단가)

X) Other (please describe after [Answer]: tag below)

[Answer]: A,B

---

## Question 8: Security Extensions
이 프로젝트에 보안 확장 규칙을 적용하시겠습니까?

A) Yes — 모든 SECURITY 규칙을 blocking constraint로 적용 (프로덕션 수준 애플리케이션에 권장)

B) No — SECURITY 규칙 건너뛰기 (PoC, 프로토타입, 실험적 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 9: Property-Based Testing Extension
이 프로젝트에 Property-Based Testing(PBT) 규칙을 적용하시겠습니까?

A) Yes — 모든 PBT 규칙을 blocking constraint로 적용 (비즈니스 로직, 데이터 변환, 직렬화, 상태 관리 컴포넌트가 있는 프로젝트에 권장)

B) Partial — 순수 함수와 직렬화 round-trip에만 PBT 규칙 적용 (알고리즘 복잡도가 제한적인 프로젝트에 적합)

C) No — PBT 규칙 건너뛰기 (단순 CRUD, UI 전용, 비즈니스 로직이 거의 없는 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 추천해줘

---
