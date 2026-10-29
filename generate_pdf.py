import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# =====================================================================
# EDIT ONLY THIS BLOCK
# =====================================================================
TEAM_NAME = "CodeAlpha"            # <-- put your REAL registered team name here
COLLEGE_NAME = "Alliance University"
MEMBERS = [
    "Asfina M (Team Leader)",
    "Dhanush",
    "Laxmi",
    "Yashas",
    "Aman",
]
AMOUNT_SPENT = "0"                    # <-- actual amount spent in rupees (0 if nothing)
REPORT_DATE = "29 October 2026"
# =====================================================================

FILE_TEAM = TEAM_NAME.replace(" ", "")
FILE_COLLEGE = COLLEGE_NAME.replace(" ", "")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        if self._pageNumber == 1:
            return  # Suppress running header/footer on cover
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#134074"))
        self.drawString(54, 752, "atomQUEST 2026 | Track 2: Water Purifier")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        self.drawRightString(612 - 54, 752, "Prognostics of Filter Failure · Round 2 Report")

        # Header rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 745, 612 - 54, 745)

        # Footer rule
        self.line(54, 45, 612 - 54, 45)
        self.setFont("Helvetica", 7.5)
        self.drawString(54, 32, "Software-Only Prototype · Data is SIMULATED · Numbers from metrics.json")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


