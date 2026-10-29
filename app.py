"""Smart Purifier Intelligence - software-only prototype (Streamlit).
Run:  pip install -r requirements.txt   then   streamlit run app.py
Pipeline: telemetry simulator -> features -> health state / health % / RUL models -> SHAP -> dashboard + what-if.
All numbers come from SIMULATED data (pipeline validation, not field performance)."""
import time
import numpy as np, pandas as pd, streamlit as st
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import f1_score, mean_absolute_error
from sklearn.model_selection import GroupShuffleSplit

FEATS = ["rejection_3d", "flow_drop_3d", "turb_load", "cum_litres", "use_7d", "turb_7d", "age_days"]
NICE = {"rejection_3d": "TDS rejection", "flow_drop_3d": "Flow drop", "turb_load": "Turbidity load",
        "cum_litres": "Cumulative litres", "use_7d": "Daily consumption", "turb_7d": "Recent turbidity", "age_days": "Filter age"}
RISK = ["Low", "Medium", "High"]; ICON = ["🟢", "🟡", "🔴"]
EOL_HEALTH = 0.2   # filter counted as end-of-life below 20% health (simulator assumption)

# ---------------- 1. Telemetry simulator ----------------
def simulate_unit(params, noise, rng, uid=0, max_days=320):
    tds_base, turb_m, use_m, wear = params
    rows, turb_load, cum = [], 0.0, 0.0
    for d in range(max_days):
        use = max(2.0, rng.normal(use_m, 3)) if noise else use_m
        turb = max(0.5, rng.normal(turb_m, 2)) if noise else turb_m
        cum += use; turb_load += turb * use
        health = float(np.clip(1 - wear * (turb_load / 60000 + cum / 6000 + d / 500), 0, 1))
        n = (lambda s: rng.normal(0, s)) if noise else (lambda s: 0.0)
        rows.append(dict(unit=uid, age_days=d, use=use, turb=turb, tds_in=tds_base + n(12),
                         rejection=float(np.clip(0.95 - 0.30 * (1 - health) + n(0.02), 0.3, 0.99)),
                         flow=0.4 + 0.6 * health + n(0.03), turb_load=turb_load, cum_litres=cum, health=health))
        if health <= EOL_HEALTH: break
    df = pd.DataFrame(rows)
    if noise:                                   # missing readings
        df.loc[rng.random(len(df)) < 0.03, "flow"] = np.nan
        df["flow"] = df["flow"].ffill().bfill()
    df["rul"] = (len(df) - 1) - df["age_days"]
    return df

