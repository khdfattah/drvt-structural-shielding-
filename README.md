# 🛡️ DRVT Structural Shielding Design Engine

**A Quantum-Geometric Civil & Radiation Protection Platform**

[![Streamlit App](https://streamlit.io)](https://streamlit.app)
[![Theory](https://shields.io)](https://github.com)
[![License: MIT](https://shields.io)](https://opensource.org)

---

## 📖 Overview

The **DRVT Structural Shielding Design Engine** is an interactive computational platform that bridges quantum electrodynamics with civil and radiation protection engineering. Formulated upon **Dynamic Resonant Volume Theory (DRVT)** by **Dr. Khalid Abdel Fattah**, this engine translates macroscopic statistical attenuation coefficients into explicit nanoscale spatial deformations.

Instead of treating radiation shielding as a silent empirical probability, this platform models how the physical interaction cavity inside protective concrete barriers expands, contracts, or collapses across shifting photon energy regimes—from diagnostic X-rays (**100 keV**) and therapeutic gamma beams (**1.25 MeV**) to ultra-high nuclear accelerator fields (**5.00 MeV**).

---

## 🔬 Theoretical Foundation

* **Core Theory:** Dynamic Resonant Volume Theory (DRVT)
* **Author:** **Dr. Khalid Abdel Fattah** (*Merowe Institute of Technology, Merowe University of Technology, Sudan*)
* **Applied Domain:** Quantum-Geometric Approach to Structural Radiation Shielding

### Fundamental Quantum-Geometric Invariants

1. **Fundamental Resonant Volume (\(V_{\text{res}}\)):**
   \[V_{\text{res}} = \frac{2 \lambda_c \cdot \pi r_1^2}{\alpha^2} = 286.398 \text{ nm}^3 \quad (r_1 = 1 \text{ nm})\]

2. **Reference Resonance Wavelength (\(\lambda_R\)):**
   \[\lambda_R = \frac{2 \lambda_c}{\alpha^2} = 91.127 \text{ nm}, \quad \lambda_c = \frac{h}{m_e c} = 0.00242631 \text{ nm}\]

3. **Effective Cavity Volume (\(V_{\text{eff}}\)) & Interaction Radius (\(r_{\text{eff}}\)):**
   \[V_{\text{eff}} = V_{\text{res}} \cdot \left(\frac{M_o}{M_m}\right), \quad r_{\text{eff}} = \sqrt{\frac{V_{\text{eff}}}{\pi \cdot \lambda}}\]

4. **Macroscopic Linear Attenuation (\(\mu\)) & Half-Value Layer (\(\text{HVL}\)):**
   \[\mu = \rho \cdot M_o \cdot \left(\frac{V_{\text{res}}}{V_{\text{eff}}}\right), \quad \text{HVL [mm]} = \frac{\ln(2)}{\mu} \times 10\]

---

## ✨ Key Platform Features

* **🧱 Smart Multi-Layer Composite Wall Calculator:** Design multi-layered structural barriers (combining Steel-Shot, Barite, Magnetite, and Normal Concrete) and compute cumulative attenuation (\(I/I_0\)), total optical depth (\(\mu \cdot x\)), and floor-space footprint savings.
* **📊 Multi-Material Cavity Analysis:** Compare nanoscale cavity contraction and dilation across standard and heavy concretes, visualizing the *"Breathing Geometric Space"* trajectory across operational energy extremes.
* **🌐 Nanoscale Geometry Cross-Section:** Interactive 2D isotropic cross-sectional visualization comparing the target shielding matrix interaction radius (\(r_{\text{eff}}\)) against the universal water baseline (\(r_{\text{res}}\)).
* **📑 BIM & Structural Export Matrix:** One-click CSV export of single-material and composite wall schedules ready for Building Information Modeling (BIM) workflows.
* **📖 DRVT Mathematical Formulation Reference:** Built-in theoretical documentation detailing the five spectral resonance domains from the *Pre-Resonant Domain* (\(\lambda < \lambda_c\)) to the *Post-Atomic Resonance Domain* (\(\lambda > \lambda_B\)).

---

## 🚀 Local Installation & Deployment

### Prerequisites
Ensure you have Python 3.9+ installed on your system.

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd drvt-structural-shielding-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run drvt_shielding_structures.py
   ```

---

## 📦 Repository Structure

```text
├── drvt_shielding_structures.py   # Main Streamlit application & DRVT computational engine
├── requirements.txt               # Python package dependencies
└── README.md                      # Project documentation & theoretical overview
```

---

## 📚 Citation

If you use this software or the underlying quantum-geometric shielding framework in your research or engineering designs, please cite:

> **Abdel Fattah, K.** *Dynamic Resonant Volume Theory (DRVT) & A Quantum-Geometric Approach to Structural Shielding*. Merowe Institute of Technology, Merowe University of Technology, Sudan.

```bibtex
@misc{abdelfattah_drvt_shielding,
  author       = {Abdel Fattah, Khalid},
  title        = {DRVT Structural Shielding Design Engine: A Quantum-Geometric Approach to Concrete Radiation Barriers},
  institution  = {Merowe Institute of Technology, Merowe University of Technology},
  note         = {Formulated on Dynamic Resonant Volume Theory (DRVT)}
}
```

---

## 📄 License

This project is licensed under the MIT License.

