import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# 1. CONFIGURATION GÉNÉRALE
# ============================================================
st.set_page_config(
    page_title="Water Quality Plateform",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page" not in st.session_state:
    st.session_state.page = "Simulation"

# ============================================================
# 2. TOKENS VISUELS & CSS
# ------------------------------------------------------------
# Direction : "instrument hydrologique" — panneau de mesure
# scientifique plutôt que dashboard SaaS générique.
# Palette ancrée dans le sujet (eau, seuils sanitaires) :
#   encre profonde #0A2A3D · papier froid #F4F7F8
#   sarcelle #0E7C86 (conforme) · cyan #35B8C9 (buvable)
#   ambre #E8A33D (risque antibio) · corail #D9524B (risqué)
# Typo : Space Grotesk (display technique) + Inter (texte)
#        + IBM Plex Mono (lectures / codes de paramètres)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root, [data-testid="stAppViewContainer"], .stApp {
    --ink: #0A2A3D;
    --paper: #F4F7F8;
    --card: #FFFFFF;
    --teal: #0E7C86;
    --teal-soft: #E4F2F1;
    --cyan: #2FAAB8;
    --cyan-soft: #E6F5F7;
    --amber: #C9822C;
    --amber-soft: #FBF0DE;
    --coral: #C24A42;
    --coral-soft: #FBE9E7;
    --line: #DCE4E6;
    --muted: #5B7480;
    background-color: var(--paper) !important;
    color: var(--ink) !important;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ---------- Typographie ---------- */
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--ink) !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}

.mono { font-family: 'IBM Plex Mono', monospace; }

.eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--teal);
    font-weight: 600;
}

section[data-testid="stSidebar"] { display: none; }

/* ---------- Bandeau d'en-tête ---------- */
.hero {
    background: linear-gradient(135deg, #0A2A3D 0%, #0E4A54 65%, #0E7C86 100%);
    border-radius: 20px;
    padding: 34px 40px 26px 40px;
    margin-bottom: 6px;
    position: relative;
    overflow: hidden;
}
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9FE0DE;
    font-weight: 600;
}
.hero h1 {
    color: #FFFFFF !important;
    font-size: 2.1rem !important;
    margin: 4px 0 4px 0 !important;
}
.hero p {
    color: #C7E4E2;
    font-size: 0.95rem;
    max-width: 620px;
    margin: 0;
}
.hero-wave { position: absolute; bottom: -2px; left: 0; width: 100%; line-height: 0; }

/* ---------- Navigation segmentée ---------- */
div[data-testid="stHorizontalBlock"] { align-items: center; }

