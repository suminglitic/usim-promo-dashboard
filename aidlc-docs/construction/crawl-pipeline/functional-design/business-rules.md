# Business Rules — crawl-pipeline

## BR-01: 크롤링 전략 (Fallback Pattern)

**규칙**: 각 통신사 크롤링은 정적 파싱을 먼저 시도하고, 실패 시 동적 렌더링으로 전환한다.

```
IF BeautifulSoup 파싱으로 데이터 추출 성공:
    RETURN 추출된 데이터
ELSE:
    Selenium 헤드리스 브라우저로 페이지 렌더링
    IF 렌더링 후 데이터 추출 성공:
        RETURN 추출된 데이터
    ELSE:
        RAISE CrawlFailureError
```

## BR-02: 크롤링 결과 검증

**규칙**: 크롤링 결과가 유효하려면 최소 1개 이상의 요금제 데이터가 존재해야 한다.

```
IF len(extracted_plans) == 0:
    결과 무효 → 에러 발생, 해당 통신사 적재 중단
IF any plan has empty plan_name OR empty monthly_fee_text:
    해당 plan 제외 (부분 데이터 허용하지 않음)
IF len(valid_plans) == 0:
    결과 무효 → 에러 발생
```

## BR-03: 통신사별 독립 실행

**규칙**: 각 통신사 크롤링은 독립적으로 실행되며, 1사 실패가 다른 2사에 영향을 주지 않는다.

```
FOR each carrier IN [SKT, KT, LG]:
    TRY:
        result = crawl(carrier)
        IF validate(result):
            processed = process(result)
            store(processed)
    EXCEPT CrawlFailureError:
        log_error(carrier, error)
        CONTINUE (다음 통신사 진행)
```

## BR-04: 빈 데이터 적재 방지

**규칙**: 크롤링 실패 또는 검증 실패 시 빈 데이터를 S3에 절대 적재하지 않는다.

```
IF NOT validate_result(crawl_data):
    DO NOT store any data for this carrier
    RAISE error and log failure
    Previous day's data remains as latest
```

## BR-05: 통화 텍스트 변환

**규칙**: 한국어 통화 표현을 정수(원 단위)로 변환한다.

```
변환 규칙:
- "6만9천원" → 69000
- "69,000원" → 69000
- "₩69,000" → 69000
- "2만4천원" → 24000
- "28만8천원" → 288000
- "5천원" → 5000

패턴: 
- X만Y천원 → X*10000 + Y*1000
- X만원 → X*10000
- X천원 → X*1000
- 숫자,숫자원 → 숫자 (콤마 제거)
```

## BR-06: 체감가 계산

**규칙**: 체감가 = 월정액 - 월 환산 혜택 금액

```
monthly_benefit = total_benefit / benefit_duration_months
perceived_price = monthly_fee - monthly_benefit

예시:
- 너겟 69: 월정액 69,000 - (288,000 / 12) = 69,000 - 24,000 = 45,000원
- 너겟 47: 월정액 47,000 - (240,000 / 12) = 47,000 - 20,000 = 27,000원
- 너겟 45: 월정액 45,000 - (75,000 / 15) = 45,000 - 5,000 = 40,000원
```

## BR-07: 요금제명 정규화

**규칙**: 요금제명에서 불필요한 공백, 특수문자를 제거하고 통일된 형식으로 변환한다.

```
정규화 규칙:
1. 앞뒤 공백 제거 (strip)
2. 연속 공백을 단일 공백으로 변환
3. 전각 문자를 반각으로 변환
4. 괄호 내 부가 설명 보존 (예: "(액션캠) 너겟 69" → "너겟 69 (액션캠)")
5. 통신사 접두사 제거 (예: "LG U+ 너겟 47" → "너겟 47")
```

## BR-08: 데이터 저장 규칙

**규칙**: 데이터는 GitHub repo의 data/ 폴더에 CSV로 저장한다.

```
저장 경로:
- data/latest.csv (최신 데이터, 매번 덮어쓰기)
- data/history/{YYYY-MM-DD}.csv (일별 스냅샷, append)
- data/metadata.json (수집 상태 메타데이터)
```

## BR-09: 데이터 보존 정책

**규칙**: 90일 초과 CSV 파일은 크롤링 시 자동 삭제한다.

```
history/ 폴더 내 파일 중:
- 파일명에서 날짜 추출
- (today - file_date).days > 90 이면 삭제
- 삭제 후 git add/commit에 포함
```

## BR-10: LG U+ 혜택 티어 파싱

**규칙**: LG U+ 주문서 페이지의 번호 매김(①②③④⑤) 텍스트에서 혜택 정보를 추출한다.

```
파싱 패턴:
- "①네이버페이 등 너겟쿠폰 {금액} 혜택 요금제 : {요금제명} ({월금액}x{개월}개월)"
- 각 번호(①~⑤)가 하나의 혜택 티어를 나타냄
- 하나의 티어에 복수 요금제가 포함될 수 있음 (콤마/슬래시 구분)

추출 결과:
- total_benefit: 총 혜택 금액
- applicable_plans: 적용 대상 요금제 리스트
- monthly_amount: 월 지급 금액
- duration_months: 지급 기간 (개월)
```

## BR-11: KT 요고 혜택 파싱

**규칙**: KT 요고 페이지에서 페이백 및 OTT 혜택 정보를 추출한다.

```
추출 대상:
- 카카오페이/네이버페이 페이백 금액
- 초이스/플러스 OTT 혜택 (금액 환산)
- 월별 쿠폰팩 할인 금액

체감가 계산 시:
- 페이백 금액을 월 환산하여 차감
- OTT 혜택은 월 구독료 기준으로 환산
```

## BR-12: 타임아웃 처리

**규칙**: 크롤링 요청은 30초 타임아웃을 적용한다.

```
HTTP 요청 타임아웃: 30초
Selenium 페이지 로드 타임아웃: 30초
전체 Lambda 실행 타임아웃: 10분 (3사 순차 실행 고려)

타임아웃 발생 시:
- 해당 통신사 크롤링 실패 처리
- 다른 통신사는 계속 진행
```
