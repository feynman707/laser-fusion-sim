import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="레이저 핵융합 시뮬레이션", layout="centered")

st.title("레이저 핵융합 3D 시뮬레이션")

# 사용자 입력 UI
laser_power = st.slider("레이저 세기 (단위: 10^15 W/cm²)", 1.0, 10.0, 5.0, 0.1)
initial_temp = st.slider("초기 플라즈마 온도 (단위: keV)", 0.1, 10.0, 1.0, 0.1)
density = st.slider("플라즈마 밀도 (단위: 10^21 cm⁻³)", 1.0, 10.0, 5.0, 0.1)
simulation_time = st.slider("시뮬레이션 시간 (단위: ns)", 1, 20, 10, 1)

st.write("---")

# 간단 온도 변화 모델 (임의 공식)
# dT/dt = a * laser_power * density - b * T**2 (냉각 효과 포함)
a = 0.05
b = 0.01

dt = 0.1
steps = int(simulation_time / dt)
temps = np.zeros(steps)
temps[0] = initial_temp

for i in range(1, steps):
    dT = a * laser_power * density - b * temps[i-1]**2
    temps[i] = temps[i-1] + dT * dt
    if temps[i] < 0:
        temps[i] = 0

time_axis = np.linspace(0, simulation_time, steps)

# 임계 온도 (융합 시작 기준)
critical_temp = 5.0

# 성공/실패 판정
fusion_success = np.any(temps >= critical_temp)

if fusion_success:
    st.success("🎉 융합 성공! 플라즈마 온도가 임계점을 넘었습니다.")
else:
    st.error("⚠️ 융합 실패. 임계 온도에 도달하지 못했습니다.")

# 온도 변화 그래프
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_axis, y=temps, mode='lines+markers', name='온도 (keV)'))
fig.add_hline(y=critical_temp, line_dash="dash", line_color="red",
              annotation_text="임계 온도", annotation_position="top right")
fig.update_layout(title="플라즈마 온도 변화", xaxis_title="시간 (ns)", yaxis_title="온도 (keV)")

st.plotly_chart(fig, use_container_width=True)

# 3D 구체 색상 변화 (온도에 따른 색상 매핑)
def temp_to_color(temp):
    # 0 ~ 10 keV 범위, 파란색(차가움)~빨간색(뜨거움)으로 매핑
    r = min(max((temp - 0) / 10, 0), 1)
    b = 1 - r
    g = 0.2
    return f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})'

latest_temp = temps[-1]
color = temp_to_color(latest_temp)

sphere = go.Figure(data=[go.Mesh3d(
    x=[0,0,1,1,0,0,1,1],
    y=[0,1,0,1,0,1,0,1],
    z=[0,0,0,0,1,1,1,1],
    color=color,
    opacity=0.7,
    alphahull=5
)])

sphere.update_layout(
    title="플라즈마 구체 시각화",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data'),
    margin=dict(l=0, r=0, b=0, t=30)
)

st.plotly_chart(sphere, use_container_width=True)