button[data-testid="baseButton-primary"], button[kind="primary"] {
    background-color: var(--ink) !important;
    color: #ffffff !important;
    border: 1px solid var(--ink) !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
button[data-testid="baseButton-primary"]:hover, button[kind="primary"]:hover {
    background-color: var(--teal) !important;
    border-color: var(--teal) !important;
}

button[data-testid="baseButton-secondary"], button[kind="secondary"] {
    background-color: var(--card) !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
button[data-testid="baseButton-secondary"]:hover, button[kind="secondary"]:hover {
    border-color: var(--teal) !important;
    color: var(--teal) !important;
}

/* ---------- Inputs numériques ---------- */
div[data-testid="stNumberInputContainer"], div[data-baseweb="input"], div[data-baseweb="base-input"] {
    background-color: var(--card) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    color: var(--ink) !important;
}
div[data-testid="stNumberInputContainer"] input {
    background-color: transparent !important;
    color: var(--ink) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
div[data-testid="stNumberInputContainer"] button { background-color: var(--card) !important; color: var(--ink) !important; border: none !important; }
div[data-testid="stNumberInputContainer"] button:hover { background-color: var(--paper) !important; color: var(--teal) !important; }

label { color: var(--ink) !important; font-weight: 500 !important; font-size: 0.88rem !important; }

/* ---------- Cartes génériques (paramètre / résultat) ---------- */
.param-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.param-card .eyebrow { display:block; margin-bottom: 6px; }

.result-card {
    border-radius: 16px;
    padding: 22px 24px;
    font-family: 'Space Grotesk', sans-serif;
}

/* ---------- Légende d'échelle ---------- */
.scale-legend { display:flex; border-radius: 10px; overflow:hidden; height: 10px; margin: 6px 0 14px 0; }
.scale-legend span { flex: 1; }
.scale-labels { display:flex; justify-content: space-between; font-family:'IBM Plex Mono', monospace; font-size: 0.68rem; color: var(--muted); }

/* ---------- Dataframe / tableau ---------- */
div[data-testid="stDataFrame"], div[data-testid="stTable"], [data-testid="stDataFrame"] > div, [data-testid="stDataFrame"] canvas {
    background-color: var(--card) !important; color: var(--ink) !important;
}
div[data-testid="stDataFrame"] { border: 1px solid var(--line) !important; border-radius: 14px !important; padding: 6px !important; }

/* ---------- File uploader ---------- */
div[data-testid="stFileUploader"] {
    background-color: var(--card) !important;
    border: 1.5px dashed #B9CDD1 !important;
    border-radius: 14px !important;
    padding: 14px !important;
}
div[data-testid="stFileUploaderDropzone"] { background-color: var(--card) !important; }
div[data-testid="stFileUploaderDropzone"] span { color: var(--ink) !important; }

/* ---------- Expanders ---------- */
div[data-testid="stExpander"] {
    background-color: var(--card) !important;
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
    margin-bottom: 16px !important;
}
div[data-testid="stExpander"] summary { font-weight: 600 !important; color: var(--teal) !important; font-family: 'Space Grotesk', sans-serif !important; }

/* ---------- Métriques KPI custom ---------- */
.kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-left: 4px solid var(--teal);
    border-radius: 12px;
    padding: 14px 16px;
}
.kpi-card .eyebrow { color: var(--muted); }
.kpi-value { font-family:'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 700; color: var(--ink); line-height:1.2; }
.kpi-sub { font-family:'IBM Plex Mono', monospace; font-size: 0.78rem; color: var(--muted); }

hr { border-color: var(--line) !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. FONCTIONS MÉTIER
# ============================================================
CLASSES = {
    "Eau potable": {"color": "#0E7C86", "soft": "#E4F2F1", "text": "#0E7C86"},
    "Eau buvable": {"color": "#2FAAB8", "soft": "#E6F5F7", "text": "#1B7A85"},
    "Exposée aux risques d'antibiorésistance": {"color": "#C9822C", "soft": "#FBF0DE", "text": "#A5691E"},
    "Eau risquée": {"color": "#C24A42", "soft": "#FBE9E7", "text": "#A83A33"},
}

def classifier_eau(eblse, mes, dco_dbo, np_ratio):
    """Classification de la qualité de l'eau selon 4 indicateurs de pollution.

    Règles (dans cet ordre) :
      1. Eau potable   : E.BLSE == 0 UFC/100mL, MES == 0 mg/L,
                          DCO/DBO5 < 5, N/P entre 10 et 17.
      2. Eau buvable    : E.BLSE < 6 UFC/100mL, MES < 5 mg/L,
                          DCO/DBO5 < 5, N/P entre 10 et 17.
      3. Sinon, si E.BLSE >= 6 UFC/100mL (bactéries résistantes confirmées) :
                          Exposée aux risques d'antibiorésistance.
      4. Sinon (buvable non satisfaite pour MES, DCO/DBO5 ou N/P,
         avec E.BLSE < 6) : Eau risquée.
    """
    eblse = 0.0 if pd.isna(eblse) else float(eblse)
    mes = 0.0 if pd.isna(mes) else float(mes)
    dco_dbo = 0.0 if pd.isna(dco_dbo) else float(dco_dbo)
    np_ratio = 0.0 if pd.isna(np_ratio) else float(np_ratio)

    if eblse == 0 and mes == 0 and dco_dbo < 5 and (10 <= np_ratio <= 17):
        return "Eau potable"
    elif eblse < 6 and mes < 5 and dco_dbo < 5 and (10 <= np_ratio <= 17):
        return "Eau buvable"
    elif eblse >= 6:
        return "Exposée aux risques d'antibiorésistance"
    else:
        return "Eau risquée"

def indice_indicatif(eblse, mes, dco_dbo, np_ratio):
    """Indice visuel 0-100 (indicatif) utilisé uniquement pour animer la
    jauge — la classification officielle reste basée sur les seuils ci-dessus."""
    eblse = 0.0 if pd.isna(eblse) else float(eblse)
    mes = 0.0 if pd.isna(mes) else float(mes)
    dco_dbo = 0.0 if pd.isna(dco_dbo) else float(dco_dbo)
    np_ratio = 0.0 if pd.isna(np_ratio) else float(np_ratio)
    score = 100
    score -= min(eblse * 12, 60)
    score -= min(mes * 4, 25)
    score -= min(abs(dco_dbo - 2) * 6, 20)
    score -= min(abs(np_ratio - 13.5) * 1.5, 15)
    return max(0, min(100, round(score)))

def build_gauge(score, label):
    color = CLASSES[label]["color"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "font": {"family": "IBM Plex Mono", "size": 40, "color": "#0A2A3D"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "#DCE4E6", "showticklabels": False},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25], "color": "#FBE9E7"},
                {"range": [25, 55], "color": "#FBF0DE"},
                {"range": [55, 80], "color": "#E6F5F7"},
                {"range": [80, 100], "color": "#E4F2F1"},
            ],
        },
    ))
    fig.update_layout(
        height=210,
        margin=dict(t=10, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
    )
    return fig

WAVE_SVG = """
<div class="hero-wave">
<svg viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" style="width:100%;height:36px;">
<path d="M0,32 C240,60 480,4 720,24 C960,44 1200,10 1440,30 L1440,60 L0,60 Z" fill="#F4F7F8"/>
</svg>
</div>
"""

# ============================================================
# 4. EN-TÊTE
# ============================================================
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">SURVEILLANCE HYDRIQUE</div>
    <h1>Water Quality Plateform</h1>
    <p>Évaluation et analyse des ressources hydriques à Madagascar — diagnostic d'échantillon
    et lecture de campagnes de terrain, selon les seuils microbiologiques, physico-chimiques
    et de résistance aux antibiotiques.</p>
    {WAVE_SVG}
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

col_l, col1, col2, col_r = st.columns([3, 1.8, 2, 3])
with col1:
    btn1 = "primary" if st.session_state.page == "Simulation" else "secondary"
    if st.button("🧪  Simulation", type=btn1, use_container_width=True):
        st.session_state.page = "Simulation"
        st.rerun()
with col2:
    btn2 = "primary" if st.session_state.page == "Analyse" else "secondary"
    if st.button("📊  Analyse de campagne", type=btn2, use_container_width=True):
        st.session_state.page = "Analyse"
        st.rerun()

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ============================================================
# 5. PAGE — SIMULATION
# ============================================================
if st.session_state.page == "Simulation":

    with st.expander("📖  Documentation des indicateurs de qualité"):
        st.markdown("""
        | Code | Indicateur | Définition & rôle écologique |
        | :--- | :--- | :--- |
        | `MES` | Matières en suspension | Particules solides non dissoutes, d'origine naturelle (sédiments, débris) ou anthropique (rejets). |
        | `DCO/DBOn` | Demande chimique / biologique en oxygène | Mesure la pollution organique et les sources de contamination. |
        | `N/P` | Ratio azote / phosphore | Équilibre entre nutriments essentiels à la croissance des plantes et algues de l'écosystème. |
        | `T°` | Température | Paramètre d'équilibre écologique influençant croissance et reproduction des espèces aquatiques. |
        | `pH` | Potentiel hydrogène | Acidité ou alcalinité de l'eau, déterminante pour la santé aquatique et la potabilité. |
        | `O₂` | Oxygène dissous | Niveau assurant la respiration de la faune aquatique et des micro-organismes. |
        | `Ec BLSE` | *E. coli* BLSE résistantes (log UFC/100ml) | Bactéries indicatrices de résistance aux antibiotiques. |
        """)
        st.markdown('<div class="eyebrow" style="margin-top:14px; display:block;">RÈGLES DE CLASSIFICATION</div>', unsafe_allow_html=True)
        st.markdown("""
        | Statut | Conditions cumulatives |
        | :--- | :--- |
        | 🟢 **Eau potable** | E.BLSE **= 0** UFC/100mL · MES **= 0** mg/L · DCO/DBO5 **< 5** · N/P **∈ [10, 17]** |
        | 🔵 **Eau buvable** | E.BLSE **< 6** UFC/100mL · MES **< 5** mg/L · DCO/DBO5 **< 5** · N/P **∈ [10, 17]** |
        | 🟠 **Exposée aux risques d'antibiorésistance** | Conditions ci-dessus non réunies **et** E.BLSE **≥ 6** UFC/100mL |
        | 🔴 **Eau risquée** | Conditions ci-dessus non réunies, avec E.BLSE **< 6** UFC/100mL |
        """)

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="eyebrow">PARAMÈTRES DE L\'ÉCHANTILLON</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            eblse_in = st.number_input("E. coli BLSE (UFC/100ml)", min_value=0.0, value=0.0, step=0.1)
            mes_in = st.number_input("MES (mg/L)", min_value=0.0, value=0.0, step=0.1)
        with c2:
            dco_dbo_in = st.number_input("Ratio DCO / DBO5", min_value=0.0, value=2.0, step=0.1)
            np_in = st.number_input("Ratio N / P", min_value=0, value=12, step=1)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        evaluer = st.button("Évaluer l'échantillon", type="primary", use_container_width=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">ÉCHELLE DE CLASSIFICATION</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="scale-legend">
            <span style="background:#C24A42;"></span>
            <span style="background:#C9822C;"></span>
            <span style="background:#2FAAB8;"></span>
            <span style="background:#0E7C86;"></span>
        </div>
        <div class="scale-labels">
            <span>Risquée</span><span>Risque antibio.</span><span>Buvable</span><span>Potable</span>
        </div>
        <div class="mono" style="font-size:0.7rem; color:var(--muted); margin-top:4px;">
            Seuils : E.BLSE = 0 / &lt; 6 / ≥ 6 UFC·100mL⁻¹ · MES = 0 / &lt; 5 mg·L⁻¹ · DCO/DBO5 &lt; 5 · N/P ∈ [10,17]
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="eyebrow">DIAGNOSTIC</div>', unsafe_allow_html=True)
        label = classifier_eau(eblse_in, mes_in, dco_dbo_in, np_in)
        score = indice_indicatif(eblse_in, mes_in, dco_dbo_in, np_in)
        style = CLASSES[label]

        st.plotly_chart(build_gauge(score, label), use_container_width=True, config={"displayModeBar": False})

        st.markdown(f"""
        <div class="result-card" style="background:{style['soft']}; border:1px solid {style['color']}33;">
            <div class="eyebrow" style="color:{style['color']};">STATUT</div>
            <div style="font-size:1.35rem; font-weight:700; color:{style['text']}; margin-top:4px;">{label}</div>
            <div class="mono" style="font-size:0.78rem; color:var(--muted); margin-top:8px;">
                Indice indicatif&nbsp;: {score}/100 — classification officielle basée sur les seuils réglementaires ci-dessus.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 6. PAGE — ANALYSE DE CAMPAGNE
# ============================================================
else:
    uploaded_file = st.file_uploader("Importer le classeur Excel de campagne (`donnees_simulees.xlsx`)", type=["xlsx"])

    if uploaded_file is not None:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        default_index = sheet_names.index('données') if 'données' in sheet_names else 0

        st.markdown('<div class="eyebrow">FEUILLE DE CALCUL</div>', unsafe_allow_html=True)
        sel_col, count_col = st.columns([2, 2])
        with sel_col:
            selected_sheet = st.selectbox(
                "Choisir une feuille du classeur :",
                options=sheet_names,
                index=default_index,
            )
        with count_col:
            st.markdown(f"""
            <div class="mono" style="font-size:0.78rem; color:var(--muted); margin-top:30px;">
                {len(sheet_names)} feuille(s) détectée(s) dans le classeur
            </div>
            """, unsafe_allow_html=True)

        REQUIRED_COLS = ['Date', 'Site', 'Lieu', 'Source', 'Saison', 'MES ', 'DCO.DBOn', 'N.P']
        raw_df = pd.read_excel(xls, sheet_name=selected_sheet)
        missing = [c for c in REQUIRED_COLS if c not in raw_df.columns]

        if missing:
            st.markdown(f"""
            <div class="param-card" style="border-left:4px solid var(--coral); text-align:left; padding:20px 22px;">
                <div class="eyebrow" style="color:var(--coral);">⚠️ FEUILLE INCOMPATIBLE</div>
                <div style="font-weight:600; margin-top:6px;">La feuille « {selected_sheet} » ne contient pas les colonnes attendues.</div>
                <div class="mono" style="font-size:0.78rem; color:var(--muted); margin-top:8px;">
                    Colonnes manquantes : {", ".join(missing)}<br>
                    Colonnes disponibles : {", ".join(raw_df.columns.astype(str))}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.stop()

        df = raw_df.copy()
        df['Date'] = pd.to_datetime(df['Date'])

        df['Classification'] = [
            classifier_eau(r.get('Ec.BLSE (UFC/100ml)', 0), r['MES '], r['DCO.DBOn'], r['N.P'])
            for _, r in df.iterrows()
        ]
        df['Indice'] = [
            indice_indicatif(r.get('Ec.BLSE (UFC/100ml)', 0), r['MES '], r['DCO.DBOn'], r['N.P'])
            for _, r in df.iterrows()
        ]

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">FILTRES DE CAMPAGNE</div>', unsafe_allow_html=True)
        col_date, col_cat = st.columns([1, 2])
        with col_date:
            min_d, max_d = df['Date'].min().date(), df['Date'].max().date()
            date_range = st.date_input("Période d'analyse :", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        with col_cat:
            cat_options = ["Tous", "Eau potable", "Eau buvable", "Exposée aux risques d'antibiorésistance", "Eau risquée"]
            selected_cat = st.segmented_control("Catégorie de qualité :", options=cat_options, default="Tous")

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]

        filtered_df = df if selected_cat == "Tous" else df[df['Classification'] == selected_cat]

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        tot = len(df) if len(df) > 0 else 1
        kpi_defs = [
            ("Eau potable", "💧"),
            ("Eau buvable", "🚰"),
            ("Exposée aux risques d'antibiorésistance", "⚠️"),
            ("Eau risquée", "⛔"),
        ]
        kcols = st.columns(4)
        for kcol, (cat, icon) in zip(kcols, kpi_defs):
            n = (df['Classification'] == cat).sum()
            pct = n / tot
            color = CLASSES[cat]["color"]
            short = "Risque antibio." if "antibio" in cat else cat
            with kcol:
                st.markdown(f"""
                <div class="kpi-card" style="border-left-color:{color};">
                    <div class="eyebrow">{icon}&nbsp; {short.upper()}</div>
                    <div class="kpi-value">{n}</div>
                    <div class="kpi-sub">{pct:.1%} de la campagne</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

        text_style = dict(color="#0A2A3D", family="Inter")
        color_map = {k: v["color"] for k, v in CLASSES.items()}

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown('<div class="eyebrow">RÉPARTITION PAR CATÉGORIE</div>', unsafe_allow_html=True)
            fig_pie = px.pie(filtered_df, names='Classification', hole=0.62, template='plotly_white', color='Classification', color_discrete_map=color_map)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=text_style, legend=dict(font=text_style), margin=dict(t=10, b=10))
            fig_pie.update_traces(marker=dict(line=dict(color='#F4F7F8', width=2)))
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        with chart_col2:
            st.markdown('<div class="eyebrow">RÉPARTITION PAR SITE</div>', unsafe_allow_html=True)
            fig_bar = px.histogram(filtered_df, x='Site', color='Classification', barmode='group', template='plotly_white', color_discrete_map=color_map)
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=text_style,
                legend=dict(font=text_style), margin=dict(t=10, b=10),
                xaxis=dict(tickfont=text_style, title=dict(font=text_style), gridcolor='#EAEFF0'),
                yaxis=dict(tickfont=text_style, title=dict(font=text_style), gridcolor='#EAEFF0'),
                bargap=0.25,
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="eyebrow">ÉVOLUTION DE L\'INDICE INDICATIF DANS LE TEMPS</div>', unsafe_allow_html=True)
        trend = filtered_df.sort_values('Date').groupby(['Date', 'Site'], as_index=False)['Indice'].mean()
        fig_trend = px.line(trend, x='Date', y='Indice', color='Site', markers=True, template='plotly_white')
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=text_style, height=320,
            legend=dict(font=text_style), margin=dict(t=10, b=10),
            xaxis=dict(tickfont=text_style, title=dict(font=text_style), gridcolor='#EAEFF0'),
            yaxis=dict(tickfont=text_style, title=dict(text="Indice /100", font=text_style), gridcolor='#EAEFF0', range=[0, 100]),
        )
        fig_trend.add_hrect(y0=80, y1=100, fillcolor="#0E7C86", opacity=0.06, line_width=0)
        fig_trend.add_hrect(y0=0, y1=25, fillcolor="#C24A42", opacity=0.06, line_width=0)
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        table_col, dl_col = st.columns([4, 1])
        with table_col:
            st.markdown(f'<div class="eyebrow">REGISTRE D\'ÉCHANTILLONS · {len(filtered_df)} LIGNES</div>', unsafe_allow_html=True)
        with dl_col:
            st.download_button(
                "⭳ Exporter (CSV)",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name=f"aequa_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.dataframe(
            filtered_df[['Site', 'Lieu', 'Source', 'Date', 'Saison', 'MES ', 'DCO.DBOn', 'N.P', 'Classification', 'Indice']],
            use_container_width=True,
            column_config={
                "Indice": st.column_config.ProgressColumn("Indice", min_value=0, max_value=100, format="%d"),
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            },
        )
    else:
        st.markdown("""
        <div class="param-card" style="text-align:center; padding:40px 20px;">
            <div style="font-size:2rem;">📄</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.05rem; margin-top:8px;">
                Aucune campagne chargée
            </div>
            <div class="mono" style="color:var(--muted); font-size:0.82rem; margin-top:4px;">
                Importez un fichier .xlsx pour afficher les indicateurs, graphiques et le registre d'échantillons.
            </div>
        </div>
        """, unsafe_allow_html=True)

