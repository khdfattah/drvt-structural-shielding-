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
    [data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
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
    delta_label = "Contraction" if metrics["vol_ratio_pct"] < 100 else "Dilation"
    st.metric(
        label="Cavity Volume (V_eff)",
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
        label="Attenuation (μ)",
        value=f"{metrics['mu']:.4f} cm⁻¹",
        delta=f"r_eff: {metrics['r_eff']:.2f} nm",
        delta_color="off"
    )

with col4:
    st.metric(
        label=f"Wall Thickness ({target_attenuation:.0f}%)",
        value=f"{metrics['req_thickness_mm']:.1f} mm",
        delta=f"{metrics['req_thickness_mm']/10.0:.2f} cm barrier",
        delta_color="off"
    )

st.divider()

# ---------------------------------------------------------
# ---------------------------------------------------------
# 7. Analytical Visualizations, Composite Wall, BIM & Theory
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧱 Multi-Layer Composite Wall",
    "📊 Multi-Material Cavity Analysis",
    "🌐 Nanoscale Geometry Cross-Section",
    "📑 BIM & Structural Export Matrix",
    "📖 DRVT Mathematical Formulation"
])

# --- TAB 1: Multi-Layer Composite Barrier Calculator ---
with tab1:
    st.subheader("Smart Multi-Layer Composite Shielding Calculator")
    st.markdown(
        "Design layered structural barriers combining high-Z nanoscale cavity contraction (e.g., Barite/Steel-Shot) "
        "with structural concrete backing based on **DRVT Volumetric Attenuation Law**."
    )

    
    if input_mode == "Benchmark Energy Regimes":
        available_mats = list(reg_obj["materials"].keys())
        num_layers = st.slider("Number of Structural Barrier Layers:", min_value=2, max_value=4, value=3)
        
        layer_configs = []
        cols_layers = st.columns(num_layers)
        
        default_indices = list((4, 2, 1, 3))
        default_thicknesses = list((25.0, 40.0, 100.0, 30.0))
        
        for i in range(num_layers):
            with cols_layers[i]:
                st.markdown(f"**Layer {i+1} (Incident → Exit)**")
                idx_choice = default_indices[i] if default_indices[i] < len(available_mats) else 1
                l_mat = st.selectbox(
                    f"Material (L{i+1}):",
                    available_mats,
                    index=idx_choice,
                    key=f"mat_l_{i}"
                )
                l_thick_mm = st.number_input(
                    f"Thickness (mm) (L{i+1}):",
                    min_value=1.0,
                    max_value=5000.0,
                    value=default_thicknesses[i],
                    step=5.0,
                    key=f"thick_l_{i}"
                )
                
                m_props = reg_obj["materials"][l_mat]
                l_metrics = compute_shielding_metrics(m_props["rho"], m_props["Mm"], Mo, lambda_nm)
                layer_configs.append({
                    "Layer": f"Layer {i+1}: {l_mat}",
                    "Material": l_mat,
                    "Thickness_mm": l_thick_mm,
                    "Density": m_props["rho"],
                    "V_eff": l_metrics["V_eff"],
                    "V_ratio": l_metrics["vol_ratio_pct"],
                    "mu": l_metrics["mu"],
                    "mu_x": l_metrics["mu"] * (l_thick_mm / 10.0)
                })
        
        # Cumulative DRVT Attenuation Calculations
        total_thickness_mm = sum(item["Thickness_mm"] for item in layer_configs)
        total_mu_x = sum(item["mu_x"] for item in layer_configs)
        transmission_fraction = np.exp(-total_mu_x)
        total_attenuation_pct = (1.0 - transmission_fraction) * 100.0
        total_hvl_equivalents = total_mu_x / np.log(2)
        
        # Equivalent Normal Concrete Thickness for Footprint Comparison
        norm_props = reg_obj["materials"]["Normal Concrete"]
        norm_metrics = compute_shielding_metrics(norm_props["rho"], norm_props["Mm"], Mo, lambda_nm)
        equiv_normal_mm = (total_mu_x / norm_metrics["mu"]) * 10.0
        space_saved_mm = equiv_normal_mm - total_thickness_mm
        space_saved_pct = (space_saved_mm / equiv_normal_mm) * 100.0 if equiv_normal_mm > 0 else 0.0
        
        st.markdown("---")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric(
                label="Composite Thickness",
                value=f"{total_thickness_mm:.1f} mm",
                delta=f"{total_thickness_mm/10.0:.2f} cm total wall",
                delta_color="off"
            )
        with m_col2:
            st.metric(
                label="Shielding Efficiency",
                value=f"{total_attenuation_pct:.4f}%",
                delta=f"{total_hvl_equivalents:.2f} HVLs blocked",
                delta_color="normal"
            )
        with m_col3:
            st.metric(
                label="Normal Concrete Eq.",
                value=f"{equiv_normal_mm:.1f} mm",
                delta=f"{equiv_normal_mm/10.0:.2f} cm standard wall",
                delta_color="off"
            )
        with m_col4:
            st.metric(
                label="Footprint Saved",
                value=f"{space_saved_mm:.1f} mm",
                delta=f"{space_saved_pct:.1f}% wall reduction",
                delta_color="normal" if space_saved_mm >= 0 else "inverse"
            )
            
        # Generate Step-by-Step Beam Intensity Profile across Layers
        depth_points = [0.0]
        intensity_points = [100.0]
        layer_labels = ["Incident Beam (0 mm)"]
        
        cum_depth = 0.0
        cum_mux = 0.0
        for item in layer_configs:
            sub_steps = np.linspace(0, item["Thickness_mm"], 25)[1:]
            for s in sub_steps:
                d_val = cum_depth + s
                mux_val = cum_mux + item["mu"] * (s / 10.0)
                depth_points.append(d_val)
                intensity_points.append(100.0 * np.exp(-mux_val))
                layer_labels.append(item["Layer"])
            cum_depth += item["Thickness_mm"]
            cum_mux += item["mu_x"]
            
        df_profile = pd.DataFrame({
            "Wall Depth (mm)": depth_points,
            "Relative Beam Intensity I/I0 (%)": intensity_points,
            "Active Barrier Layer": layer_labels
        })
        
        fig_comp_wall = px.line(
            df_profile,
            x="Wall Depth (mm)",
            y="Relative Beam Intensity I/I0 (%)",
            color="Active Barrier Layer",
            title=f"Radiation Intensity Decay Across Composite Barrier ({selected_regime})"
        )
        fig_comp_wall.update_traces(line=dict(width=3))
        st.plotly_chart(fig_comp_wall, use_container_width=True)
        
        # Layer Breakdown Summary Table
        df_layers_summary = pd.DataFrame(layer_configs)[
            ["Layer", "Thickness_mm", "Density", "V_eff", "V_ratio", "mu", "mu_x"]
        ].rename(columns={
            "Thickness_mm": "Thickness (mm)",
            "Density": "ρ (g/cm³)",
            "V_eff": "V_eff (nm³)",
            "V_ratio": "V_eff/V_res (%)",
            "mu": "μ (cm⁻¹)",
            "mu_x": "Optical Depth (μ·x)"
        })
        st.dataframe(df_layers_summary, use_container_width=True)
    else:
        st.info("Switch to 'Benchmark Energy Regimes' in the sidebar to configure multi-layer composite concrete barriers.")