def build_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    metrics_path = os.path.join(base_dir, "metrics.json")
    with open(metrics_path, "r") as f:
        m = json.load(f)

    # Dynamically compute derived metrics from metrics.json
    f1_macro = m["f1_macro"]
    f1_degraded = m["f1_degraded"]
    mae_model = m["mae_model"]
    mae_linear = m["mae_linear"]
    mae_fixed = m["mae_fixed"]
    n_units = m["n_units"]
    n_rows = m["n_rows"]

    err_reduc_linear = (1.0 - (mae_model / mae_linear)) * 100
    err_reduc_fixed = (1.0 - (mae_model / mae_fixed)) * 100

    # Compute scenario values directly from app module for exact caption agreement
    import app
    B = app.train()
    s15, _ = app.scenario(B, 15, 10, 40)
    s30, _ = app.scenario(B, 30, 10, 40)

    # Values for captions
    s15_health_pct = round(s15['health'] * 100)
    s15_rul_days = round(s15['rul'])
    s30_health_pct = round(s30['health'] * 100)
    s30_rul_days = round(s30['rul'])
    s30_health_diff = s30_health_pct - s15_health_pct
    s30_rul_diff = s30_rul_days - s15_rul_days

    pdf_filename = f"atomQUEST2026_{FILE_TEAM}_{FILE_COLLEGE}_Track2_Report.pdf"
    pdf_path = os.path.join(base_dir, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom color palette
    c_primary = colors.HexColor("#0B2545")
    c_secondary = colors.HexColor("#134074")
    c_accent = colors.HexColor("#0077B6")
    c_dark = colors.HexColor("#1E293B")
    c_light_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")
    c_amber_bg = colors.HexColor("#FEF3C7")
    c_amber_border = colors.HexColor("#F59E0B")
    c_amber_text = colors.HexColor("#92400E")

    # Typography Styles
    title_style = ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=c_primary, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle("CoverSubtitle", fontName="Helvetica", fontSize=12, leading=16, textColor=c_accent, alignment=TA_CENTER)
    h1_style = ParagraphStyle("Heading1_Custom", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=c_secondary, spaceBefore=10, spaceAfter=5, keepWithNext=True)
    h2_style = ParagraphStyle("Heading2_Custom", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=c_accent, spaceBefore=6, spaceAfter=3, keepWithNext=True)
    body_style = ParagraphStyle("Body_Custom", fontName="Helvetica", fontSize=9, leading=13, textColor=c_dark, alignment=TA_LEFT, spaceAfter=5)
    bullet_style = ParagraphStyle("Bullet_Custom", fontName="Helvetica", fontSize=8.8, leading=12.5, textColor=c_dark, leftIndent=12, spaceAfter=3)
    table_cell = ParagraphStyle("TableCell", fontName="Helvetica", fontSize=8.2, leading=11, textColor=c_dark)
    table_cell_bold = ParagraphStyle("TableCellBold", fontName="Helvetica-Bold", fontSize=8.2, leading=11, textColor=c_dark)
    table_cell_hdr = ParagraphStyle("TableCellHdr", fontName="Helvetica-Bold", fontSize=8.2, leading=11, textColor=colors.white)
    caption_style = ParagraphStyle("CaptionStyle", fontName="Helvetica-Oblique", fontSize=7.8, leading=10, textColor=colors.HexColor("#64748B"), alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)

    story = []

    # ------------------ PAGE 1: COVER PAGE ------------------
    story.append(Spacer(1, 25))
    sim_badge = Table(
        [[Paragraph("<b>[SIMULATED DATA] SOFTWARE-ONLY PROTOTYPE · ALGORITHM VALIDATION PIPELINE</b>", ParagraphStyle("HdrBadge", fontName="Helvetica-Bold", fontSize=8.5, textColor=c_amber_text, alignment=TA_CENTER))]],
        colWidths=[490]
    )
    sim_badge.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_amber_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_amber_border),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sim_badge)
    story.append(Spacer(1, 20))

    story.append(Paragraph("atomQUEST 2026", ParagraphStyle("AQC", fontName="Helvetica-Bold", fontSize=14, leading=16, textColor=c_accent, alignment=TA_CENTER)))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Atomberg product-based challenge", ParagraphStyle("AQOrg", fontName="Helvetica", fontSize=11, leading=14, textColor=c_secondary, alignment=TA_CENTER)))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Smart Purifier Intelligence:<br/>Prognostics of Filter Failure Using Data Analytics", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Round 2 Progress Report & Engineering Submission", subtitle_style))
    story.append(Spacer(1, 20))

    members_html = "<br/>".join(MEMBERS)
    meta_data = [
        [Paragraph("<b>Track</b>", table_cell_bold), Paragraph("Track 2: Water Purifier", table_cell)],
        [Paragraph("<b>Area of Exploration</b>", table_cell_bold), Paragraph("Prognostics of filter failure using data analytics", table_cell)],
        [Paragraph("<b>Team Name</b>", table_cell_bold), Paragraph(f"<b>{TEAM_NAME}</b>", table_cell_bold)],
        [Paragraph("<b>College / Institution</b>", table_cell_bold), Paragraph(f"<b>{COLLEGE_NAME}</b>", table_cell_bold)],
        [Paragraph("<b>Team Members</b>", table_cell_bold), Paragraph(members_html, table_cell)],
        [Paragraph("<b>Prototype Nature</b>", table_cell_bold), Paragraph("100% Software-only (Streamlit ML Analytics Dashboard; No physical hardware/rig)", table_cell)],
        [Paragraph("<b>Report Date</b>", table_cell_bold), Paragraph(f"{REPORT_DATE} (Submission Deadline: 4 Nov 2026)", table_cell)],
    ]
    t_meta = Table(meta_data, colWidths=[140, 350])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))

    exec_text = (
        f"<b>Executive Summary:</b> In Round 2 of atomQUEST 2026, our student team has completed and validated "
        f"an end-to-end machine learning prognostic pipeline for domestic water purifier filter life prediction. "
        f"By replacing static calendar timers with telemetry-driven gradient-boosted health estimation and RUL "
        f"regression, the system achieves a <b>{err_reduc_linear:.1f}% error reduction</b> in filter replacement scheduling over linear baselines. "
        f"All telemetry in this prototype is synthetically generated to model physical degradation dynamics; all metrics reported "
        f"represent held-out validation on {n_units} unseen simulated purifier units ({n_rows:,} daily cycles), recorded in <code>metrics.json</code>. "
        f"This submission is strictly software-based."
    )
    t_exec = Table([[Paragraph(exec_text, body_style)]], colWidths=[490])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_exec)
    story.append(PageBreak())

    # ------------------ PAGE 2: PROBLEM & ARCHITECTURE ------------------
    story.append(Paragraph("1. Problem Identified and How We Solve It", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    p1 = (
        "<b>1.1 The Operational Problem in Modern Purifiers:</b> Modern consumer water purifiers rely predominantly on crude, "
        "open-loop replacement mechanisms: either a fixed calendar interval (e.g., replace filter every 100 days or 6 months) "
        "or an unmonitored failure mode where the user only notices a problem when clean water flow drops to a trickle, "
        "water tastes saline due to TDS breakthrough, or bacterial breakthrough occurs. In practice, filter degradation is driven "
        "by cumulative throughput volume (L), particulate and sediment loading (inlet turbidity NTU), feed-water salinity (TDS ppm), "
        "and mechanical fouling rate. Static calendar intervals do not account for variable household consumption or seasonal inlet "
        "water quality, leading to premature filter replacements in low-use households or delayed replacements during heavy sediment loads."
    )
    story.append(Paragraph(p1, body_style))

    p2 = (
        "<b>1.2 Our Data Analytics Solution:</b> We approach filter prognostics as a multi-task learning challenge leveraging real-time "
        "telemetry analytics without introducing expensive hardware modifications. Our software pipeline ingests operational telemetry, "
        "computes rolling hydraulic and rejection degradation features, and feeds them into coordinated Gradient Boosting models:<br/>"
        "• <b>Health-State Classifier (3 Classes):</b> Categorizes condition into Healthy (0), Watch / Degrading (1), and Degraded (2).<br/>"
        "• <b>Continuous Health % Regressor:</b> Estimates a continuous health score from 100% (fresh) down to 20% (end-of-life cutoff).<br/>"
        "• <b>Remaining Useful Life (RUL) Regressor:</b> Direct point prediction of remaining operating days under current wear dynamics, "
        "also translated to remaining liters based on 7-day average household demand.<br/>"
        "• <b>Explainability Engine:</b> TreeSHAP feature-attribution reveals exactly which operational factor is driving degradation.<br/>"
        "• <b>Fail-Safe Safety Guardrail:</b> A real-time data validator checks sensor bounds and prediction confidence (&lt;60%), immediately "
        "issuing a 'Check data / verify filter' advisory rather than hallucinating an ungrounded prediction."
    )
    story.append(Paragraph(p2, body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Modules Completed So Far (Architecture & Implementation)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>Module 2.1 — Telemetry Simulator:</b> Implements realistic synthetic filter lifecycles. "
                           "Each simulated unit is initialized with distinct physical parameters: baseline TDS (250–600 ppm), "
                           "mean inlet turbidity (2–25 NTU), daily household water demand (8–30 L/day), and an individualized wear factor (0.7–1.4). "
                           "Degradation follows coupled membrane physics where health decreases as a joint function of turbidity load, "
                           "cumulative liters, and chronological days. Sensor noise (Gaussian) and 3% missing data dropouts are realistically simulated.", bullet_style))

    story.append(Paragraph("<b>Module 2.2 — Feature Engineering:</b> Seven operational features are extracted across rolling observation windows: "
                           "<code>rejection_3d</code> (3-day rolling mean TDS rejection), <code>flow_drop_3d</code> (3-day rolling flow rate reduction), "
                           "<code>turb_load</code> (cumulative turbidity exposure NTU×L), <code>cum_litres</code> (total water treated), "
                           "<code>use_7d</code> (7-day consumption), <code>turb_7d</code> (7-day feed turbidity), and <code>age_days</code>.", bullet_style))

    story.append(Paragraph(f"<b>Module 2.3 — Machine Learning Prognostic Models:</b> Gradient Boosting architecture (120 trees, max depth 3, "
                           f"subsample 0.6) trained strictly on 195 units and validated on {n_units} completely unseen units via GroupShuffleSplit.", bullet_style))

    story.append(Paragraph("<b>Module 2.4 — SHAP Explainability Engine:</b> Fast TreeExplainer computing Shapley contribution shares "
                           "for every daily observation, turning tree predictions into transparent engineering insights.", bullet_style))

    story.append(Paragraph("<b>Module 2.5 — Interactive Streamlit Dashboard:</b> Responsive 4-tab user interface delivering live telemetry streaming, "
                           "SHAP root-cause inspection, What-if scenario simulation, and model validation tables.", bullet_style))
    story.append(PageBreak())

    # ------------------ PAGE 3: SCREENSHOTS TAB 1 & TAB 2 ------------------
    story.append(Paragraph("2. Modules Completed So Far (Live Monitoring & Explainability)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    img_path1 = os.path.join(base_dir, "screenshots", "01_live_monitor.png")
    if os.path.exists(img_path1):
        story.append(Paragraph("<b>Figure 1: Tab 1 — Live Monitor Dashboard</b>", h2_style))
        story.append(Image(img_path1, width=6.3*inch, height=2.9*inch))
        story.append(Paragraph("Figure 1: Live monitor tab displaying unit telemetry playback, predicted health (74%), failure risk (Low), remaining life (60 days ≈ 1365 L), confidence (100%), and interactive degradation trajectory chart. Prominent 'SIMULATED DATA' badge is visible at top.", caption_style))

    story.append(Spacer(1, 4))

    img_path3 = os.path.join(base_dir, "screenshots", "03_why_this_prediction.png")
    if os.path.exists(img_path3):
        story.append(Paragraph("<b>Figure 2: Tab 2 — Explainability Engine (SHAP Analysis)</b>", h2_style))
        story.append(Image(img_path3, width=6.3*inch, height=2.8*inch))
        story.append(Paragraph("Figure 2: Explainability tab detailing SHAP feature attribution share. TDS rejection degradation, flow drop, and turbidity load dominate the prediction breakdown, ensuring full transparency for service technicians.", caption_style))
    story.append(PageBreak())

    # ------------------ PAGE 4: SCREENSHOTS TAB 3 WHAT-IF ------------------
    story.append(Paragraph("2. Modules Completed So Far (What-If Simulation Scenarios)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    img_path4 = os.path.join(base_dir, "screenshots", "04_what_if_15L.png")
    if os.path.exists(img_path4):
        story.append(Paragraph("<b>Figure 3A: Tab 3 — What-If Simulator (Baseline Demand: 15 L/day, 10 NTU, Age 40d)</b>", h2_style))
        story.append(Image(img_path4, width=6.3*inch, height=2.85*inch))
        story.append(Paragraph(f"Figure 3A: Baseline simulation showing {s15_health_pct}% health, {s15_rul_days} days RUL (Low risk), along with sensitivity curves vs. daily usage and the predicted RUL curve vs. filter age.", caption_style))

    story.append(Spacer(1, 4))

    img_path5 = os.path.join(base_dir, "screenshots", "05_what_if_30L.png")
    if os.path.exists(img_path5):
        story.append(Paragraph("<b>Figure 3B: Tab 3 — What-If Simulator Under Heavy Load (30 L/day, 10 NTU, Age 40d)</b>", h2_style))
        story.append(Image(img_path5, width=6.3*inch, height=2.85*inch))
        story.append(Paragraph(f"Figure 3B: Heavy load simulation showing drop to {s30_health_pct}% health ({s30_health_diff:+d} pts vs baseline), {s30_rul_days} days RUL ({s30_rul_diff:+d} days vs baseline), and elevated failure risk (Medium).", caption_style))
    story.append(PageBreak())

    # ------------------ PAGE 5: VALIDATION & SAFETY SCREENSHOTS ------------------
    story.append(Paragraph("2. Modules Completed So Far (Validation & Fail-Safe Demonstration)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    img_path6 = os.path.join(base_dir, "screenshots", "06_model_validation.png")
    if os.path.exists(img_path6):
        story.append(Paragraph("<b>Figure 4: Tab 4 — Held-Out Model Validation Table</b>", h2_style))
        story.append(Image(img_path6, width=6.3*inch, height=2.85*inch))
        story.append(Paragraph(f"Figure 4: Model validation tab displaying empirical performance across {n_units} held-out filter units ({n_rows:,} daily records) strictly partitioned by unit ID.", caption_style))

    story.append(Spacer(1, 4))

    img_path2 = os.path.join(base_dir, "screenshots", "02_safety_check_triggered.png")
    if os.path.exists(img_path2):
        story.append(Paragraph("<b>Figure 5: Safety Guardrail Triggered ('Check data / verify filter')</b>", h2_style))
        story.append(Image(img_path2, width=6.3*inch, height=2.85*inch))
        story.append(Paragraph("Figure 5: Live monitor safety check triggered by anomalous/out-of-range sensor readings or low confidence (&lt;60%). Confident RUL is suppressed and an amber warning instructs the user/technician to verify data.", caption_style))
    story.append(PageBreak())

    # ------------------ PAGE 6: RISK & COST & CHANGES ------------------
    story.append(Paragraph("3. Status of Sourcing Risk Flagged in Abstract", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    p_risk = (
        "<b>3.1 Risk Flagged in Abstract:</b> In the Round 1 abstract, we flagged that the mathematical telemetry "
        "simulator may not perfectly represent real filter behaviour and that publicly available labelled filter-degradation "
        "datasets with high-frequency operational telemetry are limited.<br/>"
        "<b>3.2 Mitigation Actions Taken in Round 2:</b> To reduce this gap systematically without overclaiming real-world performance:<br/>"
        "• <b>Physics-Informed Wear Formulations:</b> Wear rate was modeled not as simple linear decay, but as a coupled "
        "function of cumulative particulate loading (turbidity × volume), hydraulic throughput (cumulative liters), and chronological "
        "calendar aging. This mirrors known membrane pore blocking and surface cake buildup mechanisms.<br/>"
        "• <b>Population Heterogeneity (260 Distinct Units):</b> Instead of simulating a single 'average' filter, we generated 260 distinct "
        "units where baseline feed TDS spans 250 to 600 ppm, turbidity spans 2 to 25 NTU, water use spans 8 to 30 L/day, and manufacturing "
        "wear susceptibility varies by ±40% (0.7 to 1.4).<br/>"
        "• <b>Realistic Telemetry Noise and Packet Drops:</b> Telemetry is degraded by Gaussian sensor measurement noise and a 3% random "
        "dropout probability on daily flow readings, requiring rolling imputations identical to real IoT ingestion pipelines.<br/>"
        f"• <b>Strict Unit-Level Partitioning:</b> Enforced <code>GroupShuffleSplit</code> strictly grouped by Unit ID ({n_units} units held out). "
        "Zero readings from test units ever enter training, eliminating chronological data leakage.<br/>"
        "• <b>Operational Out-of-Bounds Rejection:</b> Physical boundary filtering immediately flags sensor anomalies before inference."
    )
    story.append(Paragraph(p_risk, body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4. Amount Spent vs. Abstract Estimate", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    cost_data = [
        [Paragraph("<b>Category</b>", table_cell_hdr), Paragraph("<b>Cost (INR)</b>", table_cell_hdr), Paragraph("<b>Remarks</b>", table_cell_hdr)],
        [Paragraph("Abstract Estimate (Total)", table_cell_bold), Paragraph("Rs 0 – 1,000", table_cell), Paragraph("Estimated total ceiling in Round 1 abstract", table_cell)],
        [Paragraph("Actual Spend", table_cell_bold), Paragraph(f"Rs {AMOUNT_SPENT}", table_cell_bold), Paragraph("100% Software-only prototype; zero physical hardware purchased", table_cell)],
    ]
    t_cost = Table(cost_data, colWidths=[160, 110, 210])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cost)
    story.append(Spacer(1, 4))

    story.append(Paragraph("5. Changes Since Abstract", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    p_changes = (
        "Three concrete adjustments were made since the abstract:<br/>"
        "• <b>Change 1: Frontend/Backend Architecture (Streamlit Adoption):</b> The abstract originally proposed a decoupled React.js frontend "
        "and FastAPI backend. Due to time constraints during university examination schedules, we consolidated the stack into a unified "
        "Python Streamlit architecture. This accelerated SHAP integration and allowed complete "
        "focus on prognostic modeling and safety checks.<br/>"
        "• <b>Change 2: Dedicated Anomaly Detection Repositioned as Round 3 Stretch Goal:</b> In the abstract, unsupervised anomaly detection "
        "(via Isolation Forest) was a stretch goal. In Round 2, we prioritized the core prognostic engine "
        "(classification + RUL regression + SHAP) and implemented a physical-range safety validator instead. Dedicated Isolation Forest "
        "anomaly detection is planned for Round 3.<br/>"
        f"• <b>Change 3: Target Metrics Restated Using Real Measured Validation Values:</b> In the abstract, an initial target of "
        f"RUL MAE &le; 7 days was set. On held-out validation across {n_units} unseen units ({n_rows:,} daily readings), the measured RUL MAE is "
        f"<b>{mae_model:.2f} days</b>. Therefore, the initial target of &le; 7 days was <b>not met</b>. However, this represents "
        f"a <b>{err_reduc_linear:.1f}% error reduction</b> compared to the linear-trend baseline ({mae_linear:.2f} days) and "
        f"<b>{err_reduc_fixed:.1f}% error reduction</b> compared to the fixed 100-day interval baseline ({mae_fixed:.2f} days). All metrics are "
        f"measured on the held-out test split and saved in <code>metrics.json</code>:"
    )
    story.append(Paragraph(p_changes, body_style))
    story.append(PageBreak())

    # ------------------ PAGE 7: METRICS & SAFETY ------------------
    story.append(Paragraph("5. Changes Since Abstract (Measured Metrics vs. Baselines)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    metrics_table_data = [
        [Paragraph("<b>Validation Metric</b>", table_cell_hdr), Paragraph("<b>Measured Value (Simulated Data)</b>", table_cell_hdr), Paragraph("<b>Baseline Comparison / Significance</b>", table_cell_hdr)],
        [Paragraph("State Classification F1 (Macro)", table_cell_bold), Paragraph(f"<b>{f1_macro:.3f}</b> ({f1_macro*100:.1f}%)", table_cell), Paragraph("Discrimination across Healthy, Watch, and Degraded", table_cell)],
        [Paragraph("Degraded-State F1 Score", table_cell_bold), Paragraph(f"<b>{f1_degraded:.3f}</b> ({f1_degraded*100:.1f}%)", table_cell), Paragraph("Detection of the critical end-of-life state", table_cell)],
        [Paragraph("RUL MAE: Trained Model", table_cell_bold), Paragraph(f"<b>{mae_model:.2f} days</b> (target &le;7d not met)", table_cell_bold), Paragraph(f"<b>{err_reduc_linear:.1f}% error reduction vs linear baseline</b>", table_cell_bold)],
        [Paragraph("RUL MAE: Linear-Trend Baseline", table_cell), Paragraph(f"{mae_linear:.2f} days", table_cell), Paragraph("Simple linear regression on filter age", table_cell)],
        [Paragraph("RUL MAE: Fixed 100-Day Baseline", table_cell), Paragraph(f"{mae_fixed:.2f} days", table_cell), Paragraph("Fixed replacement interval", table_cell)],
        [Paragraph("Held-out Test Units / Readings", table_cell), Paragraph(f"{n_units} units / {n_rows:,} days", table_cell), Paragraph("Split strictly by Unit ID (no data leakage)", table_cell)],
    ]
    t_metrics = Table(metrics_table_data, colWidths=[150, 140, 195])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    story.append(Paragraph("6. Status of Safety / Fail-Safe Mechanism", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    p_safety = (
        "<b>6.1 Fail-Safe Architecture:</b> A false-confident prediction during a sensor malfunction is "
        "more harmful than no prediction at all. We introduced a two-tiered safety verification layer (<code>check_safety</code> in <code>app.py</code>):<br/>"
        "• <b>Tier 1: Physical Boundary Envelope:</b> Ingested readings are verified against plausible purifier limits: "
        "TDS rejection in [0.25, 1.05], flow drop in [-0.20, 0.95], turbidity in [0.0, 60.0] NTU, daily consumption in [1.0, 55.0] L/day, "
        "and age in [0, 365] days. Any reading breaching these thresholds triggers a boundary violation flag.<br/>"
        "• <b>Tier 2: Algorithmic Confidence Gating:</b> The maximum predicted class probability from the Gradient Boosting classifier "
        "(<code>conf = max(P(state))</code>) must equal or exceed <b>60%</b>. If prediction uncertainty is high (conf &lt; 0.60), "
        "the prediction is withheld.<br/><br/>"
        "<b>6.2 Fail-Safe Response:</b> When either tier fails, the UI suppresses the confident RUL and health metrics, displays failure risk as "
        "<i>'Verify'</i>, and shows an amber advisory:<br/>"
        "<code>'Check data / verify filter — Fail-safe activated: [reasons]. Prediction suppressed to avoid unverified maintenance action.'</code><br/>"
        "A dashboard checkbox (<i>'Simulate sensor fault'</i>) lets testers trigger this fail-safe behavior live."
    )
    story.append(Paragraph(p_safety, body_style))
    story.append(PageBreak())

    # ------------------ PAGE 8: NEXT STEPS & LIMITATIONS ------------------
    story.append(Paragraph("7. Planned Next Steps for Round 3", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    p_next = (
        "Heading into the final round, our roadmap focuses on hardening the software pipeline:<br/>"
        "• <b>Step 1 — Real-Data Ingestion Adapter:</b> Develop a schema adapter layer capable of ingesting purifier telemetry "
        "(REST webhooks or CSV/JSON files) with automatic timestamp normalization.<br/>"
        "• <b>Step 2 — Standalone REST API Microservice:</b> Expose FastAPI endpoints (<code>/predict</code>, <code>/explain</code>, <code>/health</code>) "
        "so the prognostic engine can run as a service decoupled from the Streamlit UI.<br/>"
        "• <b>Step 3 — Unsupervised Anomaly Detection (Isolation Forest):</b> Implement the deferred Isolation Forest module on multi-day rolling "
        "rejection/flow windows to detect rapid transient faults distinct from slow filter aging.<br/>"
        "• <b>Step 4 — Robustness Testing Suite:</b> Stress-test the models against synthetic drift (gradual measurement decalibration), "
        "severe noise spikes, and unseen scenarios (e.g., highly saline water &gt; 1500 ppm TDS)."
    )
    story.append(Paragraph(p_next, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("8. Honest Limitations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_secondary, spaceBefore=2, spaceAfter=6))

    p_limit = (
        "We clearly state the following limitations:<br/>"
        "1. <b>Simulated Data Only:</b> All results, metrics, and figures presented in this report and dashboard are derived strictly from "
        "synthetic telemetry generated by our degradation simulator. They validate the <i>pipeline architecture</i>, "
        "feature engineering, and learning dynamics, but must <b>never be interpreted as field performance on physical purifiers</b>.<br/>"
        "2. <b>Simplified Physical Assumptions:</b> The simulator models wear via a simplified coupled degradation formula. Real RO/UF filter fouling involves "
        "biofilm growth, inorganic scaling, chlorine degradation, and fluctuating feed pressure that are not "
        "fully captured in synthetic equations.<br/>"
        "3. <b>Software-Only Scope:</b> No physical hardware was built or tested. This project is 100% computational."
    )
    story.append(Paragraph(p_limit, body_style))
    story.append(Spacer(1, 14))

    sig_data = [
        [Paragraph(f"<b>Submitted by Student Team:</b> {TEAM_NAME}<br/><b>Institution:</b> {COLLEGE_NAME}<br/><b>Track:</b> Track 2 Water Purifier", table_cell),
         Paragraph(f"<b>Report Date:</b> {REPORT_DATE}<br/><b>Run command:</b> <code>streamlit run app.py</code><br/><b>Metrics File:</b> <code>metrics.json</code> ({n_units} units, {n_rows:,} rows)", table_cell)]
    ]
    t_sig = Table(sig_data, colWidths=[240, 245])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_secondary),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sig)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report generated successfully: {pdf_path}")


if __name__ == "__main__":
    build_pdf()