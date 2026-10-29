# 💧 Smart Purifier Intelligence
**atomQUEST 2026 (Atomberg Technologies) · Track 2: Water Purifier**  
**Area:** Prognostics of Filter Failure Using Data Analytics  
**Submission:** Round 2 Software Prototype & Engineering Progress Report  

> ⚠️ **IMPORTANT NOTICE:**  
> This project is a **100% SOFTWARE-ONLY PROTOTYPE**. There is **NO physical hardware**, sensor rig, ESP32, pump, or plumbing built or required. All telemetry is **SIMULATED** using domain-specific membrane degradation physics. All reported metrics represent pipeline validation on simulated test units and are **NOT field performance**.

---

## 📌 Project Overview

Traditional consumer water purifiers rely on static, blind calendar timers (e.g., replace filter every 100 days or 6 months). This ignores actual household consumption and inlet sediment variations, leading to:
1. **Premature disposal:** Wasting 30–50% of serviceable filter life in low-demand homes.
2. **Delayed replacement:** Risking membrane fouling, reduced flow, and unhygienic water delivery under high turbidity.

**Smart Purifier Intelligence** replaces arbitrary timers with an end-to-end data analytics pipeline:
- **Telemetry Simulator:** Synthesizes realistic multi-unit filter lifecycles with variable TDS, turbidity, water demand, Gaussian noise, and stochastic sensor dropouts.
- **Feature Engineering:** Extracts 7 rolling hydraulic features (`rejection_3d`, `flow_drop_3d`, `turb_load`, `cum_litres`, `use_7d`, `turb_7d`, `age_days`).
- **Gradient Boosting Models:**
  - Health State Classifier (Healthy, Watch, Degraded) — **Macro F1: 0.943**
  - Continuous Health % Regressor (100% down to 20% EOL)
  - Remaining Useful Life (RUL) Regressor — **MAE: 7.52 days** (vs. **27.95 days** linear baseline; **73.1% error reduction**)
- **Explainability (TreeSHAP):** Root-cause feature attribution explaining why remaining life is declining.
- **Interactive Dashboard:** Live playback streaming, What-if scenario sandbox with RUL degradation curves, and model validation tables.
- **Fail-Safe Mechanism:** Physical boundary checks and confidence gating (<60%) triggering an explicit *"⚠️ Check data / verify filter"* advisory.

---

## 🚀 Quickstart & Run Instructions

### 1. Prerequisites
- Python 3.10 or 3.11
- Operating System: Windows, macOS, or Linux

### 2. Environment Setup
Clone or navigate to the project directory:
```bash
cd Smart-Purifier-Intelligence
```

Create and activate a virtual environment:
```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```
*(Optional dependencies for report & screenshot regeneration: `pip install reportlab playwright` followed by `playwright install chromium`)*

### 3. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🎛️ Dashboard Walkthrough

1. **📡 Live Monitor:**
   - Select any held-out purifier unit (never seen during training).
   - Scrub the **Day** slider to observe real-time health %, failure risk, RUL (days & liters), and confidence.
   - Click **"▶ Stream live data"** for real-time telemetry playback.
   - Check **"Simulate sensor fault"** to test the safety fail-safe mechanism live.
2. **🔍 Why this prediction?:**
   - Inspect the TreeSHAP horizontal bar chart quantifying which operational parameters drove the health degradation for the selected day.
3. **🎛️ What-if Simulator:**
   - Adjust **Daily water use (5–40 L/day)**, **Inlet turbidity (1–50 NTU)**, and **Filter age (0–150 days)**.
   - Observe live metric deltas against baseline (15 L / 10 NTU).
   - View two interactive curves:
     - *Predicted RUL vs. Daily Usage*
     - *Predicted RUL Degradation Trajectory vs. Filter Age*
4. **✅ Model Validation:**
   - Review held-out validation metrics evaluated across 65 unseen filter units (5,732 daily records) strictly partitioned by Unit ID.

---

## 🛡️ Safety & Fail-Safe Verification

The prototype includes a two-tiered safety verification check:
- **Physical boundary check:** Validates that TDS rejection [0.25, 1.05], flow drop [-0.20, 0.95], turbidity [0, 60 NTU], and water use [1, 55 L/d] are physically plausible.
- **Confidence gating:** Validates that model classification probability is $\ge 60\%$.

**How to test:**
- In the **Live monitor** tab, toggle the **"Simulate sensor fault"** checkbox.
- The UI immediately suppresses confident RUL and displays:
  > `⚠️ Check data / verify filter — Fail-safe activated: Turbidity (85.0 NTU) outside operational envelope; Confidence (42%) < 60% threshold.`

---

## 📊 Measured Validation Metrics (`metrics.json`)

All metrics are automatically evaluated on the held-out test split (65 unseen units, 5,732 daily cycles) and written to `metrics.json`:

| Metric | Measured Value | Baseline Comparison |
| :--- | :--- | :--- |
| **State Classification F1 (Macro)** | **0.943** (94.3%) | Robust 3-class discrimination |
| **Degraded-State F1 Score** | **0.936** (93.6%) | High recall on critical failure state |
| **RUL MAE: Trained Model** | **7.52 days** | **73.1% error reduction vs. linear** |
| **RUL MAE: Linear-Trend Baseline** | 27.95 days | Simple linear regression on age |
| **RUL MAE: Fixed 100-Day Baseline**| 27.28 days | Industry standard fixed timer |
| **Test Set Size** | 65 units / 5,732 rows | Split strictly by Unit ID |

---

## 📁 Repository Structure

```
Smart-Purifier-Intelligence/
├── app.py                     # Streamlit web application & ML pipeline
├── requirements.txt           # Core Python dependencies
├── metrics.json               # Real validation metrics recorded from app
├── capture_screenshots.py     # Playwright automated screenshot script
├── generate_pdf.py            # ReportLab progress report PDF generator
├── atomQUEST2026_[TeamName]_[CollegeName]_Track2_Report.pdf  # 8-page Round 2 report
├── video_script.md            # 90-second timed demo video script
├── README.md                  # Run instructions & project documentation
└── screenshots/               # High-resolution screenshots of dashboard
    ├── 01_live_monitor.png
    ├── 02_safety_check_triggered.png
    ├── 03_why_this_prediction.png
    ├── 04_what_if_15L.png
    ├── 05_what_if_30L.png
    └── 06_model_validation.png
```

---

## 🛠️ Automated Scripts

- **Capture Screenshots:**  
  `python capture_screenshots.py` (Captures all 6 views into `./screenshots/`)
- **Regenerate PDF Report:**  
  `python generate_pdf.py` (Compiles the 8-page PDF report with embedded screenshots and `metrics.json` values)

  
# 💧 Smart Purifier Intelligence

[🚀 **Launch Live App**](https://smart-purifier-intelligence.streamlit.app/)

An AI-based filter failure prognostics dashboard built with Streamlit and machine learning. This software-only prototype uses simulated purifier telemetry for pipeline validation, not real-world field performance.

---

