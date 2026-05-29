"""3사 요금제 비교 테이블 페이지"""
import streamlit as st
import pandas as pd

from data.data_loader import load_latest_data

st.set_page_config(page_title="비교 테이블", page_icon="📊", layout="wide")
st.title("📊 3사 요금제 비교 테이블")
st.markdown("SKT, KT, LG U+의 USIM 단독 요금제를 한눈에 비교합니다.")

# 데이터 로드
df = load_latest_data()

if df.empty:
    st.warning("⚠️ 수집된 데이터가 없습니다. 크롤링이 아직 실행되지 않았을 수 있습니다.")
    st.stop()

# 필터 옵션
st.sidebar.subheader("🔍 필터")
carriers = df["carrier"].unique().tolist()
selected_carriers = st.sidebar.multiselect(
    "통신사 선택", carriers, default=carriers
)

# 필터 적용
filtered_df = df[df["carrier"].isin(selected_carriers)].copy()

if filtered_df.empty:
    st.info("선택한 조건에 맞는 데이터가 없습니다.")
    st.stop()

# 표시용 DataFrame 생성
display_df = filtered_df[[
    "carrier", "plan_name", "monthly_fee", "perceived_price",
    "total_benefit", "benefit_detail", "collected_date"
]].copy()

display_df.columns = ["통신사", "요금제명", "월정액", "체감가", "총 혜택", "혜택 상세", "수집일"]

# 통신사 정렬 (SKT → KT → LG)
carrier_order = {"SKT": 0, "KT": 1, "LG": 2}
display_df["_sort"] = display_df["통신사"].map(carrier_order)
display_df = display_df.sort_values(["_sort", "월정액"]).drop("_sort", axis=1)

# 금액 포맷팅
def format_won(val):
    """금액을 천 단위 콤마 + 원으로 포맷"""
    if pd.isna(val) or val == 0:
        return "-"
    return f"{int(val):,}원"

# 요약 지표
col1, col2, col3 = st.columns(3)
with col1:
    avg_fee = filtered_df["monthly_fee"].mean()
    st.metric("평균 월정액", format_won(avg_fee))
with col2:
    avg_perceived = filtered_df["perceived_price"].mean()
    st.metric("평균 체감가", format_won(avg_perceived))
with col3:
    avg_benefit = filtered_df["total_benefit"].mean()
    st.metric("평균 총 혜택", format_won(avg_benefit))

st.markdown("---")

# 테이블 표시
st.dataframe(
    display_df.style.format({
        "월정액": lambda x: format_won(x),
        "체감가": lambda x: format_won(x),
        "총 혜택": lambda x: format_won(x),
    }),
    use_container_width=True,
    hide_index=True,
    height=600,
)

# 수집일 정보
if "수집일" in display_df.columns:
    latest_date = display_df["수집일"].max()
    st.caption(f"📅 최종 수집일: {latest_date}")
