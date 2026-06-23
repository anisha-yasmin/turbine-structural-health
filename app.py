import streamlit as st
import numpy as np
import plotly.graph_objects as go

# High-End Structural Analytics Suite UI Setup
st.set_page_config(page_title="Wind Turbine SHM Digital Twin", layout="wide")

# --- INDUSTRIAL CAE DARK GRID UI ---
st.markdown("""
    <style>
    .main {background-color: #0b0f19; color: #e2e8f0;}
    [data-testid="stSidebar"] {background-color: #0f172a; border-right: 1px solid #1e293b;}
    [data-testid="stSidebar"] *, div[data-baseweb="select"] * {color: #f1f5f9 !important; font-weight: 600;}
    
    /* Neumorphic Metric Panels */
    [data-testid="stMetricValue"] {
        color: #ff3e3e !important;
        font-family: 'Courier New', monospace;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(255, 62, 62, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stMetric {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
        padding: 22px !important;
        border-radius: 8px !important;
        border: 1px solid #ef4444 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("ROTORDYNAMIC STRUCTURAL HEALTH MONITORING (SHM) PLATFORM")
st.markdown("**Predictive Aeroelasticity & Structural Dynamics Diagnostics Suite | Cantilever Composite Blade**")
st.markdown("---")

# --- SIDEBAR TUNING UNIT ---
st.sidebar.markdown("SYSTEM TELEMETRY")
blade_length = st.sidebar.slider("SPAN LENGTH (L) [meters]:", 40, 90, 75)
crack_depth = st.sidebar.slider("STRUCTURAL FATIGUE DELTA (% Area Loss):", 0, 50, 15)
rpm = st.sidebar.slider("ROTOR SPEED (Ω) [RPM]:", 0, 30, 15)

# --- ROTORDYNAMIC CALCULATIONS ENGINE ---
E, rho, width, thickness = 40e9, 1800, 3.0, 0.4
I_healthy = (width * (thickness**3)) / 12
I_damaged = I_healthy * (1 - (crack_depth / 100))
mass_per_len = rho * width * thickness

# Frequency Derivations via Euler-Bernoulli Boundary Mechanics
omega_1 = (3.516 / (blade_length**2)) * np.sqrt((E * I_damaged) / mass_per_len)
omega_2 = (22.03 / (blade_length**2)) * np.sqrt((E * I_damaged) / mass_per_len)

# Rotor Harmonical Forcing Waves (1P and 3P)
rpm_range = np.linspace(0, 30, 100)
freq_1P = rpm_range / 60.0
freq_3P = 3 * freq_1P

current_1P = rpm / 60.0
current_3P = 3 * current_1P

# Resonance Safety Diagnostics
resonance_window = 0.08
is_resonant = abs(omega_1 - current_3P) < resonance_window or abs(omega_2 - current_3P) < resonance_window
resonance_status = "CRITICAL RESONANCE DETECTED" if is_resonant else "STRUCTURALLY STABLE"

# --- SYSTEM METRICS PANEL ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="1st Mode Natural Freq (ω1)", value=f"{omega_1:.3f} Hz")
with col2:
    st.metric(label="2nd Mode Natural Freq (ω2)", value=f"{omega_2:.3f} Hz")
with col3:
    st.metric(label="3P Forcing Excitation", value=f"{current_3P:.3f} Hz")
with col4:
    st.metric(label="Aeroelastic Diagnosis", value=resonance_status)

st.markdown("---")

# --- VISUALIZATION 1: INTERACTIVE CAMPBELL DIAGRAM ---
st.subheader("Rotordynamic Campbell Diagram (Critical Speed Mapping)")
st.markdown("The intersections between the operational forcing frequencies (1P, 3P lines) and the structural natural frequencies (ω1, ω2) indicate mechanical resonance speeds.")

fig_campbell = go.Figure()

# Plot Forcing Engine Vectors
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=freq_1P, name="1P Rotor Order (Unbalance Forcing)", line=dict(color="#60a5fa", width=2, dash="dash")))
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=freq_3P, name="3P Blade Passing Frequency (Aerodynamic Forcing)", line=dict(color="#f43f5e", width=2.5, dash="dot")))

# Plot Stiffness Frequency Limits
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=np.ones_like(rpm_range) * omega_1, name="1st Flexural Mode (Flapwise ω1)", line=dict(color="#34d399", width=3)))
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=np.ones_like(rpm_range) * omega_2, name="2nd Flexural Mode (Edgewise ω2)", line=dict(color="#a78bfa", width=3)))

# Plot Current Operational State Indicator
fig_campbell.add_trace(go.Scatter(x=[rpm, rpm], y=[0, 2.5], name="Current Operational RPM", line=dict(color="#ffffff", width=2)))

# CRITICAL FIX: Re-mapped the layouts using clean flat string styling keys to bypass the dictionary ValueError
fig_campbell.update_layout(
    template="plotly_dark", 
    height=450, 
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Rotor Operational Speed (RPM)",
    yaxis_title="Frequency (Hz)",
    yaxis_range=[0, 2.2],
    xaxis_gridcolor="#1e293b",
    yaxis_gridcolor="#1e293b",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_campbell, use_container_width=True)

st.markdown("---")

# --- VISUALIZATION 2: RE-STRUCTURED SPECTRUM DENSITIES ---
st.subheader("📈 Accelerometer Spectral Cascade (Dynamic FFT Signal Tracking)")

freq_axis = np.linspace(0, 2.5, 600)
structural_response = (1 / (1 + (freq_axis - omega_1)**2/0.002)) + (0.4 / (1 + (freq_axis - omega_2)**2/0.002))
forcing_response = (0.8 / (1 + (freq_axis - current_3P)**2/(0.001 if is_resonant else 0.01)))

total_signal = structural_response + forcing_response

fig_fft = go.Figure()
fig_fft.add_trace(go.Scatter(x=freq_axis, y=total_signal, name="Sensor Telemetry Power Spectrum", fill='tozeroy', line=dict(color="#00f2fe", width=2)))
fig_fft.update_layout(
    template="plotly_dark", 
    height=350, 
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Frequency Domain Axis (Hz)", 
    yaxis_title="Vibration Power Density (G²/Hz)",
    xaxis_gridcolor="#1e293b",
    yaxis_gridcolor="#1e293b"
)
st.plotly_chart(fig_fft, use_container_width=True)
