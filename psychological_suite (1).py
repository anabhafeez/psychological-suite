"""
=======================================================
   PSYCHOLOGICAL SUITE — STREAMLIT WEB APP
   Tool 1: Progress Tracker
   Tool 2: Full Assessment (GAD-7, PHQ-9, PSS, PCL-5, Sleep)
   Tool 3: Session Notes & Report Generator
   Author: Anab Hafeez
   Run: streamlit run psychological_suite.py
=======================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
import json

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Psychological Suite",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
    .main-title {
        font-size: 2rem; font-weight: 700;
        color: #1a1a2e; margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem; color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9ff;
        border: 1px solid #e0e4f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem; font-weight: 700; color: #1a1a2e;
    }
    .metric-label {
        font-size: 0.8rem; color: #888; text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .severity-minimal { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .severity-mild    { background:#fef9c3; color:#854d0e; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .severity-moderate{ background:#ffedd5; color:#9a3412; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .severity-severe  { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .section-header {
        font-size: 1.1rem; font-weight: 600;
        color: #1a1a2e; border-left: 4px solid #6366f1;
        padding-left: 0.75rem; margin: 1.5rem 0 1rem;
    }
    .report-box {
        background: #f5f5f5; border-radius: 8px;
        padding: 1rem; font-family: monospace;
        font-size: 0.85rem; white-space: pre-wrap;
        border: 1px solid #ddd;
    }
    .stButton > button {
        border-radius: 8px; font-weight: 600;
    }
    div[data-testid="stSidebar"] {
        background: #1a1a2e;
    }
    div[data-testid="stSidebar"] * {
        color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CLINICAL DATA
# ─────────────────────────────────────────────

SCALES_META = {
    "GAD-7":  {"max": 21, "thresholds": [5,10,15],    "labels": ["Minimal","Mild","Moderate","Severe"],              "color": "#6366f1"},
    "PHQ-9":  {"max": 27, "thresholds": [5,10,15,20], "labels": ["None","Mild","Moderate","Mod-Severe","Severe"],     "color": "#ec4899"},
    "PSS-10": {"max": 40, "thresholds": [14,27],       "labels": ["Low","Moderate","High"],                           "color": "#f59e0b"},
    "PCL-5":  {"max": 80, "thresholds": [33],          "labels": ["Below Threshold","PTSD Probable"],                 "color": "#ef4444"},
    "Sleep":  {"max": 28, "thresholds": [8,15,22],     "labels": ["Normal","Subthreshold","Moderate","Severe"],       "color": "#06b6d4"},
}

GAD7_Q  = ["Feeling nervous, anxious, or on edge?","Not being able to stop or control worrying?","Worrying too much about different things?","Trouble relaxing?","Being so restless it is hard to sit still?","Becoming easily annoyed or irritable?","Feeling afraid as if something awful might happen?"]
PHQ9_Q  = ["Little interest or pleasure in doing things?","Feeling down, depressed, or hopeless?","Trouble falling or staying asleep, or sleeping too much?","Feeling tired or having little energy?","Poor appetite or overeating?","Feeling bad about yourself or that you are a failure?","Trouble concentrating on things?","Moving or speaking so slowly others noticed, or being fidgety/restless?","Thoughts that you would be better off dead or of hurting yourself?"]
PSS_Q   = ["Been upset because of something that happened unexpectedly?","Felt unable to control important things in your life?","Felt nervous and stressed?","Felt confident about your ability to handle personal problems?","Felt that things were going your way?","Found you could not cope with all the things you had to do?","Been able to control irritations in your life?","Felt that you were on top of things?","Been angered because of things outside your control?","Felt difficulties were piling up so high you could not overcome them?"]
PSS_REV = [3,4,6,7]
PCL5_Q  = ["Repeated disturbing unwanted memories of a stressful experience?","Repeated disturbing dreams of a stressful experience?","Suddenly feeling as if a stressful experience were happening again?","Feeling very upset when reminded of a stressful experience?","Strong physical reactions when reminded of a stressful experience?","Avoiding memories or thoughts related to a stressful experience?","Avoiding external reminders of a stressful experience?","Trouble remembering important parts of a stressful experience?","Strong negative beliefs about yourself other people or the world?","Blaming yourself or someone else for a stressful experience?","Strong negative feelings such as fear horror anger guilt or shame?","Loss of interest in activities you used to enjoy?","Feeling distant or cut off from other people?","Trouble experiencing positive feelings?","Irritable behavior angry outbursts or acting aggressively?","Taking too many risks or doing things that could cause harm?","Being super-alert watchful or on guard?","Feeling jumpy or easily startled?","Having difficulty concentrating?","Trouble falling or staying asleep?"]
SLEEP_Q = ["Difficulty falling asleep at night?","Difficulty staying asleep during the night?","Problems waking up too early?","How satisfied/dissatisfied are you with your current sleep?","How noticeable to others is your sleep problem?","How worried/distressed are you about your sleep problem?","To what extent does sleep interfere with your daily functioning?"]

FREQ_OPTS  = ["Not at all (0)","Several days (1)","More than half the days (2)","Nearly every day (3)"]
STRESS_OPTS= ["Never (0)","Almost never (1)","Sometimes (2)","Fairly often (3)","Very often (4)"]
PCL_OPTS   = ["Not at all (0)","A little bit (1)","Moderately (2)","Quite a bit (3)","Extremely (4)"]
SLEEP_OPTS = ["No problem (0)","Slight problem (1)","Somewhat of a problem (2)","A big problem (3)","A very big problem (4)"]


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def get_label(score, meta):
    for i, t in enumerate(meta["thresholds"]):
        if score < t:
            return meta["labels"][i]
    return meta["labels"][-1]


def severity_class(label):
    l = label.lower()
    if any(w in l for w in ["minimal","none","low","below","normal","no sig"]):
        return "severity-minimal"
    elif any(w in l for w in ["mild","slight","sub"]):
        return "severity-mild"
    elif "moderate" in l:
        return "severity-moderate"
    return "severity-severe"


def gauge_chart(score, max_score, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, max_score], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#eee",
            "steps": [
                {"range": [0, max_score*0.3], "color": "#dcfce7"},
                {"range": [max_score*0.3, max_score*0.6], "color": "#fef9c3"},
                {"range": [max_score*0.6, max_score*0.8], "color": "#ffedd5"},
                {"range": [max_score*0.8, max_score], "color": "#fee2e2"},
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(t=40,b=10,l=20,r=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def line_chart(sessions, scores, scale_name, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sessions, y=scores,
        mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=8, color=color),
        fill="tozeroy",
        fillcolor=color.replace(")", ",0.08)").replace("rgb", "rgba") if "rgb" in color else color + "15",
        name=scale_name
    ))
    fig.update_layout(
        xaxis_title="Session", yaxis_title="Score",
        height=280, margin=dict(t=20,b=40,l=40,r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0")
    )
    return fig


def radar_chart(scores_dict):
    categories = list(scores_dict.keys())
    # normalize scores to percentage of max
    values = []
    for name, score in scores_dict.items():
        meta = SCALES_META.get(name, {"max": 100})
        values.append(round((score / meta["max"]) * 100, 1))

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(99,102,241,0.15)",
        line=dict(color="#6366f1", width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        height=350, margin=dict(t=30,b=30,l=30,r=30),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def bar_chart_multi(results):
    names, pcts, colors, labels_list = [], [], [], []
    for name, score in results.items():
        meta = SCALES_META.get(name, {"max":100,"color":"#888"})
        pct  = round((score / meta["max"]) * 100, 1)
        lbl  = get_label(score, meta)
        names.append(name)
        pcts.append(pct)
        colors.append(meta["color"])
        labels_list.append(lbl)

    fig = go.Figure(go.Bar(
        x=names, y=pcts,
        marker_color=colors,
        text=[f"{p}%<br>{l}" for p,l in zip(pcts, labels_list)],
        textposition="outside"
    ))
    fig.update_layout(
        yaxis=dict(title="Score %", range=[0,120]),
        height=320, margin=dict(t=20,b=40,l=40,r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#f0f0f0"), yaxis_gridcolor="#f0f0f0"
    )
    return fig


def generate_report_text(client_id, clinician, tool_name, data_dict):
    today = date.today().strftime("%B %d, %Y")
    lines = [
        "=" * 54,
        f"  PSYCHOLOGICAL REPORT — {tool_name.upper()}",
        "=" * 54,
        f"  Date      : {today}",
        f"  Client ID : {client_id}",
        f"  Clinician : {clinician}",
        "",
        "  RESULTS",
        "  " + "-" * 40,
    ]
    for key, val in data_dict.items():
        lines.append(f"  {key:<20}: {val}")
    lines += [
        "",
        "=" * 54,
        "  DISCLAIMER: Screening tool only.",
        "  Not a substitute for clinical diagnosis.",
        "=" * 54,
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────

if "tracker_data" not in st.session_state:
    st.session_state.tracker_data = {}
if "assessment_results" not in st.session_state:
    st.session_state.assessment_results = {}


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧠 Psych Suite")
    st.markdown("---")
    tool = st.radio(
        "Select Tool",
        ["🏠 Home",
         "📈 Progress Tracker",
         "🧪 Clinical Assessment",
         "📋 Session Report"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Client Info**")
    client_id  = st.text_input("Client ID", value="C-101", label_visibility="visible")
    clinician  = st.text_input("Clinician", value="Dr. Hafeez", label_visibility="visible")
    st.markdown("---")
    st.caption("Anab Hafeez · Clinical Portfolio")


# ─────────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────────

if tool == "🏠 Home":
    st.markdown('<p class="main-title">🧠 Psychological Suite</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">A comprehensive clinical tool for tracking, assessing, and reporting psychological health.</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem">📈</div>
            <div class="metric-label">Tool 1</div>
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">Progress Tracker</div>
            <div style="font-size:0.85rem; color:#666; margin-top:6px;">Track symptom scores across multiple sessions. View trends and improvement over time.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem">🧪</div>
            <div class="metric-label">Tool 2</div>
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">Clinical Assessment</div>
            <div style="font-size:0.85rem; color:#666; margin-top:6px;">Run GAD-7, PHQ-9, PSS, PCL-5 and Sleep assessments. Get instant clinical interpretation.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem">📋</div>
            <div class="metric-label">Tool 3</div>
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">Session Report</div>
            <div style="font-size:0.85rem; color:#666; margin-top:6px;">Generate and download full clinical reports combining all assessment results.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Use the sidebar to navigate between tools. Enter Client ID and Clinician name before starting.")


# ─────────────────────────────────────────────
#  TOOL 1 — PROGRESS TRACKER
# ─────────────────────────────────────────────

elif tool == "📈 Progress Tracker":
    st.markdown('<p class="main-title">📈 Progress Tracker</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Track symptom scores across multiple sessions and visualize progress over time.</p>', unsafe_allow_html=True)

    # Settings
    col1, col2, col3 = st.columns(3)
    with col1:
        scale_choice = st.selectbox("Select Scale", list(SCALES_META.keys()))
    with col2:
        num_sessions = st.slider("Number of Sessions", min_value=2, max_value=12, value=4)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)

    meta = SCALES_META[scale_choice]
    st.markdown(f'<p class="section-header">Enter Session Scores (0 – {meta["max"]})</p>', unsafe_allow_html=True)

    # Score inputs in columns
    cols = st.columns(min(num_sessions, 6))
    scores = []
    for i in range(num_sessions):
        col = cols[i % 6]
        default = max(0, meta["max"] - i * (meta["max"] // 8))
        s = col.number_input(f"Session {i+1}", min_value=0, max_value=meta["max"], value=default, key=f"tracker_{i}")
        scores.append(s)

    if st.button("▶ Analyze Progress", type="primary"):
        avg     = sum(scores) / len(scores)
        highest = max(scores)
        lowest  = min(scores)
        delta   = scores[-1] - scores[0]
        label   = get_label(avg, meta)
        last_lb = get_label(scores[-1], meta)
        improve = abs(delta / scores[0] * 100) if scores[0] > 0 else 0

        st.markdown("---")
        st.markdown('<p class="section-header">Results</p>', unsafe_allow_html=True)

        # Metrics row
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("Mean Score",    f"{avg:.1f}")
        m2.metric("Highest",       f"{highest}")
        m3.metric("Lowest",        f"{lowest}")
        m4.metric("Last Session",  f"{scores[-1]}")
        m5.metric("Change",        f"{'↓' if delta<0 else '↑' if delta>0 else '→'} {abs(delta):.1f}")
        m6.metric("Improvement",   f"{improve:.0f}%" if delta < 0 else "—")

        st.markdown(f"**Clinical Category:** <span class='{severity_class(label)}'>{label}</span>", unsafe_allow_html=True)

        # Charts
        c1, c2 = st.columns([2,1])
        with c1:
            st.markdown('<p class="section-header">Session Trend</p>', unsafe_allow_html=True)
            session_labels = [f"S{i+1}" for i in range(len(scores))]
            st.plotly_chart(line_chart(session_labels, scores, scale_choice, meta["color"]), use_container_width=True)
        with c2:
            st.markdown('<p class="section-header">Current Level</p>', unsafe_allow_html=True)
            st.plotly_chart(gauge_chart(scores[-1], meta["max"], f"{scale_choice} Last Session", meta["color"]), use_container_width=True)

        # Interpretation
        st.markdown('<p class="section-header">Clinical Interpretation</p>', unsafe_allow_html=True)
        if delta < 0:
            st.success(f"✅ Symptoms improved by **{abs(delta):.1f} points** ({improve:.0f}% reduction) from Session 1 to last session. Positive therapeutic progress indicated.")
        elif delta > 0:
            st.error(f"⚠️ Symptoms increased by **{delta:.1f} points** from Session 1 to last session. Review of current interventions is recommended.")
        else:
            st.info("→ Symptoms remained stable across all sessions. Continue monitoring.")

        # Save to session state for report
        st.session_state.tracker_data = {
            "scale": scale_choice, "scores": scores, "avg": avg,
            "highest": highest, "lowest": lowest, "delta": delta,
            "label": label, "last_label": last_lb
        }

        # Download report
        report_data = {
            "Scale": scale_choice,
            "Sessions": num_sessions,
            "Scores": str(scores),
            f"Mean Score": f"{avg:.1f} — {label}",
            "Highest": highest,
            "Lowest": lowest,
            "Last Session": f"{scores[-1]} — {last_lb}",
            "Trend": f"{'Improved' if delta<0 else 'Worsened' if delta>0 else 'Stable'} by {abs(delta):.1f} pts"
        }
        report_txt = generate_report_text(client_id, clinician, "Progress Tracker", report_data)
        st.download_button("⬇ Download Report", report_txt, file_name=f"tracker_{client_id}.txt", mime="text/plain")


# ─────────────────────────────────────────────
#  TOOL 2 — CLINICAL ASSESSMENT
# ─────────────────────────────────────────────

elif tool == "🧪 Clinical Assessment":
    st.markdown('<p class="main-title">🧪 Clinical Assessment</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Select one or more scales. Answer each question. Get instant clinical results.</p>', unsafe_allow_html=True)

    selected_tests = st.multiselect(
        "Select which tests to run",
        ["GAD-7 — Anxiety", "PHQ-9 — Depression", "PSS-10 — Stress", "PCL-5 — Trauma/PTSD", "Sleep — Insomnia"],
        default=["GAD-7 — Anxiety"]
    )

    if not selected_tests:
        st.warning("Please select at least one test.")
        st.stop()

    results = {}

    # ── GAD-7 ──
    if "GAD-7 — Anxiety" in selected_tests:
        with st.expander("📋 GAD-7 — Generalized Anxiety (last 2 weeks)", expanded=True):
            st.caption("How often have you been bothered by the following over the last 2 weeks?")
            gad_scores = []
            for i, q in enumerate(GAD7_Q):
                ans = st.radio(f"**Q{i+1}.** {q}", FREQ_OPTS, key=f"gad_{i}", horizontal=True)
                gad_scores.append(int(ans.split("(")[1].replace(")", "")))
            results["GAD-7"] = sum(gad_scores)

    # ── PHQ-9 ──
    if "PHQ-9 — Depression" in selected_tests:
        with st.expander("📋 PHQ-9 — Depression (last 2 weeks)", expanded=True):
            st.caption("How often have you been bothered by the following over the last 2 weeks?")
            phq_scores = []
            for i, q in enumerate(PHQ9_Q):
                ans = st.radio(f"**Q{i+1}.** {q}", FREQ_OPTS, key=f"phq_{i}", horizontal=True)
                phq_scores.append(int(ans.split("(")[1].replace(")", "")))
            results["PHQ-9"] = sum(phq_scores)

    # ── PSS ──
    if "PSS-10 — Stress" in selected_tests:
        with st.expander("📋 PSS-10 — Stress (last month)", expanded=True):
            st.caption("How often have you felt or thought the following over the last month?")
            pss_scores = []
            for i, q in enumerate(PSS_Q):
                ans = st.radio(f"**Q{i+1}.** {q}", STRESS_OPTS, key=f"pss_{i}", horizontal=True)
                raw = int(ans.split("(")[1].replace(")", ""))
                if i in PSS_REV:
                    raw = 4 - raw
                pss_scores.append(raw)
            results["PSS-10"] = sum(pss_scores)

    # ── PCL-5 ──
    if "PCL-5 — Trauma/PTSD" in selected_tests:
        with st.expander("📋 PCL-5 — Trauma/PTSD (last month)", expanded=True):
            st.caption("How much have you been bothered by the following in the past month?")
            pcl_scores = []
            for i, q in enumerate(PCL5_Q):
                ans = st.radio(f"**Q{i+1}.** {q}", PCL_OPTS, key=f"pcl_{i}", horizontal=True)
                pcl_scores.append(int(ans.split("(")[1].replace(")", "")))
            results["PCL-5"] = sum(pcl_scores)

    # ── Sleep ──
    if "Sleep — Insomnia" in selected_tests:
        with st.expander("📋 Sleep Quality — ISI (last 2 weeks)", expanded=True):
            st.caption("Rate the following sleep difficulties over the last 2 weeks.")
            sleep_scores = []
            for i, q in enumerate(SLEEP_Q):
                ans = st.radio(f"**Q{i+1}.** {q}", SLEEP_OPTS, key=f"slp_{i}", horizontal=True)
                sleep_scores.append(int(ans.split("(")[1].replace(")", "")))
            results["Sleep"] = sum(sleep_scores)

    # ── Submit & Show Results ──
    st.markdown("---")
    if st.button("🔬 Generate Assessment Results", type="primary"):

        st.markdown('<p class="section-header">Assessment Results</p>', unsafe_allow_html=True)

        # Score cards
        cols = st.columns(len(results))
        for i, (name, score) in enumerate(results.items()):
            meta  = SCALES_META[name]
            label = get_label(score, meta)
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{score}</div>
                    <div class="metric-label">{name} / {meta['max']}</div>
                    <div style="margin-top:6px"><span class="{severity_class(label)}">{label}</span></div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts
        if len(results) >= 2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<p class="section-header">Score Comparison</p>', unsafe_allow_html=True)
                st.plotly_chart(bar_chart_multi(results), use_container_width=True)
            with c2:
                st.markdown('<p class="section-header">Symptom Profile (Radar)</p>', unsafe_allow_html=True)
                st.plotly_chart(radar_chart(results), use_container_width=True)
        else:
            name, score = list(results.items())[0]
            meta = SCALES_META[name]
            st.plotly_chart(gauge_chart(score, meta["max"], name, meta["color"]), use_container_width=True)

        # Detailed interpretation
        st.markdown('<p class="section-header">Clinical Interpretation</p>', unsafe_allow_html=True)

        interp_map = {
            "GAD-7": [
                (0,4,   "✅ **Minimal Anxiety** — No significant anxiety detected. Levels are within normal range."),
                (5,9,   "🟡 **Mild Anxiety** — Some anxiety symptoms present. Practice relaxation techniques."),
                (10,14, "🟠 **Moderate Anxiety** — Noticeable anxiety affecting daily life. Therapy is recommended."),
                (15,21, "🔴 **Severe Anxiety** — High anxiety significantly impairing function. Seek professional help promptly."),
            ],
            "PHQ-9": [
                (0,4,   "✅ **Minimal Depression** — No significant depressive symptoms."),
                (5,9,   "🟡 **Mild Depression** — Early symptoms. Monitor and consider lifestyle changes."),
                (10,14, "🟠 **Moderate Depression** — Depression affecting daily functioning. Therapy recommended."),
                (15,19, "🔴 **Moderately Severe** — Significant depression. Therapy + medication evaluation advised."),
                (20,27, "🚨 **Severe Depression** — Immediate professional support is strongly recommended."),
            ],
            "PSS-10": [
                (0,13,  "✅ **Low Stress** — Stress is well managed."),
                (14,26, "🟡 **Moderate Stress** — Feeling overwhelmed at times. Stress management strategies recommended."),
                (27,40, "🔴 **High Stress** — Significant loss of control. Therapy and lifestyle change needed."),
            ],
            "PCL-5": [
                (0,19,  "✅ **Below Threshold** — No significant PTSD symptoms detected."),
                (20,32, "🟡 **Some Trauma Symptoms** — Below PTSD threshold. Trauma-informed counseling may help."),
                (33,80, "🔴 **PTSD Probable** — Scores above clinical threshold. Trauma-focused therapy (EMDR/CPT) recommended."),
            ],
            "Sleep": [
                (0,7,   "✅ **No Significant Insomnia** — Sleep quality is adequate."),
                (8,14,  "🟡 **Subthreshold Insomnia** — Some sleep difficulty. Improve sleep hygiene."),
                (15,21, "🟠 **Moderate Insomnia** — Sleep problems affecting daily life. CBT-I recommended."),
                (22,28, "🔴 **Severe Insomnia** — Significant sleep disorder. Urgent evaluation needed."),
            ],
        }

        for name, score in results.items():
            st.markdown(f"**{name}** (Score: {score})")
            for (low, high, text) in interp_map.get(name, []):
                if low <= score <= high:
                    st.markdown(f"  {text}")
                    break

        # Co-occurring patterns
        gad = results.get("GAD-7",  0)
        phq = results.get("PHQ-9",  0)
        pss = results.get("PSS-10", 0)
        pcl = results.get("PCL-5",  0)
        slp = results.get("Sleep",  0)

        patterns = []
        if gad >= 10 and phq >= 10:
            patterns.append("Anxiety and depression are both elevated. Integrated treatment is recommended.")
        if (gad >= 10 or phq >= 10) and slp >= 8:
            patterns.append("Poor sleep is worsening mood symptoms. Treating insomnia may improve anxiety/depression.")
        if pcl >= 33 and phq >= 10:
            patterns.append("Trauma and depression are co-occurring. Trauma-focused therapy should be the priority.")
        if pss >= 14 and gad >= 5:
            patterns.append("High stress is fueling anxiety. Reducing stressors will directly lower anxiety levels.")

        if patterns:
            st.markdown('<p class="section-header">Co-Occurring Patterns</p>', unsafe_allow_html=True)
            for p in patterns:
                st.warning(f"🔗 {p}")

        # Save to session state
        st.session_state.assessment_results = results

        # Download
        report_data = {name: f"{score}/{SCALES_META[name]['max']} — {get_label(score, SCALES_META[name])}" for name, score in results.items()}
        report_txt = generate_report_text(client_id, clinician, "Clinical Assessment", report_data)
        st.download_button("⬇ Download Assessment Report", report_txt, file_name=f"assessment_{client_id}.txt", mime="text/plain")


# ─────────────────────────────────────────────
#  TOOL 3 — SESSION REPORT
# ─────────────────────────────────────────────

elif tool == "📋 Session Report":
    st.markdown('<p class="main-title">📋 Session Report</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Generate a full session report combining tracker data and assessment results.</p>', unsafe_allow_html=True)

    st.markdown('<p class="section-header">Session Notes</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        session_date   = st.date_input("Session Date", value=date.today())
        session_number = st.number_input("Session Number", min_value=1, value=1)
        session_type   = st.selectbox("Session Type", ["Initial Assessment","Follow-up","Crisis","Discharge"])
    with c2:
        presenting_issue = st.text_area("Presenting Issue", placeholder="Brief description of why the client came in today...", height=100)
        mood_rating      = st.slider("Client Mood Rating (1=Very Low, 10=Very High)", 1, 10, 5)

    clinical_notes  = st.text_area("Clinical Observations", placeholder="Your clinical observations from this session...", height=120)
    interventions   = st.text_area("Interventions Used", placeholder="e.g. CBT techniques, psychoeducation, breathing exercises...", height=80)
    plan            = st.text_area("Plan for Next Session", placeholder="Goals and tasks for next session...", height=80)

    st.markdown('<p class="section-header">Include Data From Other Tools</p>', unsafe_allow_html=True)

    include_tracker    = st.checkbox("Include Progress Tracker data", value=bool(st.session_state.tracker_data))
    include_assessment = st.checkbox("Include Assessment results",    value=bool(st.session_state.assessment_results))

    if st.button("📄 Generate Full Report", type="primary"):
        today = date.today().strftime("%B %d, %Y")

        lines = [
            "=" * 58,
            "         CLINICAL SESSION REPORT",
            "=" * 58,
            f"  Date           : {session_date.strftime('%B %d, %Y')}",
            f"  Client ID      : {client_id}",
            f"  Clinician      : {clinician}",
            f"  Session No.    : {session_number}",
            f"  Session Type   : {session_type}",
            f"  Mood Rating    : {mood_rating}/10",
            "",
            "  PRESENTING ISSUE",
            "  " + "-" * 44,
            f"  {presenting_issue or 'Not recorded.'}",
            "",
            "  CLINICAL OBSERVATIONS",
            "  " + "-" * 44,
            f"  {clinical_notes or 'Not recorded.'}",
            "",
            "  INTERVENTIONS USED",
            "  " + "-" * 44,
            f"  {interventions or 'Not recorded.'}",
            "",
            "  PLAN FOR NEXT SESSION",
            "  " + "-" * 44,
            f"  {plan or 'Not recorded.'}",
        ]

        if include_tracker and st.session_state.tracker_data:
            td = st.session_state.tracker_data
            lines += [
                "",
                "  PROGRESS TRACKER DATA",
                "  " + "-" * 44,
                f"  Scale        : {td['scale']}",
                f"  Scores       : {td['scores']}",
                f"  Mean Score   : {td['avg']:.1f} — {td['label']}",
                f"  Last Session : {td['scores'][-1]} — {td['last_label']}",
                f"  Trend        : {'Improved' if td['delta']<0 else 'Worsened' if td['delta']>0 else 'Stable'} by {abs(td['delta']):.1f} pts",
            ]

        if include_assessment and st.session_state.assessment_results:
            lines += ["", "  ASSESSMENT RESULTS", "  " + "-" * 44]
            for name, score in st.session_state.assessment_results.items():
                meta  = SCALES_META[name]
                label = get_label(score, meta)
                lines.append(f"  {name:<10} {score:>3}/{meta['max']}  — {label}")

        lines += [
            "",
            "=" * 58,
            "  DISCLAIMER: This report is for clinical use only.",
            "  Generated by Psychological Suite — Anab Hafeez",
            "=" * 58,
        ]

        report_txt = "\n".join(lines)

        st.markdown('<p class="section-header">Generated Report</p>', unsafe_allow_html=True)
        st.code(report_txt, language=None)

        st.download_button(
            "⬇ Download Full Report",
            report_txt,
            file_name=f"session_report_{client_id}_{session_date}.txt",
            mime="text/plain"
        )

        if include_assessment and st.session_state.assessment_results:
            st.markdown('<p class="section-header">Visual Summary</p>', unsafe_allow_html=True)
            if len(st.session_state.assessment_results) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(bar_chart_multi(st.session_state.assessment_results), use_container_width=True)
                with c2:
                    st.plotly_chart(radar_chart(st.session_state.assessment_results), use_container_width=True)
