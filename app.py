import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Cell Error Visualizer", layout="centered")

st.title("🔬 Cell Growth & Error Visualizer")
st.markdown("지수 표기법(예: `1.5e5`)으로 데이터를 입력하여 실제 성장 곡선과 오차를 비교하세요.")

# --- 사이드바 설정 ---
st.sidebar.header("🧫 실험 조건 설정")
# format="%.1e" 를 사용해 지수 표기법 입력 가능하게 설정
n0 = st.sidebar.number_input("초기 Seeding (n0)", value=1.0e5, format="%.1e")
doubling_time = st.sidebar.number_input("Doubling Time (hours)", value=24.0)

# --- 데이터 입력 섹션 ---
st.subheader("📊 7일간의 관측 데이터 입력")
st.info("입력 칸에 `2e5`라고 치고 Enter를 누르면 `200,000`으로 자동 입력됩니다.")

# 입력 테이블 구성
days = [f"Day {i}" for i in range(1, 8)]
default_values = [0.0] * 7
df_input = pd.DataFrame({"Day": days, "Observed_Count": default_values})

# 데이터 에디터 (지수 표기 적용)
edited_df = st.data_editor(
    df_input, 
    column_config={
        "Observed_Count": st.column_config.NumberColumn(
            "실제 관측 세포 수",
            format="%.2e"  # 화면에 지수 형태로 표시
        )
    },
    use_container_width=True,
    num_rows="fixed"
)

if st.button("성장 곡선 비교 및 오차 분석 실행"):
    # 1. 계산 로직
    day_indices = np.arange(1, 8)
    time_hours = day_indices * 24
    theoretical_counts = n0 * (2 ** (time_hours / doubling_time))
    observed_counts = edited_df["Observed_Count"].values

    # 오차 계산 (실제 데이터가 입력된 경우만)
    valid_mask = observed_counts > 0
    if not any(valid_mask):
        st.warning("데이터를 입력해주세요!")
    else:
        errors = np.abs(theoretical_counts[valid_mask] - observed_counts[valid_mask]) / theoretical_counts[valid_mask] * 100
        avg_error = np.mean(errors)
        
        # 2. 그래프 시각화 (Plotly)
        fig = go.Figure()
        
        # 이론적 성장 곡선
        fig.add_trace(go.Scatter(
            x=days, y=theoretical_counts, 
            mode='lines', name='이론적 성장 (Ideal)',
            line=dict(color='#2ecc71', width=3, dash='dash')
        ))
        
        # 실제 관측 데이터
        fig.add_trace(go.Scatter(
            x=days, y=observed_counts, 
            mode='lines+markers', name='실제 관측 (Observed)',
            marker=dict(size=10, color='#e74c3c'),
            line=dict(color='#e74c3c', width=3)
        ))

        fig.update_layout(
            title="Cell Growth Curve: Ideal vs Observed",
            xaxis_title="Time (Days)",
            yaxis_title="Cell Number (log scale)",
            yaxis_type="log", # 세포 수는 기하급수적으로 늘어나므로 log scale이 보기 편함
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 3. 분석 결과 리포트
        st.success(f"### 📈 분석 결과")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("평균 손실/오차율", f"{avg_error:.2f}%")
        with c2:
            safety_factor = 1 + (avg_error/100)
            st.metric("추천 Seeding 보정 계수", f"{safety_factor:.2f}x")
        
        st.write(f"👉 다음 실험 시 목표량보다 **{avg_error:.1f}%** 더 깔아야 목표 Confluency에 도달할 수 있습니다.")

