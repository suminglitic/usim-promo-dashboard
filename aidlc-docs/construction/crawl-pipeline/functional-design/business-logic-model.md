# Business Logic Model — crawl-pipeline

## 전체 워크플로우

```
EventBridge Trigger (KST 10:00)
        |
        v
+-------------------+
| Lambda Handler    |
| (Orchestration)   |
+-------------------+
        |
        v
+-------------------+     +-------------------+     +-------------------+
| SKT Crawler       |     | KT Crawler        |     | LG Crawler        |
| (독립 실행)        |     | (독립 실행)        |     | (독립 실행)        |
+-------------------+     +-------------------+     +-------------------+
        |                         |                         |
        v                         v                         v
+-------------------+     +-------------------+     +-------------------+
| Validate Result   |     | Validate Result   |     | Validate Result   |
+-------------------+     +-------------------+     +-------------------+
        |                         |                         |
        v                         v                         v
+-------------------+     +-------------------+     +-------------------+
| Process Data      |     | Process Data      |     | Process Data      |
+-------------------+     +-------------------+     +-------------------+
        |                         |                         |
        +------------+------------+------------+------------+
                     |
                     v
            +-------------------+
            | Store to S3       |
            | (성공한 것만)      |
            +-------------------+
                     |
                     v
            +-------------------+
            | Return Result     |
            | (성공/실패 요약)   |
            +-------------------+
```

## Logic 1: Lambda Handler (Orchestration)

```python
def handler(event, context):
    """메인 오케스트레이션 로직"""
    execution_date = date.today().isoformat()
    carriers = ["SKT", "KT", "LG"]
    results = {}
    all_processed = []
    
    for carrier in carriers:
        try:
            # 1. 크롤링
            raw_data = crawl(carrier)
            
            # 2. 검증
            if not validate_result(raw_data):
                results[carrier] = CrawlResult(
                    carrier=carrier, success=False,
                    error_message="Validation failed: no valid plans extracted"
                )
                continue
            
            # 3. 전처리
            processed = process(raw_data)
            all_processed.extend(processed)
            
            results[carrier] = CrawlResult(
                carrier=carrier, success=True, plans=raw_data
            )
            
        except Exception as e:
            results[carrier] = CrawlResult(
                carrier=carrier, success=False, error_message=str(e)
            )
            # 다른 통신사는 계속 진행
            continue
    
    # 4. 성공한 데이터만 S3 적재
    if all_processed:
        store(all_processed, execution_date)
    
    return PipelineResult(
        execution_date=execution_date,
        results=results,
        total_plans_stored=len(all_processed),
        failed_carriers=[c for c, r in results.items() if not r.success]
    )
```

## Logic 2: Crawl Strategy (Fallback Pattern)

```python
def crawl(carrier: str) -> list[RawPlanData]:
    """통신사별 크롤링 (BS4 우선, Selenium fallback)"""
    url = get_url(carrier)
    
    # Phase 1: 정적 파싱 시도
    try:
        html = fetch_static(url, timeout=30)
        plans = parse(carrier, html)
        if plans:
            return plans
    except Exception:
        pass  # fallback으로 진행
    
    # Phase 2: Selenium 동적 렌더링
    html = fetch_dynamic(url, timeout=30)
    plans = parse(carrier, html)
    if plans:
        return plans
    
    raise CrawlFailureError(f"{carrier} crawling failed: no data extracted")
```

## Logic 3: Data Processing

```python
def process(raw_data: list[RawPlanData]) -> list[ProcessedPlanData]:
    """원시 데이터 → 정제 데이터 변환"""
    processed = []
    for raw in raw_data:
        monthly_fee = clean_currency(raw.monthly_fee_text)
        total_benefit, monthly_benefit, duration = parse_benefit(
            raw.benefit_text, raw.benefit_condition
        )
        perceived_price = monthly_fee - monthly_benefit
        
        processed.append(ProcessedPlanData(
            carrier=raw.carrier,
            plan_name=normalize_plan_name(raw.plan_name),
            monthly_fee=monthly_fee,
            perceived_price=max(0, perceived_price),  # 음수 방지
            total_benefit=total_benefit,
            monthly_benefit=monthly_benefit,
            benefit_duration=duration,
            benefit_detail=raw.benefit_text,
            collected_date=date.today().isoformat(),
            crawled_at=raw.crawled_at.isoformat()
        ))
    return processed
```

## Logic 4: Currency Parsing

```python
def clean_currency(text: str) -> int:
    """한국어 통화 표현 → 정수 변환"""
    text = text.strip().replace("₩", "").replace("원", "").replace(",", "").replace(" ", "")
    
    # "6만9천" 패턴
    man_match = re.search(r'(\d+)만', text)
    cheon_match = re.search(r'(\d+)천', text)
    
    result = 0
    if man_match:
        result += int(man_match.group(1)) * 10000
    if cheon_match:
        result += int(cheon_match.group(1)) * 1000
    
    # 순수 숫자 패턴 (콤마 제거 후)
    if not man_match and not cheon_match:
        digits = re.sub(r'[^\d]', '', text)
        if digits:
            result = int(digits)
    
    return result
```

## Logic 5: LG U+ Benefit Tier Parsing

```python
def parse_lg_benefits(html_text: str) -> list[dict]:
    """LG U+ 주문서 페이지의 혜택 티어 파싱"""
    tiers = []
    # ①②③④⑤ 번호로 분리
    pattern = r'[①②③④⑤⑥⑦⑧⑨⑩](.+?)(?=[①②③④⑤⑥⑦⑧⑨⑩]|$)'
    matches = re.findall(pattern, html_text, re.DOTALL)
    
    for match in matches:
        # 혜택 금액 추출
        benefit_amount = extract_currency(match)  # "28만8천원" → 288000
        
        # 요금제명 추출
        plan_names = extract_plan_names(match)  # ["너겟 69"]
        
        # 월 지급 조건 추출 "2만4천원x12개월"
        monthly, duration = extract_payment_schedule(match)
        
        tiers.append({
            "total_benefit": benefit_amount,
            "plans": plan_names,
            "monthly_amount": monthly,
            "duration_months": duration
        })
    
    return tiers
```

## Logic 6: CSV Storage (GitHub Repo)

```python
def store(data: list[ProcessedPlanData], execution_date: str) -> str:
    """GitHub repo의 data/ 폴더에 CSV로 저장"""
    df = pd.DataFrame([asdict(d) for d in data])
    
    # latest.csv 덮어쓰기
    latest_path = os.path.join(DATA_DIR, "latest.csv")
    df.to_csv(latest_path, index=False, encoding='utf-8-sig')
    
    # history/{date}.csv 추가
    history_path = os.path.join(DATA_DIR, "history", f"{execution_date}.csv")
    df.to_csv(history_path, index=False, encoding='utf-8-sig')
    
    # 90일 초과 파일 삭제
    cleanup_expired(retention_days=90)
    
    # metadata.json 업데이트
    update_metadata(data, execution_date)
    
    return history_path
```