def add_features(df):
    g = df.groupby("unit")
    df = df.copy()
    df["flow_drop"] = 1 - df["flow"] / g["flow"].transform(lambda s: s.iloc[:5].mean())
    df["rejection_3d"] = g["rejection"].transform(lambda s: s.rolling(3, min_periods=1).mean())
    df["flow_drop_3d"] = df.groupby("unit")["flow_drop"].transform(lambda s: s.rolling(3, min_periods=1).mean())
    df["use_7d"] = g["use"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df["turb_7d"] = g["turb"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df["state"] = np.select([df["health"] <= 0.35, df["health"] <= 0.60], [2, 1], 0)   # 0 healthy, 1 watch, 2 degraded
    return df

# ---------------- 2. Train models (cached) ----------------
@st.cache_resource(show_spinner="Training models on simulated filter life-cycles (first run only)...")
def train():
    import json, os, shap
    rng = np.random.default_rng(7)
    frames = [simulate_unit((rng.uniform(250, 600), rng.uniform(2, 25), rng.uniform(8, 30), rng.uniform(0.7, 1.4)), True, rng, u)
              for u in range(260)]
    df = add_features(pd.concat(frames, ignore_index=True))
    tr, te = next(GroupShuffleSplit(test_size=0.25, random_state=0).split(df, groups=df["unit"]))   # split BY UNIT
    dtr, dte = df.iloc[tr], df.iloc[te].copy()
    kw = dict(n_estimators=120, max_depth=3, subsample=0.6, random_state=0)
    clf = GradientBoostingClassifier(**kw).fit(dtr[FEATS], dtr["state"])
    hreg = GradientBoostingRegressor(**kw).fit(dtr[FEATS], dtr["health"])
    rreg = GradientBoostingRegressor(**kw).fit(dtr[FEATS], dtr["rul"])
    proba = clf.predict_proba(dte[FEATS])
    dte["pred_state"] = proba.argmax(1); dte["conf"] = proba.max(1)
    dte["pred_health"] = hreg.predict(dte[FEATS]).clip(0, 1); dte["pred_rul"] = rreg.predict(dte[FEATS]).clip(0)
    lin = LinearRegression().fit(dtr[["age_days"]], dtr["rul"])
    m = dict(
        f1_macro=float(f1_score(dte["state"], dte["pred_state"], average="macro")),
        f1_degraded=float(f1_score(dte["state"] == 2, dte["pred_state"] == 2)),
        mae_model=float(mean_absolute_error(dte["rul"], dte["pred_rul"])),
        mae_linear=float(mean_absolute_error(dte["rul"], lin.predict(dte[["age_days"]]).clip(0))),
        mae_fixed=float(mean_absolute_error(dte["rul"], (100 - dte["age_days"]).clip(0))),
        n_units=int(dte["unit"].nunique()), n_rows=int(len(dte)))
    metrics_file = os.path.join(os.path.dirname(__file__), "metrics.json") if "__file__" in globals() else "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(m, f, indent=2)
    return dict(clf=clf, hreg=hreg, rreg=rreg, expl=shap.TreeExplainer(rreg), test=dte, metrics=m)

def predict_row(B, X):
    p = B["clf"].predict_proba(X)[0]
    return dict(state=int(p.argmax()), conf=float(p.max()), health=float(np.clip(B["hreg"].predict(X)[0], 0, 1)),
                rul=float(max(B["rreg"].predict(X)[0], 0)))

def scenario(B, use, turb, age):
    df = add_features(simulate_unit((400, turb, use, 1.0), False, None))
    row = df.iloc[[min(age, len(df) - 1)]]
    return predict_row(B, row[FEATS]), row

def check_safety(row, conf):
    """Data-validation safety check: verifies inputs are in range and model confidence >= 60%."""
    flags = []
    if "rejection_3d" in row and not (0.25 <= row["rejection_3d"] <= 1.05):
        flags.append(f"TDS rejection ({row['rejection_3d']:.2f}) outside physical bounds [0.25, 1.0]")
    if "flow_drop_3d" in row and not (-0.20 <= row["flow_drop_3d"] <= 0.95):
        flags.append(f"Flow drop ({row['flow_drop_3d']:.2f}) outside expected range")
    if "turb_7d" in row and not (0.0 <= row["turb_7d"] <= 60.0):
        flags.append(f"Turbidity ({row['turb_7d']:.1f} NTU) outside operational envelope")
    if "use_7d" in row and not (1.0 <= row["use_7d"] <= 55.0):
        flags.append(f"Water usage ({row['use_7d']:.1f} L/d) outside domestic bounds")
    if conf is not None and conf < 0.60:
        flags.append(f"Confidence ({conf * 100:.0f}%) < 60% threshold")
    return (len(flags) == 0), flags

# ---------------- 3. Dashboard ----------------
st.set_page_config(page_title="Smart Purifier Intelligence", page_icon="💧", layout="wide")
st.title("💧 Smart Purifier Intelligence")
st.caption("AI-based filter failure prognostics · software-only prototype · data is SIMULATED (pipeline validation, not field performance)")
B = train(); T = B["test"]

SIM_BADGE_HTML = """
<div style="display:inline-flex; align-items:center; background-color:#fff3cd; color:#856404; padding:4px 12px; border-radius:12px; font-size:0.83rem; font-weight:600; border:1px solid #ffeeba; margin-bottom:12px;">
    🧪 SIMULATED DATA — Pipeline Validation Only
</div>
"""

tab1, tab2, tab3, tab4 = st.tabs(["📡 Live monitor", "🔍 Why this prediction?", "🎛️ What-if simulator", "✅ Model validation"])

def show(dfu, d):
    r = dfu.iloc[d]; s = int(r["pred_state"]); conf = float(r["conf"])
    is_safe, reasons = check_safety(r, conf)
    c = st.columns(4)
    if not is_safe:
        c[0].metric("Filter health", f"{r['pred_health'] * 100:.0f}%")
        c[1].metric("Failure risk", "⚠️ Verify")
        c[2].metric("Remaining life", "-- days", delta_color="off")
        c[3].metric("Confidence", f"{conf * 100:.0f}%")
        st.warning(f"⚠️ **Check data / verify filter** — Fail-safe activated: {'; '.join(reasons)}. Prediction suppressed to avoid unverified maintenance action.")
    else:
        c[0].metric("Filter health", f"{r['pred_health'] * 100:.0f}%")
        c[1].metric("Failure risk", f"{ICON[s]} {RISK[s]}")
        c[2].metric("Remaining life", f"{r['pred_rul']:.0f} days", f"≈ {r['pred_rul'] * r['use_7d']:.0f} L", delta_color="off")
        c[3].metric("Confidence", f"{conf * 100:.0f}%")
        if s == 2: st.error("Degradation detected: plan filter replacement")
        elif s == 1: st.warning("Degradation trend detected")
        else: st.success("Filter healthy")
    h = dfu.iloc[: d + 1]
    st.line_chart(pd.DataFrame({"Predicted health %": h["pred_health"].values * 100,
                                "Actual health % (simulator)": h["health"].values * 100}, index=h["age_days"].values))

with tab1:
    st.markdown(SIM_BADGE_HTML, unsafe_allow_html=True)
    units = sorted(T["unit"].unique())
    unit = st.selectbox("Purifier unit (held-out, never seen in training)", units, key="unit")
    dfu = T[T["unit"] == unit].reset_index(drop=True)
    c_sl1, c_sl2 = st.columns([3, 1])
    day = c_sl1.slider("Day", 0, len(dfu) - 1, min(30, len(dfu) - 1), key="day")
    test_fault = c_sl2.checkbox("Simulate sensor fault", help="Inject out-of-bounds readings to test safety check")
    if test_fault:
        dfu = dfu.copy()
        dfu.loc[day, "conf"] = 0.42
        dfu.loc[day, "turb_7d"] = 85.0
    box = st.empty()
    if st.button("▶ Stream live data"):
        for d in range(0, len(dfu), 2):
            with box.container(): show(dfu, d)
            time.sleep(0.12)
    else:
        with box.container(): show(dfu, day)

with tab2:
    st.markdown(SIM_BADGE_HTML, unsafe_allow_html=True)
    st.subheader("Why is the remaining life changing?")
    dfu = T[T["unit"] == st.session_state.get("unit", T["unit"].iloc[0])].reset_index(drop=True)
    d = min(st.session_state.get("day", 30), len(dfu) - 1)
    X = dfu.iloc[[d]][FEATS]
    sv = np.abs(B["expl"].shap_values(X)[0]); share = sv / sv.sum() * 100
    st.bar_chart(pd.Series(share, index=[NICE[f] for f in FEATS]).sort_values(ascending=False), horizontal=True)
    st.caption("SHAP contribution share for the selected unit and day (Live monitor tab).")

with tab3:
    st.markdown(SIM_BADGE_HTML, unsafe_allow_html=True)
    st.subheader("What happens if conditions change?")
    c1, c2, c3 = st.columns(3)
    use = c1.slider("Daily water use (L/day)", 5, 40, 15)
    turb = c2.slider("Inlet turbidity (NTU)", 1, 50, 10)
    age = c3.slider("Filter age (days)", 0, 150, 40)
    now, _ = scenario(B, use, turb, age); ref, _ = scenario(B, 15, 10, age)
    conf = now["conf"]
    whatif_valid = (5 <= use <= 40) and (1 <= turb <= 50) and (0 <= age <= 150)
    if not whatif_valid or conf < 0.60:
        st.warning(f"⚠️ **Check data / verify filter**: Low confidence ({conf * 100:.0f}%) or parameters outside operating envelope.")
        k = st.columns(3)
        k[0].metric("Filter health", f"{now['health'] * 100:.0f}%")
        k[1].metric("Failure risk", "⚠️ Verify")
        k[2].metric("Remaining life", "-- days")
    else:
        k = st.columns(3)
        k[0].metric("Filter health", f"{now['health'] * 100:.0f}%", f"{(now['health'] - ref['health']) * 100:+.0f} pts vs 15 L / 10 NTU")
        k[1].metric("Failure risk", f"{ICON[now['state']]} {RISK[now['state']]}")
        k[2].metric("Remaining life", f"{now['rul']:.0f} days", f"{now['rul'] - ref['rul']:+.0f} days vs 15 L / 10 NTU")
    st.markdown("##### 💧 Sensitivity: Predicted RUL vs. Daily Water Usage")
    sweep_use = pd.Series({u: scenario(B, u, turb, age)[0]["rul"] for u in range(8, 41, 4)}, name="Predicted RUL (days)")
    st.line_chart(sweep_use.rename_axis("Daily use (L)"))
    st.markdown(f"##### ⏳ Predicted RUL Curve vs. Filter Age ({use} L/day, {turb} NTU)")
    df_sim = add_features(simulate_unit((400, turb, use, 1.0), False, None))
    max_sim_age = len(df_sim)
    age_steps = sorted(list(set(list(range(0, max_sim_age, max(1, max_sim_age // 25))) + [max_sim_age - 1])))
    sweep_age = pd.Series({a: predict_row(B, df_sim.iloc[[a]][FEATS])["rul"] for a in age_steps}, name="Predicted RUL (days)")
    st.line_chart(sweep_age.rename_axis("Filter age (days)"))

with tab4:
    st.markdown(SIM_BADGE_HTML, unsafe_allow_html=True)
    m = B["metrics"]
    st.subheader("Held-out validation (simulated data)")
    st.write(f"Test = {m['n_units']} complete filter units never seen in training ({m['n_rows']} daily readings). Split is **by unit**, not by row.")
    st.table(pd.DataFrame({
        "Metric": ["State classification F1 (macro)", "Degraded-state F1", "RUL MAE: model (days)", "RUL MAE: linear-trend baseline", "RUL MAE: fixed 100-day interval"],
        "Value": [f"{m['f1_macro']:.3f}", f"{m['f1_degraded']:.3f}", f"{m['mae_model']:.1f}", f"{m['mae_linear']:.1f}", f"{m['mae_fixed']:.1f}"]}))
    st.info("These numbers validate the pipeline on simulated data only. Do not present them as real-world performance.")