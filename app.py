import streamlit as st
import pandas as pd
from pathlib import Path
import os
import re
import time
from dotenv import load_dotenv
from google import genai

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="AQUAINTEL | PFAS Removal Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# AQUAINTEL DESIGN SYSTEM
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #07111f;
    --panel: #0d1b2c;
    --panel-2: #102338;
    --border: rgba(139, 183, 208, .16);
    --text: #eaf5fb;
    --muted: #91a9bc;
    --teal: #38e0c1;
    --cyan: #61c9ff;
}
.stApp {
    background:
      radial-gradient(ellipse at 12% 0%, rgba(20, 108, 128, .19), transparent 35%),
      radial-gradient(ellipse at 95% 8%, rgba(45, 104, 174, .16), transparent 30%),
      #07111f;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: rgba(7,17,31,.78); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1a2a 0%, #081421 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text); }
h1, h2, h3, h4 {
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -.025em;
}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--text); }
small, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(17,39,59,.96), rgba(11,27,43,.96));
    border: 1px solid var(--border);
    padding: 18px 20px;
    border-radius: 16px;
    min-height: 125px;
}
div[data-testid="stMetricLabel"] { color: #9db7c9 !important; }
div[data-testid="stMetricValue"] { color: #f0fbff !important; font-family: 'Space Grotesk', sans-serif; }
div[data-testid="stMetricDelta"] { color: var(--teal) !important; }
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(115deg, rgba(14,49,67,.98), rgba(12,32,55,.98) 55%, rgba(12,48,66,.95));
    border: 1px solid rgba(80,221,205,.24);
    border-radius: 24px;
    padding: 34px 38px;
    margin: 0 0 24px 0;
    box-shadow: 0 18px 55px rgba(0,0,0,.20);
}
.hero:after {
    content: "";
    position: absolute;
    width: 310px; height: 310px;
    border-radius: 50%;
    border: 1px solid rgba(56,224,193,.22);
    right: -80px; top: -140px;
    box-shadow: 0 0 0 28px rgba(56,224,193,.035), 0 0 0 58px rgba(56,224,193,.025);
}
.eyebrow {
    color: var(--teal);
    font-size: .76rem;
    font-weight: 700;
    letter-spacing: .17em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.hero h1 { font-size: clamp(2rem, 4vw, 3.1rem); margin: 0 0 8px 0; line-height: 1.08; }
.hero p { color: #c0d8e6; font-size: 1rem; max-width: 760px; margin-bottom: 0; }
.section-kicker {
    color: var(--teal);
    text-transform: uppercase;
    font-weight: 700;
    font-size: .72rem;
    letter-spacing: .14em;
    margin-bottom: 5px;
}
.panel {
    background: linear-gradient(145deg, rgba(15,34,53,.96), rgba(10,25,41,.96));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 16px;
}
.panel-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 700; margin-bottom: 6px; color: #effaff; }
.panel-subtitle { color: var(--muted); font-size: .9rem; }
.pill {
    display: inline-block;
    border: 1px solid rgba(56,224,193,.35);
    background: rgba(56,224,193,.09);
    color: #79f0d8;
    border-radius: 999px;
    padding: 5px 11px;
    font-size: .76rem;
    font-weight: 700;
}
.recommendation {
    background: linear-gradient(110deg, rgba(20,91,82,.30), rgba(17,48,64,.72));
    border: 1px solid rgba(56,224,193,.35);
    border-left: 4px solid var(--teal);
    border-radius: 16px;
    padding: 22px 24px;
    margin: 12px 0 20px 0;
}
.recommendation h3 { margin-top: 0; color: #8bf5e0 !important; }
.note {
    background: rgba(97,201,255,.07);
    border: 1px solid rgba(97,201,255,.22);
    border-radius: 12px;
    padding: 13px 16px;
    color: #bdd9e9;
    font-size: .88rem;
}
div[data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(11,26,42,.88);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 7px;
}
button[data-baseweb="tab"] {
    border-radius: 10px;
    color: #a8bfd0;
    padding: 11px 17px;
    font-weight: 600;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(100deg, rgba(56,224,193,.17), rgba(97,201,255,.12));
    color: #8ff3df;
}
button[kind="primary"] {
    background: linear-gradient(100deg, #16b99e, #229ed0) !important;
    color: #04151e !important;
    border: 0 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}
button[kind="secondary"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}
hr { border-color: var(--border); }
.stTextInput input, .stTextArea textarea {
    background: #0b1b2b !important;
    color: #eaf5fb !important;
    border-color: var(--border) !important;
}
/* AQUAINTEL HIGH-CONTRAST CONTROLS */
/* ===== PFAS dropdown (sidebar): white box, black selected text ===== */
html body [data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #8fb0c4 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    color-scheme: light !important;
}
html body [data-testid="stSidebar"] [data-baseweb="select"] > div * {
    background: transparent !important;
    background-color: transparent !important;
}
html body [data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #07111f !important;
    -webkit-text-fill-color: #07111f !important;
    opacity: 1 !important;
    text-shadow: none !important;
    font-weight: 600 !important;
}
html body [data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #07111f !important;
    color: #07111f !important;
}
/* Dropdown menu (opens in a popover outside the sidebar): white with black options */
html body div[data-baseweb="popover"],
html body div[data-baseweb="popover"] > div,
html body div[data-baseweb="popover"] ul[role="listbox"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
}
html body div[data-baseweb="popover"] ul[role="listbox"] li,
html body div[data-baseweb="popover"] ul[role="listbox"] li * {
    background: transparent !important;
    color: #07111f !important;
    -webkit-text-fill-color: #07111f !important;
    opacity: 1 !important;
}
html body div[data-baseweb="popover"] ul[role="listbox"] li:hover,
html body div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"] {
    background: #d6f3ec !important;
}
/* ===== Chat input and text fields: white box, dark readable text and placeholder ===== */
html body [data-testid="stChatInput"],
html body [data-testid="stChatInput"] > div,
html body [data-testid="stChatInput"] [data-baseweb="textarea"],
html body [data-testid="stChatInput"] [data-baseweb="base-input"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border-color: #8fb0c4 !important;
    border-radius: 14px !important;
    color-scheme: light !important;
}
html body [data-testid="stChatInput"] > div {
    border: 1px solid #8fb0c4 !important;
}
html body [data-testid="stChatInput"] textarea,
html body [data-testid="stChatInput"] input,
html body [data-testid="stChatInputTextArea"] {
    background: transparent !important;
    color: #07111f !important;
    -webkit-text-fill-color: #07111f !important;
    caret-color: #07111f !important;
    opacity: 1 !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
html body [data-testid="stChatInput"] textarea::placeholder,
html body [data-testid="stChatInput"] input::placeholder,
html body [data-testid="stChatInputTextArea"]::placeholder {
    color: #3f566a !important;
    -webkit-text-fill-color: #3f566a !important;
    opacity: 1 !important;
}
html body [data-testid="stChatInput"] textarea::-webkit-input-placeholder {
    color: #3f566a !important;
    -webkit-text-fill-color: #3f566a !important;
    opacity: 1 !important;
}
html body [data-testid="stChatInput"] textarea::-moz-placeholder {
    color: #3f566a !important;
    opacity: 1 !important;
}
html body [data-testid="stChatInputSubmitButton"] {
    background: #16b99e !important;
    border-radius: 10px !important;
}
html body [data-testid="stChatInputSubmitButton"] svg {
    fill: #04151e !important;
    color: #04151e !important;
}
/* Other text fields */
html body [data-testid="stTextInput"] input,
html body [data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #07111f !important;
    -webkit-text-fill-color: #07111f !important;
    caret-color: #07111f !important;
    opacity: 1 !important;
    border: 1px solid #8fb0c4 !important;
}
html body [data-testid="stTextInput"] input::placeholder,
html body [data-testid="stTextArea"] textarea::placeholder {
    color: #3f566a !important;
    -webkit-text-fill-color: #3f566a !important;
    opacity: 1 !important;
}

/* Suggested questions and other standard buttons: dark blue with white text */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #12344a, #16445a) !important;
    border: 1px solid rgba(56,224,193,.55) !important;
    color: #f4fbff !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    height: auto !important;
    white-space: normal !important;
    text-align: left !important;
    padding: 11px 14px !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button *,
[data-testid="stButton"] button p,
[data-testid="stButton"] button span {
    color: #f4fbff !important;
    -webkit-text-fill-color: #f4fbff !important;
    opacity: 1 !important;
}
[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #15536a, #126b70) !important;
    border-color: #38e0c1 !important;
}
[data-testid="stChatMessage"] {
    border: 1px solid rgba(139,183,208,.22);
    border-radius: 14px;
    padding: 10px 14px;
}
[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    background: rgba(13,29,46,.68);
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# PATHS + DATA
# ==================================================
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@st.cache_data
def load_data():
    molecular = pd.read_csv(BASE_DIR / "molecular_data.csv")
    treatments = pd.read_csv(BASE_DIR / "treatment_data.csv")
    database = pd.read_csv(BASE_DIR / "database.csv")

    molecular.columns = molecular.columns.str.strip()
    treatments.columns = treatments.columns.str.strip()
    database.columns = database.columns.str.strip()

    for df in [molecular, treatments, database]:
        if "PFAS" in df.columns:
            df["PFAS"] = df["PFAS"].astype(str).str.strip().str.upper()

    for column in [
        "Molecular_Weight", "LogP", "Atom_Count",
        "Carbon_Atoms", "Fluorine_Atoms", "Chain_Length"
    ]:
        if column in molecular.columns:
            molecular[column] = pd.to_numeric(molecular[column], errors="coerce")

    return molecular, treatments, database

try:
    molecular_data, treatment_data, pfas_database = load_data()
except Exception as error:
    st.error("The project databases could not be loaded.")
    st.write("Check that molecular_data.csv, treatment_data.csv, and database.csv are in the same folder as app.py.")
    st.code(str(error))
    st.stop()

available_pfas = sorted(
    set(molecular_data["PFAS"].dropna()) & set(treatment_data["PFAS"].dropna())
)
if not available_pfas:
    st.error("No matching PFAS compounds were found in the databases.")
    st.stop()

treatment_names = {
    "GAC": "Granular Activated Carbon",
    "AIX": "Anion Exchange",
    "RO": "Reverse Osmosis",
    "NF": "Nanofiltration",
}

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 18px 0">
      <div style="font-family:'Space Grotesk',sans-serif;font-size:1.45rem;font-weight:700;color:#eaf5fb">💧 AQUA<span style="color:#38e0c1">INTEL</span></div>
      <div style="font-size:.72rem;color:#91a9bc;letter-spacing:.12em;text-transform:uppercase">Environmental intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Analysis workspace")
    selected_pfas = st.selectbox("Select PFAS compound", available_pfas)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Treatment library")
    for code, name in treatment_names.items():
        st.markdown(f"<div style='padding:5px 0;color:#b5cad8'><span style='color:#38e0c1;font-weight:700'>{code}</span> · {name}</div>", unsafe_allow_html=True)
    st.markdown("---")
    if GEMINI_API_KEY:
        st.markdown('<span class="pill">● AI key detected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill" style="border-color:#f0b36c;color:#f0b36c;background:rgba(240,179,108,.08)">● AI key not detected</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Decision-support prototype • For preliminary comparison only")

# ==================================================
# SELECTED COMPOUND + SCORES
# ==================================================
molecule_rows = molecular_data[molecular_data["PFAS"] == selected_pfas]
treatment_rows = treatment_data[treatment_data["PFAS"] == selected_pfas].copy()
database_rows = pfas_database[pfas_database["PFAS"] == selected_pfas]

if molecule_rows.empty:
    st.error("Molecular data is unavailable for this compound.")
    st.stop()
if treatment_rows.empty:
    st.error("Treatment data is unavailable for this compound.")
    st.stop()

molecule = molecule_rows.iloc[0]
full_name = selected_pfas
if not database_rows.empty and "Full_Name" in database_rows.columns:
    full_name = database_rows.iloc[0]["Full_Name"]
functional_group = molecule.get("Functional_Group", "N/A")

evidence_mapping = {
    "Very High": 4,
    "High": 3,
    "Moderate-High": 2,
    "Moderate": 1,
}

def calculate_molecular_score(treatment):
    """Project heuristic rules; these are not experimentally validated predictions."""
    chain_length = molecule.get("Chain_Length", 0)
    if pd.isna(chain_length):
        chain_length = 0
    group = str(molecule.get("Functional_Group", "")).strip()
    if treatment == "GAC":
        return 2 if chain_length >= 6 else 1
    if treatment == "AIX":
        return 2 if group in ["Sulfonic acid", "Carboxylic acid"] else 0
    if treatment in ["RO", "NF"]:
        return 2
    return 0

treatment_rows["Evidence_Score"] = treatment_rows["Performance_Level"].map(evidence_mapping)
treatment_rows["Molecular_Score"] = treatment_rows["Treatment"].apply(calculate_molecular_score)
treatment_rows["Suitability_Score"] = (
    0.60 * treatment_rows["Evidence_Score"] + 0.40 * treatment_rows["Molecular_Score"]
)
treatment_rows = treatment_rows.sort_values(
    by=["Suitability_Score", "Evidence_Score"], ascending=False
).reset_index(drop=True)
recommended = treatment_rows.iloc[0]
recommended_code = str(recommended["Treatment"])
recommended_name = treatment_names.get(recommended_code, recommended_code)

def display_value(value, suffix=""):
    if pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.2f}{suffix}"
    except (ValueError, TypeError):
        return f"{value}{suffix}"

# ==================================================
# BRAND HEADER
# ==================================================
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">Environmental AI • Research workspace</div>
  <h1>AQUAINTEL</h1>
  <p style="font-size:1.12rem;font-weight:600;color:#d9f7f4">PFAS Removal Intelligence</p>
  <p>Explore molecular characteristics, compare treatment technologies, and interpret model-based removal recommendations in one scientific workspace.</p>
  <div style="margin-top:20px"><span class="pill">● PFAS ANALYSIS</span>&nbsp;&nbsp;<span class="pill">4 TREATMENT PATHWAYS</span>&nbsp;&nbsp;<span class="pill">GENAI-ASSISTED EXPLANATIONS</span></div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# FOUR MAIN TABS
# ==================================================
dashboard_tab, molecular_tab, advisor_tab, ai_tab = st.tabs([
    "⌂  Dashboard",
    "⚛  Molecular Analysis",
    "◈  Treatment Advisor",
    "✦  GenAI Assistant",
])

# ---------------- DASHBOARD ----------------
with dashboard_tab:
    st.markdown('<div class="section-kicker">Overview / 01</div>', unsafe_allow_html=True)
    st.title("Environmental intelligence overview")
    st.markdown(f"Your current workspace is focused on **{selected_pfas}** — *{full_name}*.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("PFAS compounds", f"{len(available_pfas)}", "in molecular/treatment data")
    with c2:
        method_count = int(treatment_data["Treatment"].nunique()) if "Treatment" in treatment_data.columns else 0
        st.metric("Treatment methods", f"{method_count}", "available pathways")
    with c3:
        st.metric("Treatment records", f"{len(treatment_data)}", "dataset entries")
    with c4:
        st.metric("Molecular records", f"{len(molecular_data)}", "compound profiles")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("""
        <div class="panel">
          <div class="section-kicker">Selected compound</div>
          <div class="panel-title" style="font-size:1.55rem">""" + str(selected_pfas) + """</div>
          <div class="panel-subtitle">""" + str(full_name) + """</div>
          <hr>
          <div style="display:flex;gap:30px;flex-wrap:wrap">
            <div><div style="color:#91a9bc;font-size:.8rem">Molecular weight</div><div style="font-size:1.35rem;font-weight:700;color:#eaf5fb">""" + display_value(molecule.get("Molecular_Weight"), " g/mol") + """</div></div>
            <div><div style="color:#91a9bc;font-size:.8rem">LogP</div><div style="font-size:1.35rem;font-weight:700;color:#eaf5fb">""" + display_value(molecule.get("LogP")) + """</div></div>
            <div><div style="color:#91a9bc;font-size:.8rem">Chain length</div><div style="font-size:1.35rem;font-weight:700;color:#eaf5fb">""" + display_value(molecule.get("Chain_Length"), " C") + """</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="section-kicker">Project workflow</div><div class="panel-title">From molecule to treatment insight</div><p class="panel-subtitle">01 · Inspect molecular properties</p><p class="panel-subtitle">02 · Compare treatment methods</p><p class="panel-subtitle">03 · Review model-based ranking</p><p class="panel-subtitle">04 · Ask GenAI to explain the results</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="section-kicker">Treatment ranking</div><div class="panel-title">Suitability comparison</div><div class="panel-subtitle">Scores calculated using the current project rules.</div></div>', unsafe_allow_html=True)
        chart_data = treatment_rows[["Treatment", "Suitability_Score"]].set_index("Treatment")
        st.bar_chart(chart_data, use_container_width=True)
        st.markdown(f"""
        <div class="recommendation">
          <div class="section-kicker">Current top-ranked option</div>
          <h3 style="margin-bottom:4px">{recommended_name}</h3>
          <div style="color:#c0d8e6">{recommended_code} · Suitability score <b>{recommended['Suitability_Score']:.2f}</b></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="note">Scientific note: suitability scores are heuristic decision-support values defined by this project. They are not probabilities, guarantees, or experimentally validated predictions of removal efficiency.</div>', unsafe_allow_html=True)

# ---------------- MOLECULAR ANALYSIS ----------------
with molecular_tab:
    st.markdown('<div class="section-kicker">Molecular intelligence / 02</div>', unsafe_allow_html=True)
    st.title(f"Molecular analysis · {selected_pfas}")
    st.markdown(f"<p style='color:#91a9bc'>{full_name}</p>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Molecular weight", display_value(molecule.get("Molecular_Weight"), " g/mol"))
    with m2:
        st.metric("LogP", display_value(molecule.get("LogP")))
    with m3:
        st.metric("Chain length", display_value(molecule.get("Chain_Length"), " carbons"))
    with m4:
        st.metric("Fluorine atoms", display_value(molecule.get("Fluorine_Atoms")))
    st.markdown("<br>", unsafe_allow_html=True)
    info_col, group_col = st.columns([1.15, .85])
    with info_col:
        st.markdown('<div class="panel"><div class="section-kicker">Molecular profile</div><div class="panel-title">Compound descriptors</div><div class="panel-subtitle">Values are loaded from molecular_data.csv.</div></div>', unsafe_allow_html=True)
        extra_data = {
            "Property": ["PFAS identifier", "Full name", "Functional group", "Total atoms", "Carbon atoms", "Fluorine atoms"],
            "Value": [
                selected_pfas, str(full_name), str(functional_group),
                display_value(molecule.get("Atom_Count")),
                display_value(molecule.get("Carbon_Atoms")),
                display_value(molecule.get("Fluorine_Atoms")),
            ],
        }
        st.dataframe(pd.DataFrame(extra_data), use_container_width=True, hide_index=True)
    with group_col:
        st.markdown('<div class="panel"><div class="section-kicker">Chemical context</div><div class="panel-title">Functional group</div></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:linear-gradient(145deg,rgba(19,69,77,.5),rgba(12,29,46,.95));border:1px solid rgba(56,224,193,.25);border-radius:18px;padding:28px;text-align:center">
          <div style="font-size:2.3rem">⚛</div>
          <div style="font-size:1.35rem;font-weight:700;color:#7ef0da;margin:10px 0">{functional_group}</div>
          <div style="font-size:.86rem;color:#a9c0d0">Recorded functional-group label</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="note">Molecular descriptors help characterize a compound, but individual properties do not by themselves establish real-world treatment performance.</div>', unsafe_allow_html=True)
    st.markdown("### Compare molecular descriptors")
    compare_pfas = st.multiselect(
        "Choose compounds to compare",
        available_pfas,
        default=[selected_pfas],
        key="molecular_compare",
    )
    if compare_pfas:
        compare_data = molecular_data[molecular_data["PFAS"].isin(compare_pfas)].copy()
        compare_cols = [c for c in ["PFAS", "Molecular_Weight", "LogP", "Chain_Length", "Fluorine_Atoms", "Functional_Group"] if c in compare_data.columns]
        st.dataframe(compare_data[compare_cols], use_container_width=True, hide_index=True)

# ---------------- TREATMENT ADVISOR ----------------
with advisor_tab:
    st.markdown('<div class="section-kicker">Decision support / 03</div>', unsafe_allow_html=True)
    st.title(f"Treatment advisor · {selected_pfas}")
    st.markdown("Review the model's ranking alongside the treatment details and limitations.")
    st.markdown(f"""
    <div class="recommendation">
      <div class="section-kicker">Top-ranked treatment in this model</div>
      <h3>{recommended_name} ({recommended_code})</h3>
      <div style="display:flex;gap:32px;flex-wrap:wrap;color:#c0d8e6">
        <div>Suitability score<br><b style="font-size:1.4rem;color:#8bf5e0">{recommended['Suitability_Score']:.2f}</b></div>
        <div>Evidence score<br><b style="font-size:1.4rem;color:#8bf5e0">{recommended['Evidence_Score']:.0f} / 4</b></div>
        <div>Molecular score<br><b style="font-size:1.4rem;color:#8bf5e0">{recommended['Molecular_Score']:.0f} / 2</b></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Compare all treatment methods")
    chart_col, table_col = st.columns([.9, 1.1])
    with chart_col:
        st.bar_chart(treatment_rows[["Treatment", "Suitability_Score"]].set_index("Treatment"), use_container_width=True)
    with table_col:
        display_columns = [
            "Treatment", "Category", "Reported_Removal", "Performance_Level",
            "Evidence_Score", "Molecular_Score", "Suitability_Score",
        ]
        display_columns = [c for c in display_columns if c in treatment_rows.columns]
        comparison = treatment_rows[display_columns].copy()
        if "Suitability_Score" in comparison.columns:
            comparison["Suitability_Score"] = comparison["Suitability_Score"].round(2)
        st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.markdown("### Why did this option rank first?")
    reason1, reason2, reason3 = st.columns(3)
    with reason1:
        st.markdown(f'<div class="panel"><div class="section-kicker">Evidence score</div><div style="font-size:1.6rem;font-weight:700">{recommended["Evidence_Score"]:.0f} / 4</div><div class="panel-subtitle">Based on the project&#39;s performance-level mapping.</div></div>', unsafe_allow_html=True)
    with reason2:
        st.markdown(f'<div class="panel"><div class="section-kicker">Molecular score</div><div style="font-size:1.6rem;font-weight:700">{recommended["Molecular_Score"]:.0f} / 2</div><div class="panel-subtitle">Based on the current heuristic rules.</div></div>', unsafe_allow_html=True)
    with reason3:
        st.markdown(f'<div class="panel"><div class="section-kicker">Combined score</div><div style="font-size:1.6rem;font-weight:700;color:#38e0c1">{recommended["Suitability_Score"]:.2f}</div><div class="panel-subtitle">60% evidence score + 40% molecular score.</div></div>', unsafe_allow_html=True)
    st.markdown("### Treatment details and limitations")
    for _, row in treatment_rows.iterrows():
        code = row.get("Treatment", "Unknown")
        name = treatment_names.get(code, code)
        with st.expander(f"{name} ({code})"):
            if pd.notna(row.get("How_It_Works")):
                st.write("**How it works**")
                st.write(row["How_It_Works"])
            if pd.notna(row.get("Reported_Removal")):
                st.write("**Reported removal**")
                st.write(row["Reported_Removal"])
            if pd.notna(row.get("Performance_Level")):
                st.write("**Performance level in dataset**")
                st.write(row["Performance_Level"])
            if pd.notna(row.get("Limitation")):
                st.write("**Limitations**")
                st.write(row["Limitation"])
            if pd.notna(row.get("Source")):
                st.write("**Source**")
                st.write(row["Source"])
    st.markdown('<div class="note">Interpret the ranking as a project-level heuristic, not a validated treatment design. Actual performance depends on water chemistry, operating conditions, system design, and experimental verification.</div>', unsafe_allow_html=True)

# ==================================================
# GENAI ASSISTANT HELPERS (instant answers + Gemini with retries)
# ==================================================
# Models are tried in order. Override with GEMINI_MODELS="model-a,model-b" in your .env file.
GEMINI_MODELS = [
    name.strip() for name in os.getenv("GEMINI_MODELS", "").split(",") if name.strip()
] or ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
GEMINI_TIME_BUDGET_SECONDS = 30
INSTANT_NOTE = "⚡ Instant answer built from your project data (no AI call needed)."


def text_or(value, fallback="not available"):
    """Return a clean string, or a fallback for missing / NaN values."""
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    return str(value)


def fmt_num(value, digits=0):
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "N/A"


def md_cell(value):
    return text_or(value, "N/A").replace("|", "/").replace("\n", " ")


def answer_full_name():
    if str(full_name).strip().upper() == str(selected_pfas).strip().upper():
        return f"The project database does not list a full name for **{selected_pfas}**."
    return (
        f"**{selected_pfas}** stands for **{full_name}**.\n\n"
        f"Its functional group is recorded as **{text_or(functional_group)}** in the project data."
    )


def answer_why_rank():
    r = recommended
    lines = [
        f"**{recommended_name} ({recommended_code})** ranked first for **{selected_pfas}** "
        "in this project's heuristic scoring.",
        "",
        f"- **Evidence score: {fmt_num(r.get('Evidence_Score'))} / 4.** Mapped from the performance level "
        f"in the dataset (**{text_or(r.get('Performance_Level'))}**).",
        f"- **Molecular score: {fmt_num(r.get('Molecular_Score'))} / 2.** Simple rules using chain length "
        f"({display_value(molecule.get('Chain_Length'))} C) and functional group "
        f"({text_or(functional_group)}).",
        f"- **Combined score: {fmt_num(r.get('Suitability_Score'), 2)}** "
        f"(60% evidence + 40% molecular).",
    ]
    if pd.notna(r.get("Reported_Removal")):
        lines += ["", f"**Reported removal in the dataset:** {r['Reported_Removal']}"]
    if pd.notna(r.get("Limitation")):
        lines += ["", f"**Key limitation:** {r['Limitation']}"]
    if len(treatment_rows) > 1:
        second = treatment_rows.iloc[1]
        second_code = str(second.get("Treatment", "?"))
        lines += [
            "",
            f"The runner-up was **{treatment_names.get(second_code, second_code)} ({second_code})** "
            f"with a score of {fmt_num(second.get('Suitability_Score'), 2)}.",
        ]
    lines += ["", "*This is a heuristic ranking, not an experimentally validated prediction.*"]
    return "\n".join(lines)


def answer_compare():
    lines = [
        f"Here is how the treatment options compare for **{selected_pfas}** in this project's data:",
        "",
        "| Treatment | Performance level | Evidence (0-4) | Molecular (0-2) | Score |",
        "|---|---|---|---|---|",
    ]
    for _, row in treatment_rows.iterrows():
        code = str(row.get("Treatment", "?"))
        lines.append(
            f"| {md_cell(treatment_names.get(code, code))} ({code}) "
            f"| {md_cell(row.get('Performance_Level'))} "
            f"| {fmt_num(row.get('Evidence_Score'))} "
            f"| {fmt_num(row.get('Molecular_Score'))} "
            f"| {fmt_num(row.get('Suitability_Score'), 2)} |"
        )
    limitation_lines = [
        f"- **{row.get('Treatment', '?')}:** {row['Limitation']}"
        for _, row in treatment_rows.iterrows()
        if pd.notna(row.get("Limitation"))
    ]
    if limitation_lines:
        lines += ["", "**Limitations noted in the dataset**", ""] + limitation_lines
    lines += ["", "*Scores are project heuristics, not validated predictions of removal efficiency.*"]
    return "\n".join(lines)


def answer_difficulty():
    return (
        "**Why PFAS are hard to remove from water**\n\n"
        "- **Very strong carbon-fluorine bonds.** The C-F bond is one of the strongest in organic "
        "chemistry, so PFAS barely break down naturally. That is why they are called "
        "\"forever chemicals\".\n"
        "- **Surfactant-like structure.** A water-repelling fluorinated tail is paired with a charged "
        "or polar head group, so they behave differently from ordinary organic pollutants.\n"
        "- **Mobile and soluble.** Many PFAS, especially short-chain ones, stay dissolved and are "
        "captured less well by adsorption.\n"
        "- **Huge variety.** There are thousands of PFAS with different chain lengths and head groups, "
        "so one method rarely works equally well for all of them.\n"
        "- **Very low targets.** Health-based limits are in the parts-per-trillion range, and the removed "
        "PFAS still ends up in spent carbon, resin or a concentrate that needs safe handling.\n\n"
        "That is why this project compares several treatment options instead of assuming one works for everything."
    )


def answer_limitations():
    return (
        "**Limitations of this project's scoring method**\n\n"
        "- **Heuristic, not validated.** The score is a decision-support value defined by this project. "
        "It is not a probability or a measured removal efficiency.\n"
        "- **Coarse evidence score.** It converts text labels from the dataset into numbers "
        "(Very High = 4, High = 3, Moderate-High = 2, Moderate = 1). A label outside this list gets no score.\n"
        "- **Simple molecular rules.** Only chain length and functional group are used. "
        "For example, GAC is favoured for chain length of 6 or more, AIX for sulfonic or carboxylic acids, "
        "and RO/NF always receive the top molecular score.\n"
        "- **Fixed 60/40 weighting.** The weights were chosen by the project, not fitted to experimental data.\n"
        "- **Ignores real-world conditions.** pH, competing organic matter, other ions, flow rate, "
        "contact time and system design all change real performance.\n"
        "- **No cost, energy or waste factors.** Operating cost, energy use and disposal of spent media "
        "or concentrate are not scored.\n"
        "- **Depends on the dataset.** Results are only as good as the reported values in the CSV files.\n\n"
        "*Use the ranking as a starting point for discussion, then verify with lab or pilot data.*"
    )


def answer_descriptors():
    return "\n".join([
        f"**Molecular descriptors for {selected_pfas}, in plain language**",
        "",
        f"- **Molecular weight ({display_value(molecule.get('Molecular_Weight'), ' g/mol')}):** "
        "how heavy one molecule is. Heavier molecules are generally larger, which can matter for "
        "membranes such as RO and NF.",
        f"- **LogP ({display_value(molecule.get('LogP'))}):** how much the molecule prefers oily "
        "surroundings over water. Higher values mean more water-repelling.",
        f"- **Chain length ({display_value(molecule.get('Chain_Length'), ' C')}):** the number of carbons "
        "in the backbone. In general, longer chains stick to activated carbon more strongly, while "
        "short-chain PFAS are harder to capture.",
        f"- **Fluorine atoms ({display_value(molecule.get('Fluorine_Atoms'))}):** more fluorine means "
        "more strong C-F bonds, which makes the compound more persistent.",
        f"- **Functional group ({text_or(functional_group)}):** the reactive head of the molecule. "
        "Sulfonic and carboxylic acid heads are negatively charged in water, which is why anion "
        "exchange can target them.",
        "",
        "*Descriptors describe a molecule, but on their own they do not prove how well a treatment "
        "will work in real water.*",
    ])


def answer_overview():
    return "\n".join([
        "**How AQUAINTEL helps with PFAS removal**",
        "",
        "AQUAINTEL is a decision-support prototype that takes you from a molecule to a treatment shortlist:",
        "",
        "1. **Molecular Analysis:** inspect descriptors (weight, LogP, chain length, fluorine count, "
        "functional group) for each PFAS compound.",
        "2. **Treatment Advisor:** compare GAC, AIX, RO and NF using the reported performance levels "
        "in the dataset plus simple molecular rules.",
        "3. **Ranking:** each option gets a heuristic suitability score (60% evidence + 40% molecular), "
        "so you can see which looks most promising and why.",
        "4. **GenAI assistant:** explains the results and limitations in plain language.",
        "",
        f"For **{selected_pfas}** right now, the top-ranked option is **{recommended_name} "
        f"({recommended_code})** with a score of {fmt_num(recommended.get('Suitability_Score'), 2)}.",
        "",
        "*It is a screening tool, not a validated treatment design. Confirm with lab or pilot testing.*",
    ])


def explain_gemini_error(error_text):
    """Turn raw API errors into a short, honest reason."""
    t = str(error_text).upper()
    if any(k in t for k in ("API_KEY_INVALID", "API KEY NOT VALID", "PERMISSION_DENIED", "UNAUTHENTICATED", "403", "401")):
        return "the API key was rejected. Check GEMINI_API_KEY in your .env file."
    if "NOT_FOUND" in t or "404" in t:
        return "the configured model name was not found. Update GEMINI_MODELS in your .env file."
    if "429" in t or "RESOURCE_EXHAUSTED" in t or "QUOTA" in t:
        return "your Gemini quota or rate limit was reached. Wait a minute and try again."
    if "503" in t or "UNAVAILABLE" in t:
        return "Google's servers are busy (high demand). Try again in a moment."
    if "EMPTY" in t:
        return "the model returned an empty response."
    return "the AI service could not complete the request."


def lookup_full_form(question):
    """Answer 'full form / full name of <compound>' questions straight from the database."""
    q = question.lower()
    if not re.search(r"full form|full name|stand(s)? for|abbreviation|expand", q):
        return None
    if "Full_Name" in pfas_database.columns and "PFAS" in pfas_database.columns:
        for _, row in pfas_database.drop_duplicates("PFAS").iterrows():
            name = str(row["PFAS"]).strip()
            if name and re.search(rf"\b{re.escape(name.lower())}\b", q) and pd.notna(row.get("Full_Name")):
                return f"**{name}** stands for **{row['Full_Name']}**."
    if re.search(r"\bpfas\b", q):
        return (
            "**PFAS** stands for **per- and polyfluoroalkyl substances**, a large family of "
            "man-made chemicals containing strong carbon-fluorine bonds."
        )
    return None


def keyword_answer(question):
    """Offline fallback: map a typed question to the closest built-in answer."""
    q = question.lower()
    if re.search(r"website|web site|aquaintel|this (app|tool|project|platform|site)|how does this|purpose of|what does this", q):
        return answer_overview
    if re.search(r"limitation|scoring|score method|heuristic", q):
        return answer_limitations
    if "descriptor" in q:
        return answer_descriptors
    if re.search(r"difficult|hard to remove|hard to treat|persistent|forever", q):
        return answer_difficulty
    if re.search(r"compare|comparison|\bvs\b|versus", q):
        return answer_compare
    if re.search(r"rank|first|recommend|best|top", q):
        return answer_why_rank
    return None


@st.cache_resource(show_spinner=False)
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)


def is_transient_error(error):
    text = str(error).upper()
    return any(token in text for token in (
        "503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL", "DEADLINE", "TIMEOUT",
    ))


def ask_gemini(question, response_area):
    """Stream an answer from Gemini. Retries busy models once, then tries the next model.
    Returns (answer_text, error_text)."""
    molecular_summary = {
        "PFAS": selected_pfas,
        "Full name": str(full_name),
        "Molecular weight": display_value(molecule.get("Molecular_Weight")),
        "LogP": display_value(molecule.get("LogP")),
        "Chain length": display_value(molecule.get("Chain_Length")),
        "Fluorine atoms": display_value(molecule.get("Fluorine_Atoms")),
        "Functional group": str(functional_group),
    }
    treatment_summary = [
        {
            "Treatment": str(row.get("Treatment", "N/A")),
            "Reported removal": str(row.get("Reported_Removal", "Unavailable")),
            "Performance level": str(row.get("Performance_Level", "Unavailable")),
            "Limitation": str(row.get("Limitation", "Unavailable")),
            "Score": display_value(row.get("Suitability_Score")),
        }
        for _, row in treatment_rows.iterrows()
    ]
    recent_history = st.session_state.aquaintel_chat_messages[-5:-1]
    history_text = "\n".join(
        f"{item['role'].upper()}: {item['content'][:600]}" for item in recent_history
    )
    prompt = f"""
You are AQUAINTEL, a scientific assistant for a college PFAS Removal Advisor prototype.
Answer the latest question in clear, student-friendly English. Be concise and accurate (under 150 words).

Recent conversation:
{history_text if history_text else "No previous messages."}

Latest question: {question}
Selected compound data: {molecular_summary}
Treatment comparison: {treatment_summary}
Current top-ranked treatment: {recommended_name} ({recommended_code}), heuristic score {recommended["Suitability_Score"]:.2f}

Rules: Use only the supplied project data for project-specific claims. Distinguish reported information
from heuristic scores. Do not invent experimental results, percentages, studies, or references.
Explain that the project's scores are heuristics, not experimentally validated predictions.
Do not claim that the top-ranked treatment is universally best. If information is missing, say so.
"""
    client = get_gemini_client(GEMINI_API_KEY)
    deadline = time.monotonic() + GEMINI_TIME_BUDGET_SECONDS
    errors = []
    skip_models = set()  # models with permanent errors (wrong name, bad key) are not retried
    # Round 1 tries every model once; if all are busy we back off (2s, 4s) and go again.
    for round_number, pause in enumerate([0, 2, 4]):
        if pause:
            if time.monotonic() + pause > deadline:
                break
            response_area.markdown(f"*Gemini is busy, retrying (attempt {round_number + 1} of 3)…*")
            time.sleep(pause)
        any_transient = False
        for model_name in GEMINI_MODELS:
            if model_name in skip_models:
                continue
            if time.monotonic() > deadline:
                return "", "\n".join(errors)
            parts = []
            try:
                stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=prompt,
                    config={"temperature": 0.3, "max_output_tokens": 2048},
                )
                for chunk in stream:
                    chunk_text = getattr(chunk, "text", None)
                    if chunk_text:
                        parts.append(chunk_text)
                        response_area.markdown("".join(parts) + " ▌")
                if parts:
                    return "".join(parts).strip(), None
                errors.append(f"{model_name}: empty response")
                any_transient = True
            except Exception as error:
                if parts:  # connection dropped mid-answer: keep what we have
                    return "".join(parts).strip() + "\n\n*(answer was cut off)*", None
                errors.append(f"{model_name}: {error}")
                if is_transient_error(error):
                    any_transient = True
                else:
                    skip_models.add(model_name)
        if not any_transient:
            break  # nothing worth retrying
    return "", "\n".join(errors)


# ---------------- GENAI CHAT ASSISTANT ----------------
with ai_tab:
    st.markdown('<div class="section-kicker">Generative AI / 04</div>', unsafe_allow_html=True)
    st.title("GenAI research assistant")
    st.markdown(
        "Explore the selected PFAS compound, understand its treatment ranking, "
        "and ask follow-up questions."
    )
    st.markdown(
        f'<div class="panel"><div class="section-kicker">CURRENT CONTEXT</div>'
        f'<div class="panel-title">{selected_pfas} · {full_name}</div>'
        f'<div class="panel-subtitle">Top-ranked option: {recommended_name} '
        f'({recommended_code}) · heuristic score {recommended["Suitability_Score"]:.2f}</div></div>',
        unsafe_allow_html=True,
    )

    # Start a fresh conversation when the selected compound changes.
    if "aquaintel_chat_messages" not in st.session_state:
        st.session_state.aquaintel_chat_messages = []
    if "aquaintel_answer_cache" not in st.session_state:
        st.session_state.aquaintel_answer_cache = {}
    if st.session_state.get("aquaintel_chat_compound") != selected_pfas:
        st.session_state.aquaintel_chat_messages = []
        st.session_state.aquaintel_chat_compound = selected_pfas

    # Built-in questions: answered instantly from the project data, no AI call.
    suggestion_items = [
        (f"Why did {recommended_code} rank first for {selected_pfas}?", answer_why_rank),
        (f"Compare GAC, AIX, RO, and NF for {selected_pfas}.", answer_compare),
        (f"What is the full name of {selected_pfas}?", answer_full_name),
        ("Why are PFAS difficult to remove from water?", answer_difficulty),
        ("What are the limitations of this project's scoring method?", answer_limitations),
        ("Explain the molecular descriptors in simple terms.", answer_descriptors),
    ]
    instant_lookup = {label.strip().lower(): builder for label, builder in suggestion_items}

    def queue_question(question_text):
        st.session_state["aquaintel_pending_question"] = question_text

    def clear_chat():
        st.session_state.aquaintel_chat_messages = []

    header_col, clear_col = st.columns([5, 1])
    with header_col:
        st.markdown("#### Conversation")
    with clear_col:
        st.button("Clear chat", key="clear_aquaintel_chat", on_click=clear_chat)

    # Messages are drawn inside this container so they always appear ABOVE the buttons and input.
    history_box = st.container()

    st.markdown("#### Suggested questions")
    st.caption("⚡ Click a question for an instant answer, or type your own message below.")
    suggestion_columns = st.columns(2)
    for index, (label, _builder) in enumerate(suggestion_items):
        with suggestion_columns[index % 2]:
            st.button(
                label,
                key=f"aquaintel_suggestion_{index}",
                use_container_width=True,
                on_click=queue_question,
                args=(label,),
            )

    typed_question = st.chat_input("Type your question here...")
    user_question = typed_question or st.session_state.pop("aquaintel_pending_question", None)

    with history_box:
        for message in st.session_state.aquaintel_chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("note"):
                    st.caption(message["note"])

        if user_question:
            st.session_state.aquaintel_chat_messages.append(
                {"role": "user", "content": user_question}
            )
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                response_area = st.empty()
                answer, note = None, None
                question_key = user_question.strip().lower()
                cache_key = (selected_pfas, question_key)

                # 1) Built-in suggested question -> instant local answer.
                builder = instant_lookup.get(question_key)
                if builder:
                    answer, note = builder(), INSTANT_NOTE
                # 2) "Full form / full name of X" -> instant lookup in the database.
                if answer is None:
                    answer = lookup_full_form(user_question)
                    if answer:
                        note = INSTANT_NOTE
                # 3) Same custom question asked before -> cached Gemini answer.
                if answer is None and cache_key in st.session_state.aquaintel_answer_cache:
                    answer = st.session_state.aquaintel_answer_cache[cache_key]
                # 4) Otherwise ask Gemini (with retries), then fall back to built-in answers.
                if answer is None:
                    gemini_answer, gemini_error = "", None
                    if GEMINI_API_KEY:
                        response_area.markdown("*Thinking…*")
                        try:
                            gemini_answer, gemini_error = ask_gemini(user_question, response_area)
                        except Exception as error:
                            gemini_error = error
                    if gemini_answer:
                        answer = gemini_answer
                        st.session_state.aquaintel_answer_cache[cache_key] = answer
                    else:
                        reason = (
                            explain_gemini_error(gemini_error) if (GEMINI_API_KEY and gemini_error)
                            else "no GEMINI_API_KEY was found in your .env file."
                        )
                        fallback = keyword_answer(user_question)
                        if fallback:
                            answer = fallback()
                        else:
                            answer = (
                                "I could not reach Gemini for this custom question, so here is what the "
                                "project data says about your current compound instead:\n\n"
                                + answer_overview()
                            )
                        note = f"⚡ Built-in answer, because {reason}"
                        if gemini_error:
                            with st.expander("Technical detail"):
                                st.code(str(gemini_error))

                if answer:
                    response_area.markdown(answer)
                    if note:
                        st.caption(note)
                    st.session_state.aquaintel_chat_messages.append(
                        {"role": "assistant", "content": answer, "note": note}
                    )

    st.markdown(
        '<div class="note">Research prototype: AI explanations should be checked against scientific sources. '
        'Treatment rankings are project heuristics, not experimentally validated design recommendations.</div>',
        unsafe_allow_html=True,
    )

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown("""
<div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:#718da2;font-size:.78rem">
  <span><b style="color:#9cb8c9">AQUAINTEL</b> · PFAS Removal Intelligence</span>
  <span>Research prototype · Not a substitute for laboratory validation or professional treatment design</span>
</div>
""", unsafe_allow_html=True)
