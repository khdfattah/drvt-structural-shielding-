import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# 1. Page Configuration & Visual Styling (Matching DRVT Suite)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DRVT Structural Shielding Design Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .drvt-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #162E69;
        line-height: 1.15;
        margin-bottom: 0.6rem;
        font-family: 'Source Sans Pro', sans-serif;
    }
    .drvt-subtitle {
        font-size: 1.15rem;
        color: #334155;
        line-height: 1.55;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    .section-heading {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Fundamental Constants of DRVT (Dr. Khalid Abdel Fattah)
# ---------------------------------------------------------
H_PLANCK = 4.135667696e-15      # eV.s
C_LIGHT = 2.99792458e17         # nm/s
LAMBDA_C = 0.00242631           # nm (Compton Wavelength)
ALPHA_INV_SQ = 18778.865        # alpha^-2
LAMBDA_R = (2 * LAMBDA_C) * ALPHA_INV_SQ  # 91.127 nm (Reference Resonance Wavelength)
V_RES = LAMBDA_R * np.pi * (1.0**2)       # 286.398 nm^3 (Fundamental Resonant Volume)
R_C = 193.8                     # nm (Compton Boundary Radius)
A_0 = 0.0529177                 # nm (Bohr Radius)
LAMBDA_B = 32550.0              # nm (32.55 um, Bohr-Horizon Boundary)

# Benchmark Shielding Materials & Operational Regimes
REGIMES_DATA = {
    "Diagnostic X-Ray Regime (100 keV)": {
        "energy_kev": 100.0,
        "lambda_nm": 0.0124,
        "Mo": 0.1700,
        "materials": {
            "Water Baseline": {"rho": 1.0, "Mm": 0.1700, "Z_eff": 7.42},
            "Normal Concrete": {"rho": 2.3, "Mm": 0.1810, "Z_eff": 13.4},
            "Barite Concrete": {"rho": 3.5, "Mm": 0.4900, "Z_eff": 28.5},
            "Magnetite Concrete": {"rho": 3.6, "Mm": 0.3220, "Z_eff": 21.2},
            "Steel-Shot Concrete": {"rho": 4.8, "Mm": 0.3850, "Z_eff": 24.8},
        }
    },
    "Therapeutic Compton Regime (1.25 MeV)": {
        "energy_kev": 1250.0,
        "lambda_nm": 0.000992,
        "Mo": 0.0630,
        "materials": {
            "Water Baseline": {"rho": 1.0, "Mm": 0.0630, "Z_eff": 7.42},
            "Normal Concrete": {"rho": 2.3, "Mm": 0.0570, "Z_eff": 13.4},
            "Barite Concrete": {"rho": 3.5, "Mm": 0.0550, "Z_eff": 28.5},
            "Magnetite Concrete": {"rho": 3.6, "Mm": 0.0545, "Z_eff": 21.2},
            "Steel-Shot Concrete": {"rho": 4.8, "Mm": 0.0535, "Z_eff": 24.8},
        }
    },
    "Pair-Production Regime (5.00 MeV)": {
        "energy_kev": 5000.0,
        "lambda_nm": 0.000248,
        "Mo": 0.0303,
        "materials": {
            "Water Baseline": {"rho": 1.0, "Mm": 0.0303, "Z_eff": 7.42},
            "Normal Concrete": {"rho": 2.3, "Mm": 0.0291, "Z_eff": 13.4},
            "Barite Concrete": {"rho": 3.5, "Mm": 0.0324, "Z_eff": 28.5},
            "Magnetite Concrete": {"rho": 3.6, "Mm": 0.0312, "Z_eff": 21.2},
            "Steel-Shot Concrete": {"rho": 4.8, "Mm": 0.0348, "Z_eff": 24.8},
        }
    }
}

# ---------------------------------------------------------
# 3. Core Mathematical Engine (DRVT-Shielding Formulation)
# ---------------------------------------------------------
def compute_shielding_metrics(rho, Mm, Mo, lambda_nm, target_attenuation=50.0):
    V_eff = V_RES * (Mo / Mm)
    vol_ratio_pct = (V_eff / V_RES) * 100.0
    r_eff = np.sqrt(V_eff / (np.pi * lambda_nm))
    r_res_ref = np.sqrt(V_RES / (np.pi * lambda_nm))
    mu = rho * Mo * (V_RES / V_eff)
    hvl_mm = (np.log(2) / mu) * 10.0
    tvl_mm = (np.log(10) / mu) * 10.0
    
    transmission = 1.0 - (target_attenuation / 100.0)
    req_thickness_mm = (-np.log(transmission) / mu) * 10.0
    
    if vol_ratio_pct < 99.5:
        cavity_status = "Spatial Collapse / Contraction"
    elif vol_ratio_pct > 100.5:
        cavity_status = "Spatial Dilation / Porous State"
    else:
        cavity_status = "Resonant Equilibrium Baseline"
        
    return {
        "V_eff": V_eff,
        "vol_ratio_pct": vol_ratio_pct,
        "r_eff": r_eff,
        "r_res_ref": r_res_ref,
        "mu": mu,
        "hvl_mm": hvl_mm,
        "tvl_mm": tvl_mm,
        "req_thickness_mm": req_thickness_mm,
        "cavity_status": cavity_status
    }

def classify_drvt_regime(lambda_nm):
    if lambda_nm < LAMBDA_C:
        return "Pre-Resonant Domain"
    elif LAMBDA_C <= lambda_nm < LAMBDA_R:
        return "Above-Reference Resonance"
    elif np.isclose(lambda_nm, LAMBDA_R, rtol=1e-3):
        return "Reference Resonance"
    elif LAMBDA_R < lambda_nm <= LAMBDA_B:
        return "Below-Reference Resonance"
    else:
        return "Post-Atomic Resonance Domain"

# ---------------------------------------------------------
# 4. Sidebar Controls (Design & Simulation Parameters)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Design Parameters")
    st.caption("Dynamic Resonant Volume Theory (DRVT) — Dr. Khalid Abdel Fattah")
    
    input_mode = st.radio(
        "Operational Mode:",
        ["Benchmark Energy Regimes", "Custom Structural Matrix"]
    )
    
    if input_mode == "Benchmark Energy Regimes":
        selected_regime = st.selectbox("Operational Energy Regime:", list(REGIMES_DATA.keys()))
        reg_obj = REGIMES_DATA[selected_regime]
        selected_material = st.selectbox("Primary Shielding Matrix:", list(reg_obj["materials"].keys()), index=2)
        
        mat_data = reg_obj["materials"][selected_material]
        rho = mat_data["rho"]
        Mm = mat_data["Mm"]
        Mo = reg_obj["Mo"]
        lambda_nm = reg_obj["lambda_nm"]
        energy_kev = reg_obj["energy_kev"]
    else:
        energy_kev = st.number_input("Incident Photon Energy (keV):", min_value=10.0, max_value=20000.0, value=100.0, step=10.0)
        lambda_nm = (H_PLANCK * C_LIGHT) / (energy_kev * 1000.0)
        Mo = st.number_input("Water Mass Attenuation Mo (cm²/g):", min_value=0.0010, max_value=10.0000, value=0.1700, format="%.4f")
        selected_material = st.text_input("Custom Matrix Name:", value="High-Density Barite Concrete")
        rho = st.slider("Bulk Mass Density ρ (g/cm³):", min_value=1.0, max_value=8.0, value=3.5, step=0.1)
        Mm = st.number_input("Matrix Mass Attenuation μ/ρ (cm²/g):", min_value=0.0010, max_value=10.0000, value=0.4900, format="%.4f")

    st.divider()
    target_attenuation = st.slider("Target Attenuation Efficiency (%):", min_value=50.0, max_value=99.99, value=90.0, step=0.5)
    
    st.markdown("---")
    st.markdown(f"""
    **DRVT Fundamental Invariants:**
    * $V_{{res}} = {V_RES:.3f}\\text{{ nm}}^3$
    * $\\lambda_R = {LAMBDA_R:.3f}\\text{{ nm}}$
    * $\\lambda_c = {LAMBDA_C:.6f}\\text{{ nm}}$
    """)

# ---------------------------------------------------------
# 5. Main Header & Status Banner (Exact Layout Match)
# ---------------------------------------------------------
st.markdown('<div class="drvt-title">DRVT Structural Shielding<br>Design Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="drvt-subtitle">Civil & Radiation Protection Platform applying '
    '<strong>Dynamic Resonant Volume Theory (DRVT)</strong> by <strong>Dr. Khalid Abdel Fattah</strong> '
    'to optimize nanoscale interaction cavities and compress structural concrete barriers.</div>',
    unsafe_allow_html=True
)

metrics = compute_shielding_metrics(rho, Mm, Mo, lambda_nm, target_attenuation)
drvt_regime_label = classify_drvt_regime(lambda_nm)

st.info(
    f"**DRVT Regime:** {drvt_regime_label} | "
    f"**Matrix:** {selected_material} (Energy: {energy_kev:.2f} keV, Density: {rho:.2f} g/cm³, $\\lambda$: {lambda_nm:.6f} nm)"
)

# ---------------------------------------------------------
# 6. Primary Engineering & Structural Metrics
# ---------------------------------------------------------
st.markdown('<div class="section-heading">Primary Engineering & Structural Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_label = "Spatial Contraction" if metrics["vol_ratio_pct"] < 100 else "Spatial Dilation"
    st.metric(
        label="Effective Cavity Volume (V_eff)",
        value=f"{metrics['V_eff']:.2f} nm³",
        delta=f"{metrics['vol_ratio_pct']:.1f}% ({delta_label})",
        delta_color="inverse" if metrics["vol_ratio_pct"] < 100 else "normal"
    )

with col2:
    st.metric(
        label="Half-Value Layer (HVL)",
        value=f"{metrics['hvl_mm']:.2f} mm",
        delta=f"TVL: {metrics['tvl_mm']:.1f} mm",
        delta_color="off"
    )

with col3:
    st.metric(
        label="Linear Attenuation (μ)",
        value=f"{metrics['mu']:.4f} cm⁻¹",
        delta=f"r_eff: {metrics['r_eff']:.2f} nm",
        delta_color="off"
    )

with col4:
    st.metric(
        label=f"Design Wall Thickness ({target_attenuation:.0f}%)",
        value=f"{metrics['req_thickness_mm']:.1f} mm",
        delta=f"{metrics['req_thickness_mm']/10.0:.2f} cm barrier",
        delta_color="off"
    )

st.divider()

# ---------------------------------------------------------
# 7. Analytical Visualizations, Composite Wall & BIM Matrix
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🧱 Multi-Layer Composite Wall",
    "📊 Multi-Material Cavity Analysis",
    "🌐 Nanoscale Geometry Cross-Section",
    "📑 BIM & Structural Export Matrix"
])

# --- TAB 1: Multi-Layer Composite Barrier Calculator ---
with tab1:

