# Business Rules — dashboard-app

## BR-01: 데이터 캐싱

**규칙**: S3 데이터 조회 결과는 1시간 동안 캐시한다.

```
캐시 TTL: 3600초 (1시간)
캐시 키: 함수 인자 기반 자동 생성 (Streamlit @st.cache_data)
캐시 무효화: TTL 만료 시 자동
```

## BR-02: 최신 데이터 탐색

**규칙**: 최신 데이터가 오늘 날짜에 없으면 최대 7일 전까지 역순 탐색한다.

```
FOR days_back IN range(0, 7):
    target_date = today - days_back
    IF parquet file exists at target_date:
        RETURN data
RETURN empty (데이터 없음 표시)
```

## BR-03: 수집 상태 경고

**규칙**: 마지막 수집일이 1일 이상 경과하면 경고를 표시한다.

```
IF (today - last_collected_date).days > 1:
    SHOW warning icon (⚠️) with days elapsed
ELSE:
    SHOW success icon (✅)
```

## BR-04: 금액 표시 형식

**규칙**: 모든 금액은 천 단위 콤마와 "원" 접미사로 표시한다.

```
69000 → "69,000원"
288000 → "288,000원"
45000 → "45,000원"
```

## BR-05: 테이블 정렬

**규칙**: 비교 테이블은 통신사(SKT→KT→LG) 순서로 1차 정렬, 월정액 오름차순으로 2차 정렬한다.

## BR-06: 트렌드 차트 기본값

**규칙**: 트렌드 차트의 기본 설정은 다음과 같다.
- 기본 지표: 체감가
- 기본 기간: 90일
- 기본 요금제: 상위 5개 (데이터 빈도 기준)

## BR-07: 인증 없는 접근

**규칙**: 대시보드는 별도 인증 없이 URL만으로 즉시 접속 가능해야 한다.
- Streamlit 앱에 authentication 설정 없음
- Public URL로 배포
