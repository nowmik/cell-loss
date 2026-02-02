import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="Cell Culture Error Analyzer", layout="wide")

st.title("🔬 Cell Culture Personal Error Analyzer")
st.markdown("""
이 프로그램은 일주일간의 Cell 성장 데이터를 바탕으로 **개인의 실험적 오차(Suction, Seeding 등)**를 계산합니다.
이를 통해 향후 실험에서 필요한 **Over-seeding** 양을 예측할 수 있습니다.
""")

# 사이드바: 기본 파라미터 입력
st.sidebar.header("Configuration")
n0 = st.sidebar.number_input("초기 Seeding 세포 수", value=100000, step=10000)
doubling_time = st.sidebar.number_input("Doubling Time (Hours)", value=24.0, step=1.0)
target_confluency = st.sidebar.slider("목표 Confluency (%)", 0, 100, 80)

# 메인 화면: 데이터 입력 테이블
st.subheader("🗓 7-Day Observation Data")
data = {
    "Day": [f"Day {i}" for i in range(1, 8)],
    "Observed Count": [0.0] * 7
}
df_input = pd.DataFrame(data)

# 사용자로부터 직접 입력받는 데이터 에디터
edited_df = st.data_editor(df_input, num_rows="fixed", use_container_width=True)

if st.button("Calculate Statistical Error"):
    # 이론적 수치 계산
    days = np.arange(1, 8)
    time_hours = days * 24
    theoretical_counts = n0 * (2 ** (time_hours / doubling_time))
    observed_counts = edited_df["Observed Count"].values

    # 통계 계산
    errors = np.abs(theoretical_counts - observed_counts) / theoretical_counts * 100
    avg_error = np.mean(errors)
    std_dev = np.std(errors)
    
    # 보정 계수 (Safety Factor)
    safety_factor = 1 + (avg_error + std_dev) / 100

    # 결과 대시보드 출력
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 오차율", f"{avg_error:.2f}%")
    col2.metric("오차 표준편차", f"{std_dev:.2f}%")
    col3.metric("추천 Seeding 배수", f"{safety_factor:.2f}x")

    # 시각화 (Plotly 사용 - 웹 인터랙티브 그래프)
    fig = go.Figure()
    
    # 이론적 성장 곡선
    fig.add_trace(go.Scatter(x=days, y=theoretical_counts, name='이론적 성장(Ideal)', line=dict(color='green', dash='dash')))
    
    # 실제 관측 데이터
    fig.add_trace(go.Scatter(x=days, y=observed_counts, name='실제 관측(Observed)', mode='lines+markers', line=dict(color='red')))
    
    # 오차 범위 표시 (Error Band)
    fig.add_trace(go.Scatter(
        x=np.concatenate([days, days[::-1]]),
        y=np.concatenate([theoretical_counts * (1 + avg_error/100), (theoretical_counts * (1 - avg_error/100))[::-1]]),
        fill='toself', fillcolor='rgba(128,128,128,0.2)', line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", showlegend=True, name="평균 오차 범위"
    ))

    fig.update_layout(title="Growth Curve: Theoretical vs Observed", xaxis_title="Days", yaxis_title="Cell Number")
    st.plotly_chart(fig, use_container_width=True)

    # 제언 섹션
    st.info(f"""
    **💡 실험 가이드:**
    - 현재 본인의 핸들링 습관상 약 **{avg_error:.1f}%**의 세포 소실이 발생하고 있습니다.
    - 다음 실험에서 목표하는 세포 수를 얻으려면 초기 분주 시 **{int(n0 * safety_factor):,} cells**를 깔아야 합니다.
    - 오차 표준편차({std_dev:.2f}%)가 크다면, 특정 날짜의 pipetting 강도가 일정하지 않았음을 의미합니다.
    """)
