# Unit of Work — Story Mapping

## Story-to-Unit Assignment

| Story ID | Story Title | Unit | Priority |
|----------|-------------|------|----------|
| US-01 | SKT 요금제 크롤링 | crawl-pipeline | Must |
| US-02 | KT 요고 요금제 크롤링 | crawl-pipeline | Must |
| US-03 | LG U+ 너겟 요금제 크롤링 | crawl-pipeline | Must |
| US-04 | 배치 스케줄링 | crawl-pipeline | Must |
| US-05 | 데이터 전처리 | crawl-pipeline | Must |
| US-06 | 데이터 적재 | crawl-pipeline | Must |
| US-07 | 3사 요금제 비교 테이블 | dashboard-app | Must |
| US-08 | 요금제 트렌드 차트 | dashboard-app | Must |
| US-09 | 데이터 수집 상태 표시 | dashboard-app | Should |
| US-10 | 크롤링 실패 시 안전 중단 | crawl-pipeline | Must |
| US-11 | 부분 실패 시 기존 데이터 유지 | crawl-pipeline + dashboard-app | Should |

## Unit별 Story 요약

### crawl-pipeline (7 stories)
| Priority | Count | Stories |
|----------|-------|---------|
| Must | 6 | US-01, US-02, US-03, US-04, US-05, US-06, US-10 |
| Should | 1 | US-11 (부분) |

### dashboard-app (4 stories)
| Priority | Count | Stories |
|----------|-------|---------|
| Must | 2 | US-07, US-08 |
| Should | 2 | US-09, US-11 (부분) |

## Cross-Unit Story: US-11

US-11 (부분 실패 시 기존 데이터 유지)은 두 단위에 걸쳐 있습니다:
- **crawl-pipeline 책임**: 실패한 통신사의 데이터를 적재하지 않되, 성공한 통신사 데이터는 정상 적재
- **dashboard-app 책임**: 실패한 통신사는 마지막 성공 데이터를 표시하며 경고 표시

## 구현 순서 권장

```
Phase 1: crawl-pipeline (Must stories)
  US-04 → US-01 → US-02 → US-03 → US-05 → US-06 → US-10

Phase 2: dashboard-app (Must stories)
  US-07 → US-08

Phase 3: Should stories (양쪽)
  US-09 → US-11
```
