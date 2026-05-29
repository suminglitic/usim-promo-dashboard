# Business Logic Model — dashboard-app

## 페이지 구조

```
app.py (메인)
├── 사이드바: 수집 상태 표시
├── Page 1: 3사 비교 테이블
└── Page 2: 트렌드 차트
```

## Logic 1: 데이터 로딩 (캐시 적용)

```python
@st.cache_data(ttl=3600)  # 1시간 캐시
def load_latest_data() -> pd.DataFrame:
    """S3에서 최신 수집 데이터 로드"""
    # 가장 최근 날짜의 parquet 파일 찾기
    today = date.today()
    for days_back in range(7):  # 최대 7일 전까지 탐색
        target_date = today - timedelta(days=days_back)
        s3_key = f"data/year={target_date.year}/month={target_date.month:02d}/day={target_date.day:02d}/plans.parquet"
        try:
            df = read_parquet_from_s3(s3_key)
            return df
        except FileNotFoundError:
            continue
    return pd.DataFrame()  # 데이터 없음


@st.cache_data(ttl=3600)
def load_trend_data(days: int = 90) -> pd.DataFrame:
    """최근 N일간의 트렌드 데이터 로드"""
    all_data = []
    today = date.today()
    for days_back in range(days):
        target_date = today - timedelta(days=days_back)
        s3_key = f"data/year={target_date.year}/month={target_date.month:02d}/day={target_date.day:02d}/plans.parquet"
        try:
            df = read_parquet_from_s3(s3_key)
            all_data.append(df)
        except FileNotFoundError:
            continue
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()
```

## Logic 2: 비교 테이블 렌더링

```python
def render_comparison_table():
    """3사 요금제 비교 테이블"""
    df = load_latest_data()
    
    if df.empty:
        st.warning("수집된 데이터가 없습니다.")
        return
    
    # 컬럼 정리 및 포맷팅
    display_df = df[["carrier", "plan_name", "monthly_fee", 
                     "perceived_price", "total_benefit", "benefit_detail",
                     "collected_date"]].copy()
    
    display_df.columns = ["통신사", "요금제명", "월정액", "체감가", 
                          "총 혜택", "혜택 상세", "수집일"]
    
    # 금액 포맷팅 (천 단위 콤마)
    for col in ["월정액", "체감가", "총 혜택"]:
        display_df[col] = display_df[col].apply(lambda x: f"{x:,}원")
    
    # 통신사별 정렬
    carrier_order = {"SKT": 0, "KT": 1, "LG": 2}
    display_df["sort_key"] = display_df["통신사"].map(carrier_order)
    display_df = display_df.sort_values(["sort_key", "월정액"]).drop("sort_key", axis=1)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
```

## Logic 3: 트렌드 차트 렌더링

```python
def render_trend_chart():
    """시계열 트렌드 차트"""
    df = load_trend_data(days=90)
    
    if df.empty:
        st.warning("트렌드 데이터가 없습니다.")
        return
    
    # 지표 선택
    metric = st.selectbox("지표 선택", ["월정액", "체감가"], index=1)
    metric_col = "monthly_fee" if metric == "월정액" else "perceived_price"
    
    # 요금제 필터 (주요 요금제만)
    available_plans = df["plan_name"].unique().tolist()
    selected_plans = st.multiselect("요금제 선택", available_plans, default=available_plans[:5])
    
    filtered = df[df["plan_name"].isin(selected_plans)]
    
    # Plotly 라인 차트
    fig = px.line(
        filtered,
        x="collected_date",
        y=metric_col,
        color="plan_name",
        line_group="carrier",
        title=f"{metric} 변화 추이 (최근 90일)",
        labels={metric_col: f"{metric} (원)", "collected_date": "날짜", "plan_name": "요금제"}
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

## Logic 4: 수집 상태 표시

```python
def show_collection_status():
    """사이드바에 수집 상태 표시"""
    df = load_latest_data()
    
    if df.empty:
        st.sidebar.error("데이터 없음")
        return
    
    st.sidebar.subheader("📊 수집 상태")
    
    for carrier in ["SKT", "KT", "LG"]:
        carrier_data = df[df["carrier"] == carrier]
        if carrier_data.empty:
            st.sidebar.warning(f"⚠️ {carrier}: 수집 실패")
        else:
            last_date = carrier_data["collected_date"].max()
            plan_count = len(carrier_data)
            days_old = (date.today() - date.fromisoformat(last_date)).days
            
            if days_old > 1:
                st.sidebar.warning(f"⚠️ {carrier}: {last_date} ({days_old}일 전, {plan_count}개)")
            else:
                st.sidebar.success(f"✅ {carrier}: {last_date} ({plan_count}개)")
```
