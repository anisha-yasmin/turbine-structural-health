import streamlit as st
import numpy as np
import plotly.graph_objects as go

# High-End Engineering Suite Configuration
st.set_page_config(page_title="Wind Turbine SHM Platform", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CAD INTERFACE CSS OVERHAUL ---
st.markdown("""
    <style>
    /* Main App Background Override */
    .main {
        background-color: #060913 !important;
        color: #f1f5f9 !important;
    }
    
    /* Sidebar Engineering Control Panel Styling */
    [data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid #1e293b !important;
    }
    [data-testid="stSidebar"] *, div[data-baseweb="select"] * {
        color: #cbd5e1 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom CSS Cards: Telemetry Panels */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        padding: 20px 24px !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4) !important;
        transition: border 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
    }
    
    /* Target Text Inside Metric Blocks to Prevent Ellipsis Cutoff */
    div[data-testid="stMetricValue"] > div {
        color: #38bdf8 !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    label[data-testid="stMetricLabel"] > div > p {
        color: #94a3b8 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        white-space: normal !important;
    }
    
    /* Horizontal Rule Separators */
    hr {
        border-color: rgba(30, 41, 59, 0.7) !important;
    }
    
    /* Section Headers styling */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }
    h1 {
        color: #ffffff !important;
    }
    h3 {
        color: #f1f5f9 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMarkdown p {
        color: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)

# Application Header Block
st.title("ROTORDYNAMIC STRUCTURAL HEALTH MONITORING (SHM)")
st.markdown("Predictive Aeroelasticity & Structural Dynamics Diagnostics Suite | Cantilever Composite Blade")
st.markdown("---")

# --- SIDEBAR CONTROL INPUTS ---
st.sidebar.markdown("### SYSTEM TELEMETRY")
blade_length = st.sidebar.slider("SPAN LENGTH (L) [meters]:", 40, 90, 75)
crack_depth = st.sidebar.slider("STRUCTURAL FATIGUE DELTA (% Area Loss):", 0, 50, 15)
rpm = st.sidebar.slider("ROTOR SPEED (Omega) [RPM]:", 0, 30, 15)

# --- ROTORDYNAMIC SYSTEM PHYSICS ENGINE ---
E, rho, width, thickness = 40e9, 1800, 3.0, 0.4
I_healthy = (width * (thickness**3)) / 12
I_damaged = I_healthy * (1 - (crack_depth / 100))
mass_per_len = rho * width * thickness

# Frequency Derivations via Euler-Bernoulli Boundary Mechanics
omega_1 = (3.516 / (blade_length**2)) * np.sqrt((E * I_damaged) / mass_per_len)
omega_2 = (22.03 / (blade_length**2)) * np.sqrt((E * I_damaged) / mass_per_len)

# Rotor Forcing Waves
rpm_range = np.linspace(0, 30, 100)
freq_1P = rpm_range / 60.0
freq_3P = 3 * freq_1P

current_3P = 3 * (rpm / 60.0)

is_resonant = abs(omega_1 - current_3P) < 0.08 or abs(omega_2 - current_3P) < 0.08
resonance_status = "CRITICAL COUPLING" if is_resonant else "STABLE OPERATION"

# Fatigue calculations via Miner's Rule
stiffness_ratio = I_damaged / I_healthy
if crack_depth == 0:
    hours_remaining = 175200.0  
else:
    damage_exponent = (1.0 / stiffness_ratio) ** 2.5
    hours_remaining = max(100.0, 175200.0 * (stiffness_ratio ** 1.5) - (crack_depth * 250 * damage_exponent))

if is_resonant:
    hours_remaining *= 0.1  

# --- SYSTEM METRICS PANEL ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="1st Mode Freq (w1)", value=f"{omega_1:.3f} Hz")
with col2:
    st.metric(label="2nd Mode Freq (w2)", value=f"{omega_2:.3f} Hz")
with col3:
    st.metric(label="Aeroelastic Diagnosis", value=resonance_status)
with col4:
    st.metric(label="Time to Failure", value=f"{int(hours_remaining):,} Hours")

st.markdown("---")

# --- VISUALIZATION 1: LIVE 3D STRUT DEFORMATION SOLVER ---
st.subheader("3D Finite Element Deformation Mesh (Modal Displacement Analysis)")

# Generate 3D blade wireframe coordinates
z_segments = 40
theta_segments = 16

z = np.linspace(0, blade_length, z_segments)
theta = np.linspace(0, 2 * np.pi, theta_segments)
z_mesh, theta_mesh = np.meshgrid(z, theta)

# Tapered aerodynamic chord distribution
chord_profile = width * (1 - 0.7 * (z_mesh / blade_length))
thick_profile = thickness * (1 - 0.6 * (z_mesh / blade_length))

# Euler-Bernoulli Mode Shape Deflection multiplier
norm_z = z_mesh / blade_length
mode_deflection = (np.cosh(1.875 * norm_z) - np.cos(1.875 * norm_z)) - 0.734 * (np.sinh(1.875 * norm_z) - np.sin(1.875 * norm_z))

# Dynamic displacement amplification factor scales with structural damage
scaling_factor = 2.0 * (1.0 + (crack_depth / 15.0))
if is_resonant:
    scaling_factor *= 2.5 

delta_x = mode_deflection * scaling_factor

X = chord_profile * np.cos(theta_mesh) + delta_x
Y = thick_profile * np.sin(theta_mesh)
Z = z_mesh

strain_intensity = (mode_deflection ** 2) * (crack_depth + 10)

# CRITICAL FIX: Restructured the colorbar dict parameters to map to modern Plotly API specifications
fig_3d = go.Figure(data=[go.Surface(
    x=X, y=Y, z=Z, 
    surfacecolor=strain_intensity, 
    colorscale="Plasma",
    colorbar=dict(
        title=dict(text="Relative Strain", font=dict(color="#94a3b8")),
        tickfont=dict(color="#64748b"),
        len=0.6
    )
)])

fig_3d.update_layout(
    template="plotly_dark",
    height=550,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    scene=dict(
        xaxis=dict(title="Flapwise Deflection (m)", gridcolor="#1e293b", titlefont=dict(color="#64748b"), tickfont=dict(color="#475569")),
        yaxis=dict(title="Thickness Profile (m)", gridcolor="#1e293b", titlefont=dict(color="#64748b"), tickfont=dict(color="#475569")),
        zaxis=dict(title="Blade Span (m)", gridcolor="#1e293b", titlefont=dict(color="#64748b"), tickfont=dict(color="#475569")),
        aspectratio=dict(x=1, y=1, z=2)
    )
)
st.plotly_chart(fig_3d, use_container_width=True)

st.markdown("---")

# --- VISUALIZATION 2: CAMPBELL DIAGRAM ---
st.subheader("Rotordynamic Campbell Diagram (Critical Speed Mapping)")

fig_campbell = go.Figure()
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=freq_1P, name="1P Rotor Order", line=dict(color="#38bdf8", width=1.5, dash="dash")))
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=freq_3P, name="3P Forcing Freq", line=dict(color="#f43f5e", width=2, dash="dot")))
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=np.ones_like(rpm_range) * omega_1, name="1st Flexural Mode (w1)", line=dict(color="#34d399", width=2.5)))
fig_campbell.add_trace(go.Scatter(x=rpm_range, y=np.ones_like(rpm_range) * omega_2, name="2nd Flexural Mode (w2)", line=dict(color="#a78bfa", width=2.5)))
fig_campbell.add_trace(go.Scatter(x=[rpm, rpm], y=[0, 2.5], name="Operational RPM", line=dict(color="#ffffff", width=1.5)))

fig_campbell.update_layout(
    template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Rotor Operational Speed (RPM)", yaxis_title="Frequency (Hz)", yaxis_range=[0, 2.2],
    xaxis_gridcolor="#1e293b", yaxis_gridcolor="#1e293b",
    xaxis_titlefont=dict(color="#64748b"), yaxis_titlefont=dict(color="#64748b"),
    xaxis_tickfont=dict(color="#475569"), yaxis_tickfont=dict(color="#475569"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#cbd5e1"))
)
st.plotly_chart(fig_campbell, use_container_width=True)

st.markdown("---")

# --- VISUALIZATION 3: SPECTRUM DENSITIES ---
st.subheader("Accelerometer Spectral Cascade (Dynamic FFT Signal Tracking)")

freq_axis = np.linspace(0, 2.5, 600)
structural_response = (1 / (1 + (freq_axis - omega_1)**2/0.002)) + (0.4 / (1 + (freq_axis - omega_2)**2/0.002))
forcing_response = (0.8 / (1 + (freq_axis - (3 * (rpm / 60.0)))**2/(0.001 if is_resonant else 0.01)))
total_signal = structural_response + forcing_response

fig_fft = go.Figure()
fig_fft.add_trace(go.Scatter(x=freq_axis, y=total_signal, name="Sensor Telemetry", fill='tozeroy', line=dict(color="#0ea5e9", width=2), fillcolor="rgba(14, 165, 233, 0.08)"))
fig_fft.update_layout(
    template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Frequency Domain Axis (Hz)", yaxis_title="Vibration Power Density (G2/Hz)",
    xaxis_gridcolor="#1e293b", yaxis_gridcolor="#1e293b",
    xaxis_titlefont=dict(color="#64748b"), yaxis_titlefont=dict(color="#64748b"),
    xaxis_tickfont=dict(color="#475569"), yaxis_tickfont=dict(color="#475569"),
    legend=dict(font=dict(color="#cbd5e1"))
)
st.plotly_chart(fig_fft, use_container_width=True)
