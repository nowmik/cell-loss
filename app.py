import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Cell Growth Error Analyzer", layout="wide")

st.title("🔬 Cell Growth Analysis & Error Calculator")

# --- 1. 세포 정보 및 기본 설정 ---
st.header("1. 기본 정보 입력")
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    cell_name = st.text_input("분석할 세포 명칭", value="HeLa")
with col_info2:
    doubling_time = st.number_input(f"{cell_name}의 Doubling Time (hours)", value=24.0)
with col_info3:
    st.write("초기 Seeding 수 ($A \\times 10^B$)")
    c_a, c_b = st.columns(2)
    with c_a:
        n0_coeff = st.number_input("계수(A)", value=2.5, step=0.1, key="n0_a")
    with c_b:
        n0_exp = st.number_input("지수(B)", value=4, step=1, key="n0_b")
    n0 = n0_coeff * (10 ** n0_exp)

st.divider()

# --- 2. 7일간의 데이터 입력 ---
st.header(f"2. {cell_name} 관측 데이터 입력 ($Value \\times 10^{{Power}}$)")

# 입력 편의를 위한 데이터프레임 구성
days = [f"Day {i}" for i in range(1, 8)]
input_data = {
    "Day": days,
    "Value (계수)": [0.0] * 7,
    "Power (지수)": [int(n0_exp)] * 7 # 기본적으로 초기 seeding 지수와 맞춰둠
}
df_input = pd.DataFrame(input_data)

# 데이터 에디터
edited_df = st.data_editor(df_input, use_container_width=True, num_rows="fixed")

if st.button(f"{cell_name} 데이터 분석 시작"):
    # 실제 값 계산
    observed_counts = edited_df["Value (계수)"].values * (10 ** edited_df["Power (지수)"].values)
    
    # 이론적 수치 계산
    day_indices = np.arange(1, 8)
    theoretical_counts = n0 * (2 ** ((day_indices * 24) / doubling_time))
    
    # 오차 계산
    valid_mask = observed_counts > 0
    if not any(valid_mask):
        st.error("입력된 데이터가 없습니다. 값을 입력해주세요.")
    else:
        errors = np.abs(theoretical_counts[valid_mask] - observed_counts[valid_mask]) / theoretical_counts[valid_mask] * 100
        avg_error = np.mean(errors)
        
        # --- 3. 그래프 시각화 ---
        fig = go.Figure()
        
        # 이론적 성장 곡선
        fig.add_trace(go.Scatter(
            x=days, y=theoretical_counts, name='Theoretical Growth',
            line=dict(color='gray', dash='dash'), opacity=0.5
        ))
        
        # 실제 관측 곡선
        fig.add_trace(go.Scatter(
            x=days, y=observed_counts, name=f'Observed ({cell_name})',
            mode='lines+markers', line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))

        fig.update_layout(
            title=f"{cell_name} Growth Curve Analysis",
            xaxis_title="Timeline",
            yaxis_title="Cell Number (Log Scale)",
            yaxis_type="log",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- 4. 결과 리포트 ---
        st.success(f"### 📋 {cell_name} 실험 숙련도 리포트")
        res1, res2, res3 = st.columns(3)
        res1.metric("평균 오차율", f"{avg_error:.2f}%")
        res2.metric("보정 계수", f"{(1 + avg_error/100):.22f}x")
        res3.metric("최종 권장 Seeding", f"{(n0 * (1 + avg_error/100)):.2e}")
        
        st.info(f"💡 {cell_name} 실험 시, 평소 본인의 숙련도를 고려하여 목표 수치보다 약 **{avg_error:.1f}%** 더 분주하는 것을 권장합니다.")
