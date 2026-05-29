"""요금제 트렌드 차트 페이지"""
import streamlit as st
import pandas as pd
import plotly.express as px

from data.data_loader import load_trend_data

st.set_page_config(page_title="트렌드 차트", page_icon="📈", layout="wide")
st.title("📈 요금제 트렌드 차트")
st.markdown("주요 요금제의 월정액/체감가 변화 추이를 확인합니다. (최근 90일)")

# 데이터 로드
df = load_trend_data(days=90)

if df.empty:
    st.warning("⚠️ 트렌드 데이터가 없습니다. 최소 2일 이상의 수집 데이터가 필요합니다.")
    st.stop()

# 날짜 컬럼 변환
if "collected_date" in df.columns:
    df["collected_date"] = pd.to_datetime(df["collected_date"])

# 필터 옵션
st.sidebar.subheader("🔍 필터")

# 지표 선택
metric = st.sidebar.selectbox(
    "지표 선택",
    ["체감가", "월정액"],
    index=0,
)
metric_col = "perceived_price" if metric == "체감가" else "monthly_fee"

# 통신사 필터
carriers = df["carrier"].unique().tolist()
selected_carriers = st.sidebar.multiselect(
    "통신사 선택", carriers, default=carriers
)

# 요금제 필터
available_plans = df[df["carrier"].isin(selected_carriers)]["plan_name"].unique().tolist()
default_plans = available_plans[:8] if len(available_plans) > 8 else available_plans
selected_plans = st.sidebar.multiselect(
    "요금제 선택", available_plans, default=default_plans
)

# 필터 적용
filtered = df[
    (df["carrier"].isin(selected_carriers)) &
    (df["plan_name"].isin(selected_plans))
].copy()

if filtered.empty:
    st.info("선택한 조건에 맞는 데이터가 없습니다.")
    st.stop()

# 라벨 생성 (통신사 + 요금제명)
filtered["label"] = filtered["carrier"] + " " + filtered["plan_name"]

# Plotly 라인 차트
fig = px.line(
    filtered,
    x="collected_date",
    y=metric_col,
    color="label",
    title=f"{metric} 변화 추이 (최근 90일)",
    labels={
        metric_col: f"{metric} (원)",
        "collected_date": "날짜",
        "label": "요금제",
    },
    markers=True,
)

fig.update_layout(
    xaxis_title="날짜",
    yaxis_title=f"{metric} (원)",
    legend_title="요금제",
    hovermode="x unified",
    height=500,
)

fig.update_yaxis(tickformat=",")

st.plotly_chart(fig, use_container_width=True)

# 변동 요약
st.markdown("---")
st.subheader("📋 변동 요약")

if len(filtered["collected_date"].unique()) >= 2:
    # 최신 vs 이전 비교
    latest_date = filtered["collected_date"].max()
    prev_dates = filtered[filtered["collected_date"] < latest_date]["collected_date"]

    if not prev_dates.empty:
        prev_date = prev_dates.max()
        latest_data = filtered[filtered["collected_date"] == latest_date]
        prev_data = filtered[filtered["collected_date"] == prev_date]

        comparison = latest_data.merge(
            prev_data[["label", metric_col]],
            on="label",
            suffixes=("_now", "_prev"),
        )

        if not comparison.empty:
            comparison["변동"] = comparison[f"{metric_col}_now"] - comparison[f"{metric_col}_prev"]
            comparison["변동률"] = (comparison["변동"] / comparison[f"{metric_col}_prev"] * 100).round(1)

            changes = comparison[comparison["변동"] != 0][["label", f"{metric_col}_now", "변동", "변동률"]]
            if not changes.empty:
                changes.columns = ["요금제", f"현재 {metric}", "변동 (원)", "변동률 (%)"]
                st.dataframe(changes, use_container_width=True, hide_index=True)
            else:
                st.info(f"최근 변동 없음 ({prev_date.strftime('%Y-%m-%d')} → {latest_date.strftime('%Y-%m-%d')})")
else:
    st.info("변동 비교를 위해 최소 2일 이상의 데이터가 필요합니다.")
