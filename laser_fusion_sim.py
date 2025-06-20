import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="레이저 핵융합 시뮬레이션 업그레이드", layout="centered", initial_sidebar_state="expanded")

st.title("레이저 핵융합 3D 시뮬레이션 (업그레이드)")

# 사용자 입력
laser_power = st.sidebar.slider("레이저 세기 (10^15 W/cm²)", 1.0, 10.0, 5.0, 0.1)
initial_temp = st.sidebar.slider("초기 플라즈마 온도 (keV)", 0.1, 10.0, 1.0, 0.1)
density = st.sidebar.slider("플라즈마 밀도 (10^21 cm⁻³)", 1.0, 10.0, 5.0, 0.1)
simulation_time = st.sidebar.slider("시뮬레이션 시간 (ns)", 1, 20, 10, 1)

st.sidebar.markdown("---")
st.sidebar.markdown("**Lawson Criterion 조건:**")
st.sidebar.markdown("`nτ > 10^{14} (s/cm^3)`")

# 시뮬레이션 파라미터
dt = 0.1
steps = int(simulation_time / dt)
temps = np.zeros(steps)
temps[0] = initial_temp

# 물리 상수 (임의 조정)
a = 0.05  # 레이저 가열 계수
b = 0.01  # 냉각 계수

# 시뮬레이션 - 온도 변화
for i in range(1, steps):
    dT = a * laser_power * density - b * temps[i - 1] ** 2
    temps[i] = max(temps[i - 1] + dT * dt, 0)

time_axis = np.linspace(0, simulation_time, steps)

# 에너지 유지 시간 τ 계산 (임의식, 온도, 밀도에 비례)
tau = (initial_temp * density) * 1e-9  # ns → s 변환

# Lawson Criterion 계산
n_tau = density * 1e21 * tau  # 단위 변환 후 nτ 계산

critical_n_tau = 1e14

fusion_success = n_tau > critical_n_tau

# 결과 메시지 및 요약 카드
if fusion_success:
    st.success(f"🎉 융합 성공! nτ = {n_tau:.2e} > {critical_n_tau:.2e}")
else:
    st.error(f"⚠️ 융합 실패. nτ = {n_tau:.2e} < {critical_n_tau:.2e}")

# 온도 변화 그래프
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_axis, y=temps, mode="lines+markers", name="온도 (keV)"))
fig.update_layout(
    title="플라즈마 온도 변화",
    xaxis_title="시간 (ns)",
    yaxis_title="온도 (keV)",
    yaxis_range=[0, max(10, np.max(temps) + 1)],
)

st.plotly_chart(fig, use_container_width=True)

# 3D 구체 색상 변화 및 에너지 방출 애니메이션
def temp_to_color(temp):
    r = min(max((temp) / 10, 0), 1)
    b = 1 - r
    g = 0.2
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

latest_temp = temps[-1]
base_color = temp_to_color(latest_temp)

# 빛 퍼짐 효과 (성공 시)
def get_glow_frames(base_rgb, steps=20):
    glow_frames = []
    r_base, g_base, b_base = [int(c) for c in base_rgb[4:-1].split(",")]
    for i in range(steps):
        factor = 0.5 + 0.5 * np.sin(i * np.pi / steps)
        r = min(255, int(r_base + factor * 100))
        g = min(255, int(g_base + factor * 100))
        b = min(255, int(b_base + factor * 100))
        glow_frames.append(f"rgb({r},{g},{b})")
    return glow_frames

sphere = go.Figure()

if fusion_success:
    glow_colors = get_glow_frames(base_color)
    sphere.add_trace(
        go.Mesh3d(
            x=[0, 0, 1, 1, 0, 0, 1, 1],
            y=[0, 1, 0, 1, 0, 1, 0, 1],
            z=[0, 0, 0, 0, 1, 1, 1, 1],
            color=glow_colors[0],
            opacity=0.8,
            alphahull=5,
        )
    )
    st.write("에너지 방출 애니메이션 (아래)")
    for color in glow_colors:
        sphere.data[0].color = color
        st.plotly_chart(sphere, use_container_width=True)
        time.sleep(0.05)
else:
    sphere.add_trace(
        go.Mesh3d(
            x=[0, 0, 1, 1, 0, 0, 1, 1],
            y=[0, 1, 0, 1, 0, 1, 0, 1],
            z=[0, 0, 0, 0, 1, 1, 1, 1],
            color=base_color,
            opacity=0.7,
            alphahull=5,
        )
    )
    st.plotly_chart(sphere, use_container_width=True)
