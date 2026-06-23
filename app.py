import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Structural Health Twin", layout="wide")
st.title("WIND TURBINE STRUCTURAL HEALTH PLATFORM")
st.markdown("**Real-time Modal Analysis & Dynamic Vibration Diagnostic Environment**")
st.markdown("---")

blade_length = st.sidebar.slider("Blade Length (L) [meters]:", 40, 90, 70)
crack_depth = st.sidebar.slider("Simulated Internal Crack Severity (% Area Loss):", 0, 50, 0)
rpm = st.sidebar.slider("Rotor Operational Speed (RPM):", 5, 25, 12)

E, rho, width, thickness = 40e9, 1800, 3.0, 0.4
I_healthy = (width * (thickness**3)) / 12
I_damaged = I_healthy * (1 - (crack_depth / 100))
mass_per_len = rho * width * thickness

omega_n_actual = (3.516 / (blade_length**2)) * np.sqrt((E * I_damaged) / mass_per_len)
f_blade_passing = 3 * (rpm / 60.0)
stiffness_retention = (I_damaged / I_healthy) * 100
resonance_risk = "CRITICAL RESONANCE" if abs(omega_n_actual - f_blade_passing) < 0.1 else "SAFE OPERATION"

col1, col2, col3, col4 = st.columns(4)
col1.metric("NATURAL FREQUENCY", f"{omega_n_actual:.3f} Hz")
col2.metric("STIFFNESS RETENTION", f"{stiffness_retention:.1f} %")
col3.metric("EXCITATION FREQUENCY", f"{f_blade_passing:.3f} Hz")
col4.metric("RESONANCE DIAGNOSTIC", resonance_risk)

st.markdown("---")
st.subheader("Fast Fourier Transform (FFT) Power Spectral Density")
freq_axis = np.linspace(0, 5, 500)
signal = 1 / (1 + (freq_axis - omega_n_actual)**2/0.005) + 0.3 / (1 + (freq_axis - f_blade_passing)**2/0.002)

fig_fft = go.Figure(go.Scatter(x=freq_axis, y=signal, line=dict(color="#58a6ff", width=2.5)))
fig_fft.update_layout(template="plotly_dark", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
st.plotly_chart(fig_fft, use_container_width=True)