# --- TAB 2: Multi-Material Cavity Analysis ---
with tab2:
    if input_mode == "Benchmark Energy Regimes":
        rows = []
        for mat_name, props in reg_obj["materials"].items():
            m_res = compute_shielding_metrics(props["rho"], props["Mm"], Mo, lambda_nm, target_attenuation)
            rows.append({
                "Shielding Medium": mat_name,
                "Density ρ (g/cm³)": props["rho"],
                "Z_eff": props["Z_eff"],
                "V_eff (nm³)": round(m_res["V_eff"], 2),
                "V_eff / V_res (%)": round(m_res["vol_ratio_pct"], 2),
                "r_eff (nm)": round(m_res["r_eff"], 2),
                "μ (cm⁻¹)": round(m_res["mu"], 4),
                "HVL (mm)": round(m_res["hvl_mm"], 2),
                f"Thickness {target_attenuation:.0f}% (mm)": round(m_res["req_thickness_mm"], 2)
            })
        df_results = pd.DataFrame(rows)
        
        c1, c2 = st.columns(2)
        with c1:
            fig_cavity = px.bar(
                df_results,
                x="Shielding Medium",
                y="V_eff / V_res (%)",
                color="Shielding Medium",
                text="V_eff / V_res (%)",
                title=f"Nanoscale Cavity Deformation vs. V_res ({selected_regime})"
            )
            fig_cavity.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="V_res = 286.398 nm³ (100%)")
            st.plotly_chart(fig_cavity, use_container_width=True)
            
        with c2:
            fig_hvl = px.bar(
                df_results,
                x="Shielding Medium",
                y="HVL (mm)",
                color="Shielding Medium",
                text="HVL (mm)",
                title=f"Required Structural Half-Value Layer ({selected_regime})"
            )
            st.plotly_chart(fig_hvl, use_container_width=True)
            
        st.subheader("Breathing Geometric Space Across Energy Extremes")
        breath_rows = []
        for r_key, r_val in REGIMES_DATA.items():
            for m_key, m_val in r_val["materials"].items():
                if m_key != "Water Baseline":
                    b_m = compute_shielding_metrics(m_val["rho"], m_val["Mm"], r_val["Mo"], r_val["lambda_nm"])
                    breath_rows.append({
                        "Operational Regime": r_key,
                        "Shielding Medium": m_key,
                        "V_eff / V_res (%)": b_m["vol_ratio_pct"],
                        "HVL (mm)": b_m["hvl_mm"]
                    })
        df_breath = pd.DataFrame(breath_rows)
        fig_breath = px.line(
            df_breath,
            x="Operational Regime",
            y="V_eff / V_res (%)",
            color="Shielding Medium",
            markers=True,
            title="Volumetric Contraction & Dilation Trajectory (100 keV → 1.25 MeV → 5.00 MeV)"
        )
        fig_breath.add_hline(y=100, line_dash="dot", line_color="black", annotation_text="Water Reference Baseline (100%)")
        st.plotly_chart(fig_breath, use_container_width=True)
    else:
        st.info("Switch to 'Benchmark Energy Regimes' in the sidebar to view comparative charts across standard and heavy concretes.")

