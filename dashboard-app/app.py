"""통신 3사 USIM 요금제 프로모션 대시보드

인증 없이 URL로 즉시 접속 가능한 공개 대시보드입니다.
"""
import streamlit as st

st.set_page_config(
    page_title="USIM 요금제 프로모션 비교",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 사이드바: 수집 상태
from data.data_loader import load_metadata

st.sidebar.title("📱 USIM 프로모션 대시보드")
st.sidebar.markdown("---")

# 수집 상태 표시
metadata = load_metadata()
st.sidebar.subheader("📊 수집 상태")

if metadata and "last_crawl" in metadata:
    for carrier in ["SKT", "KT", "LG"]:
        info = metadata["last_crawl"].get(carrier, {})
        if info.get("success"):
            last_date = info.get("date", "N/A")
            plan_count = info.get("plan_count", 0)
            st.sidebar.success(f"✅ {carrier}: {last_date} ({plan_count}개)")
        elif info.get("date"):
            st.sidebar.warning(f"⚠️ {carrier}: 마지막 성공 {info.get('date', 'N/A')}")
        else:
            st.sidebar.error(f"❌ {carrier}: 수집 데이터 없음")
else:
    st.sidebar.warning("메타데이터를 불러올 수 없습니다.")

# 메인 페이지
st.title("📱 통신 3사 USIM 요금제 프로모션 비교")
st.markdown(
    """
    SKT, KT, LG U+의 USIM 단독 요금제 프로모션을 자동으로 수집하여 비교합니다.
    
    **페이지 안내:**
    - 📊 **비교 테이블** — 3사 요금제 현황을 한눈에 비교
    - 📈 **트렌드 차트** — 월정액/체감가 변화 추이 (최근 90일)
    
    👈 왼쪽 사이드바에서 페이지를 선택하세요.
    """
)
