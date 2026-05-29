# Requirements Clarification Questions

답변 감사합니다. 2개 항목에 대해 추가 안내와 선택이 필요합니다.

---

## Clarification 1: 대시보드 배포 환경 (Question 2)

각 옵션의 비교표입니다:

| 옵션 | 월 비용 (예상) | 장점 | 단점 | 적합 대상 |
|------|---------------|------|------|-----------|
| A) EC2/ECS | $15~50/월 | 안정적, 항상 접속 가능, 커스터마이징 자유 | 서버 관리 필요, 고정 비용 | 팀 내부 상시 사용 |
| B) Lambda + 정적 프론트 | $1~5/월 | 서버리스, 저비용, 확장성 | Streamlit 사용 불가(별도 프론트 개발 필요), 복잡도 증가 | 외부 공개, 대규모 |
| C) Streamlit Cloud | 무료 | 무료, 배포 간편, 유지보수 최소 | 성능 제한, 커스터마이징 한계, 외부 서비스 의존 | PoC, 소규모 팀 |
| D) Fargate | $10~30/월 | 컨테이너 기반, 서버 관리 불필요, 확장 용이 | EC2보다 비용 높을 수 있음, 설정 복잡 | 중규모 이상 |

**추천**: 내부 팀 5명 이하 사용(Q5 답변 기준)이고 Streamlit 프레임워크를 사용하시므로, **옵션 C (Streamlit Community Cloud)** 가 가장 적합합니다.
- 무료이며 배포가 간편합니다
- GitHub 연동으로 코드 푸시 시 자동 배포됩니다
- 5명 이하 동시 접속에 충분한 성능입니다
- 단, 회사 보안 정책상 외부 클라우드 사용이 불가하면 **옵션 A (EC2)** 를 권장합니다

### Clarification Question 1
위 비교를 참고하여 배포 환경을 선택해 주세요.

A) AWS EC2/ECS에 Streamlit 앱 직접 배포 (항상 실행 상태)

B) AWS Lambda + API Gateway + 정적 프론트엔드 (서버리스, Streamlit 미사용)

C) Streamlit Community Cloud (무료, 추천)

D) AWS Fargate 컨테이너로 배포

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Clarification 2: Property-Based Testing (Question 9)

**추천: C (No — PBT 규칙 건너뛰기)**

이유:
- 이 프로젝트의 핵심은 웹 크롤링 + 데이터 시각화이며, 복잡한 비즈니스 로직이나 데이터 변환 알고리즘이 적습니다
- 크롤링 결과는 외부 사이트 구조에 의존하므로 property-based testing보다 integration test/snapshot test가 더 효과적입니다
- 내부 팀 5명 이하 사용의 PoC 성격 프로젝트에 PBT는 과도한 오버헤드입니다

### Clarification Question 2
PBT 적용 여부를 확정해 주세요.

A) Yes — 모든 PBT 규칙 적용

B) Partial — 순수 함수에만 적용

C) No — PBT 건너뛰기 (추천)

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---