# --- TAB 3: Nanoscale Geometry Cross-Section ---
with tab3:
    st.subheader(f"Isotropic Interaction Cavity Cross-Section: {selected_material}")
    g_col1, g_col2 = st.columns([1.3, 1])
    
    with g_col1:
        theta = np.linspace(0, 2 * np.pi, 250)
        fig_circle = go.Figure()
        
        trace_water = go.Scatter(
            x=metrics["r_res_ref"] * np.cos(theta),
            y=metrics["r_res_ref"] * np.sin(theta),
            mode="lines",
            name=f"Water Reference Radius (r_res = {metrics['r_res_ref']:.2f} nm)",
            line=dict(color="#1E3A8A", dash="dash", width=2)
        )
        fig_circle.add_trace(trace_water)
        
        is_contracted = metrics["vol_ratio_pct"] < 100
        fill_rgba = "rgba(220, 38, 38, 0.22)" if is_contracted else "rgba(16, 185, 129, 0.22)"
        stroke_hex = "#DC2626" if is_contracted else "#059669"
        
        trace_mat = go.Scatter(
            x=metrics["r_eff"] * np.cos(theta),
            y=metrics["r_eff"] * np.sin(theta),
            mode="lines",
            fill="toself",
            fillcolor=fill_rgba,
            name=f"{selected_material} (r_eff = {metrics['r_eff']:.2f} nm)",
            line=dict(color=stroke_hex, width=3)
        )
        fig_circle.add_trace(trace_mat)
        
        fig_circle.update_layout(
            title="Transverse Resonant State Cross-Section (A_eff = π · r_eff²)",
            xaxis_title="Transverse Coordinate X (nm)",
            yaxis_title="Transverse Coordinate Y (nm)",
            yaxis=dict(scaleanchor="x", scaleratio=1),
            height=480
        )
        st.plotly_chart(fig_circle, use_container_width=True)
        
    with g_col2:
        st.markdown("#### Quantum-Geometric Diagnostics")
        st.write(f"""
        * **Theoretical Framework:** Dynamic Resonant Volume Theory (DRVT) — Dr. Khalid Abdel Fattah
        * **Incident Wavelength ($\\lambda$):** `{lambda_nm:.6f} nm`
        * **Reference Resonant Area ($A_{{ref}}$):** `{V_RES / lambda_nm:.2f} nm²`
        * **Effective Cavity Volume ($V_{{eff}}$):** `{metrics['V_eff']:.2f} nm³`
        * **Geometric State:** `{metrics['cavity_status']}`
        """)
        if is_contracted:
            st.success(
                "**Spatial Collapse Active:** High-Z atomic shells or nuclear fields compress the interaction cavity below "
                "the 286.398 nm³ baseline, driving non-linear attenuation and reducing wall thickness."
            )
        else:
            st.warning(
                "**Spatial Dilation Active:** Compton scattering expands the interaction cavity beyond the water baseline, "
                "requiring bulk mass compaction (ρ) to maintain structural attenuation."
            )

