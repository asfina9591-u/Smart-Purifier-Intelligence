# 90-Second Demo Video Script
**Competition:** atomQUEST 2026 (Atomberg Technologies)  
**Track:** Track 2 — Water Purifier  
**Area:** Prognostics of Filter Failure Using Data Analytics  
**Submission:** Round 2 Video Pitch  
**Target Duration:** Exactly 90 Seconds (1 min 30 sec)  
**Tone:** Confident, crisp, engineering-driven, transparent  

---

### Timing Breakdown at a Glance

| Time Range | Duration | Section | Key Visual Focus |
| :--- | :--- | :--- | :--- |
| **00:00 – 00:12** | 12s | Team Details & Topic Intro | Dashboard title banner & Team metadata |
| **00:12 – 00:26** | 14s | The Problem | Current industry fixed-timer failure modes |
| **00:26 – 00:42** | 16s | How We Solve It | Live Monitor telemetry & SHAP attribution |
| **00:42 – 01:04** | 22s | Live Demo: What-If Slider | Dragging slider 15 L → 30 L; RUL vs Age curve |
| **01:04 – 01:17** | 13s | Safety Guardrail Status | Triggering "Check data / verify filter" |
| **01:17 – 01:30** | 13s | What is Done, Pending & Close | Validation metrics (7.5d MAE) & Round 3 next steps |

---

### Detailed Scene-by-Scene Script

#### Scene 1: Team & Topic Introduction (00:00 – 00:12 | 12 Seconds)
* **On-Screen Action:**
  * Open browser to Streamlit Dashboard at `http://localhost:8501`.
  * Highlight dashboard title: **"💧 Smart Purifier Intelligence"**.
  * Mouse cursor briefly points to top banner and team credentials overlay.
* **Speaker Narration:**
  > *"Hello Atomberg team! We are team **[TeamName]** from **[CollegeName]**, presenting our Round 2 submission for atomQUEST Track 2: Prognostics of Water Purifier Filter Failure using Data Analytics. This is a 100% software-based predictive intelligence prototype."*

---

#### Scene 2: Problem Statement (00:12 – 00:26 | 14 Seconds)
* **On-Screen Action:**
  * Stay on Dashboard header, zoom in slightly on the caption: *"Data is SIMULATED (pipeline validation)"*.
  * Mouse hovers over fixed baseline comparison in Tab 4 or live monitor.
* **Speaker Narration:**
  > *"Conventional purifiers rely on blind calendar timers—like replace every 100 days—ignoring actual water demand and sediment load. This wastes up to 40% of good filter life in low-use homes, while risking severe membrane clogging and bad water quality in high-turbidity regions."*

---

#### Scene 3: How We Solve It (00:26 – 00:42 | 16 Seconds)
* **On-Screen Action:**
  * Click **"📡 Live monitor"** tab.
  * Move the **Day slider** to day 30, showing real-time updates of Health (74%), Failure Risk (🟢 Low), and Remaining Life (60 days ≈ 1365 L).
  * Click **"🔍 Why this prediction?"** tab to reveal the horizontal SHAP feature attribution bar chart.
* **Speaker Narration:**
  > *"We solve this with a multi-task Gradient Boosting architecture. Using seven rolling hydraulic features—including TDS rejection drop, flow decline, and turbidity load—our model predicts continuous health percentage, discrete failure risk, and remaining useful life in days and liters. TreeSHAP explains the exact root cause behind every prediction."*

---

#### Scene 4: Live Interactive Demo — What-If Simulator (00:42 – 01:04 | 22 Seconds)
* **On-Screen Action:**
  * Switch to **"🎛️ What-if simulator"** tab.
  * Show baseline: Daily water use at **15 L/day**, Turbidity **10 NTU**, Age **40 days** (Health: 75%, RUL: 58 days).
  * **Live Drag Action:** Drag the *Daily water use* slider smoothly from **15 L/day up to 30 L/day**.
  * Highlight immediate reactive changes:
    * Health drops by **25 points** (from 75% down to 50%).
    * Failure risk escalates from 🟢 Low to **🟡 Medium**.
    * Remaining life drops by **30 days** (from 58 days down to 28 days).
  * Scroll down to show:
    1. Sensitivity curve: *Predicted RUL vs. Daily Use*.
    2. Degradation trajectory: *Predicted RUL Curve vs. Filter Age*.
* **Speaker Narration:**
  > *"Here in the What-If Simulator, we can stress-test any household scenario live. At a baseline of 15 liters a day, this 40-day-old filter has 58 days left. If consumption doubles to 30 liters a day—watch the cards update instantly: health drops by 25 points, risk jumps to Medium, and remaining life cuts in half to 28 days. The dashboard also graphs the projected life degradation trajectory across the filter's entire lifespan."*

---

#### Scene 5: Safety Guardrail Status — "Check Data / Verify Filter" (01:04 – 01:17 | 13 Seconds)
* **On-Screen Action:**
  * Click back to **"📡 Live monitor"** tab.
  * Click the checkbox: **"Simulate sensor fault"**.
  * Instantly, the metric cards switch to:
    * Failure Risk: **⚠️ Verify**
    * Remaining Life: **-- days** (suppressed)
    * Confidence: **42%**
  * Highlight the prominent amber warning banner:
    * `⚠️ Check data / verify filter — Fail-safe activated: Turbidity (85.0 NTU) outside operational envelope; Confidence (42%) < 60% threshold.`
* **Speaker Narration:**
  > *"Safety is paramount. If sensor readings exceed physical bounds or model confidence falls below 60%, our fail-safe automatically triggers: confident predictions are suppressed, and an amber alert instructs the user to 'Check data / verify filter', avoiding false-positive maintenance dispatches."*

---

#### Scene 6: What is Done, Pending & Round 3 Roadmap (01:17 – 01:30 | 13 Seconds)
* **On-Screen Action:**
  * Click to **"✅ Model validation"** tab.
  * Highlight the real metrics table:
    * **RUL MAE: 7.5 days** vs. linear baseline **27.9 days** (73% error reduction).
    * **State F1: 0.943**.
  * Conclude with clean view of the application.
* **Speaker Narration:**
  > *"In Round 2, our complete simulator, ML models, SHAP explainability, safety checks, and Streamlit dashboard are completed and validated—slashing RUL error from 28 days down to 7.5 days on 65 held-out units. For Round 3, we will add a real-data IoT adapter, a FastAPI REST microservice, and unsupervised anomaly detection. Thank you!"*

---

### Speaker Preparation Checklist

- [ ] **Rehearse with a stopwatch:** Ensure Scene 4 (slider drag) takes ~22 seconds and entire run matches 90s.
- [ ] **Streamlit running locally:** Execute `streamlit run app.py` before recording.
- [ ] **Browser zoom:** Set Chrome/Edge browser zoom to 100% or 110% on 1080p display for maximum legibility.
- [ ] **Microphone audio:** Ensure quiet environment with clear narration audio.
- [ ] **No hardware:** Remember never to show or mention any physical sensors or ESP32 rigs.