# --- TAB 4: BIM & Structural Export Matrix ---
with tab4:
    st.subheader("Structural Shielding Data Matrix (BIM Integration Ready)")
    if input_mode == "Benchmark Energy Regimes":
        st.dataframe(df_results, use_container_width=True)
        csv_bytes = df_results.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Single-Material BIM Dataset (CSV)",
            data=csv_bytes,
            file_name=f"DRVT_Structural_Shielding_{selected_regime[:10].replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.subheader("Composite Barrier Design Export (CSV)")
        comp_csv = df_layers_summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Multi-Layer Composite Wall Schedule (CSV)",
            data=comp_csv,
            file_name=f"DRVT_Composite_Barrier_{selected_regime[:10].replace(' ', '_')}.csv",
            mime="text/csv"
        )
    else:
        custom_table = pd.DataFrame([{
            "Shielding Medium": selected_material,
            "Energy (keV)": energy_kev,
            "Wavelength (nm)": lambda_nm,
            "Density (g/cm³)": rho,
            "V_eff (nm³)": round(metrics["V_eff"], 2),
            "V_eff / V_res (%)": round(metrics["vol_ratio_pct"], 2),
            "r_eff (nm)": round(metrics["r_eff"], 2),
            "μ (cm⁻¹)": round(metrics["mu"], 4),
            "HVL (mm)": round(metrics["hvl_mm"], 2),
            "TVL (mm)": round(metrics["tvl_mm"], 2),
            f"Thickness {target_attenuation:.0f}% (mm)": round(metrics["req_thickness_mm"], 2)
        }])
        st.dataframe(custom_table, use_container_width=True)

# --- TAB 5: DRVT Mathematical Formulation & Theoretical Reference ---
with tab5:
    st.subheader("Dynamic Resonant Volume Theory (DRVT) — Mathematical & Physical Framework")
    st.markdown("**Author:** Dr. Khalid Abdel Fattah (*Merowe Institute of Technology, Merowe University of Technology, Sudan*)")
    
    col_eq1, col_eq2 = st.columns(2)
    
    with col_eq1:
        st.markdown("#### 1. Fundamental Quantum-Geometric Invariants")
        st.latex(r"V_{\text{res}} = \frac{2 \lambda_c \cdot \pi r_1^2}{\alpha^2} = 286.398 \text{ nm}^3 \quad (r_1 = 1 \text{ nm})")
        st.latex(r"\lambda_R = \frac{2 \lambda_c}{\alpha^2} = 91.127 \text{ nm}, \quad \lambda_c = \frac{h}{m_e c} = 0.00242631 \text{ nm}")
        st.latex(r"\frac{E}{r_{\text{res}}^2} = \pi k = 13.606 \text{ eV/nm}^2 \quad \left(k = \frac{13}{3} \text{ eV/nm}^2\right)")
        
    with col_eq2:
        st.markdown("#### 2. Structural Shielding & Cavity Mapping")
        st.latex(r"V_{\text{eff}} = V_{\text{res}} \cdot \left(\frac{M_o}{M_m}\right), \quad r_{\text{eff}} = \sqrt{\frac{V_{\text{eff}}}{\pi \cdot \lambda}}")
        st.latex(r"\mu = \rho \cdot M_o \cdot \left(\frac{V_{\text{res}}}{V_{\text{eff}}}\right)")
        st.latex(r"\text{HVL [mm]} = \frac{\ln(2)}{\mu} \times 10 = \frac{10 \ln(2)}{\rho \cdot M_o \cdot (V_{\text{res}} / V_{\text{eff}})}")
        
    st.markdown("---")
    st.markdown("#### 3. Spectral Resonance Classification Domains")
    regime_table = pd.DataFrame([
        {"Resonance Regime": "Pre-Resonant Domain", "Wavelength Condition": "λ < λ_c (0.002426 nm)", "Resonant Radius": "r_res > 193.8 nm", "Physical Regime": "Vacuum & Nuclear Pair-Production (> 511 keV)"},
        {"Resonance Regime": "Above-Reference Resonance", "Wavelength Condition": "λ_c < λ < λ_R", "Resonant Radius": "1 nm < r_res < 193.8 nm", "Physical Regime": "Transverse Expansion / Diagnostic & Hard X-Ray"},
        {"Resonance Regime": "Reference Resonance", "Wavelength Condition": "λ = λ_R (91.127 nm)", "Resonant Radius": "r_res = 1.00 nm", "Physical Regime": "Fundamental Geometric Equilibrium (13.606 eV)"},
        {"Resonance Regime": "Below-Reference Resonance", "Wavelength Condition": "λ_R < λ < λ_B", "Resonant Radius": "0.053 nm < r_res < 1 nm", "Physical Regime": "Progressive Atomic-Scale Localization"},
        {"Resonance Regime": "Post-Atomic Resonance Domain", "Wavelength Condition": "λ > λ_B (32.55 μm)", "Resonant Radius": "r_res << 0.053 nm (a_0)", "Physical Regime": "Collective Lattice & Phonon Vibrations (< 38 meV)"}
    ])
    st.dataframe(regime_table, use_container_width=True)

st.markdown("---")
st.caption("© DRVT Quantum-Geometric Structural Shielding Suite | Formulated on Dynamic Resonant Volume Theory (DRVT) by Dr. Khalid Abdel Fattah.")
