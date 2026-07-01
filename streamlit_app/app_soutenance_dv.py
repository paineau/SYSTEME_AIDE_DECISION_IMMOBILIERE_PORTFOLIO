import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from PIL import Image

st.set_page_config(
    page_title="Comprendre la formation des prix immobiliers",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
.hero-box {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 62%, #60a5fa 100%);
    color: white;
    padding: 2rem;
    border-radius: 18px;
    margin-bottom: 1.2rem;
}
.hero-title {font-size: 2.25rem; font-weight: 800; margin-bottom: 0.45rem;}
.hero-subtitle {font-size: 1.08rem; line-height: 1.55;}
.big-question {
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-left:7px solid #2563eb;
    border-radius:14px;
    padding:1.2rem 1.4rem;
    font-size:1.05rem;
    line-height:1.6;
    margin:1rem 0;
}
.card {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:1rem;
    box-shadow:0 2px 10px rgba(15,23,42,0.05);
    height:100%;
}
.card h4 {margin-top:0; color:#0f172a;}
.note {color:#475569; font-size:0.92rem;}
.flow {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:1rem;
    margin:0.4rem 0;
    text-align:center;
    font-weight:700;
}
.arrow {text-align:center; font-size:1.6rem; color:#2563eb; margin:-0.15rem 0;}
.conclusion {
    background:#eff6ff;
    border:1px solid #bfdbfe;
    border-radius:14px;
    padding:1rem 1.2rem;
    margin:0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name == "streamlit_app":
    PROJECT_ROOT = PROJECT_ROOT.parent

def first_existing(candidates):
    for p in candidates:
        if Path(p).exists():
            return Path(p)
    return None

def first_col_existing(data, candidates):
    for c in candidates:
        if c in data.columns:
            return c
    return None

def normalise_type(x):
    t = str(x).upper()
    if "APPART" in t:
        return "Appartement"
    if "MAISON" in t:
        return "Maison"
    return str(x)

def radius_policy_km(metropole, mode="strict"):
    metropole = str(metropole)
    if mode == "strict":
        if metropole == "Paris":
            return 0.30
        if metropole in ["Lyon", "Lille"]:
            return 0.40
        if metropole == "Marseille":
            return 0.50
        return 0.60
    if metropole == "Paris":
        return 0.50
    if metropole in ["Lyon", "Lille"]:
        return 0.60
    if metropole == "Marseille":
        return 0.80
    return 1.00

def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(float(lat1))
    lon1 = np.radians(float(lon1))
    lat2 = np.radians(pd.to_numeric(lat2, errors="coerce"))
    lon2 = np.radians(pd.to_numeric(lon2, errors="coerce"))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))

def fallback_pool():
    return pd.DataFrame({
        "date_mutation": [
            "2025-09-23", "2024-04-22", "2021-06-01", "2024-09-25", "2024-10-10", "2023-12-01",
            "2025-03-14", "2024-07-03", "2023-05-18", "2025-01-11", "2022-11-08", "2024-12-06",
            "2025-05-17", "2023-09-21", "2024-02-12", "2025-06-02"
        ],
        "nom_commune": ["PARIS 16E ARRONDISSEMENT"] * 16,
        "code_iris": ["751166409"] * 16,
        "type_bien": ["Appartement"] * 16,
        "surface_reference": [76.88, 84.43, 84.54, 85.28, 66.00, 80.04, 92.20, 97.60, 101.40, 108.00, 118.50, 126.20, 54.00, 62.50, 143.00, 155.00],
        "nb_pieces_total": [4, 4, 4, 4, 3, 4, 4, 4, 5, 5, 5, 5, 2, 3, 6, 6],
        "prix_m2": [7540, 7110, 6620, 8020, 7350, 7860, 7740, 7950, 8120, 7680, 7440, 7310, 8300, 7600, 7100, 6950],
        "distance_km": [0.12, 0.18, 0.22, 0.25, 0.28, 0.30, 0.16, 0.21, 0.27, 0.29, 0.34, 0.42, 0.19, 0.31, 0.46, 0.58],
        "latitude": [48.869] * 16,
        "longitude": [2.285] * 16,
        "source": ["démonstration"] * 16,
    })

@st.cache_data(show_spinner=False)
def load_transaction_pool():
    candidates = [
        PROJECT_ROOT / "outputs" / "feature_store_modelisation_taux" / "tables" / "dataset_modelisation_selected_taux.parquet",
        PROJECT_ROOT / "data" / "processed" / "dataset_modelisation_selected_taux.parquet",
        PROJECT_ROOT / "outputs" / "demo_streamlit" / "comparables_demo.csv",
    ]
    found = first_existing(candidates)
    if found is None:
        return fallback_pool(), "mode démonstration intégré"

    try:
        if found.suffix.lower() == ".parquet":
            df = pd.read_parquet(found)
        else:
            df = pd.read_csv(found)
    except Exception:
        return fallback_pool(), "mode démonstration intégré"

    col_prix = first_col_existing(df, ["prix_m2", "prix_m2_obs", "prix_m2_model", "prix_m2_net"])
    col_surface = first_col_existing(df, ["surface_reference", "surface_reference_model", "surface_reelle_bati", "surface_carrez", "surface"])
    col_commune = first_col_existing(df, ["nom_commune", "commune", "libelle_commune"])
    col_iris = first_col_existing(df, ["code_iris", "iris", "CODE_IRIS"])
    col_type = first_col_existing(df, ["type_bien", "type_local", "segment_bien"])
    col_date = first_col_existing(df, ["date_mutation", "date", "date_reference"])
    col_pieces = first_col_existing(df, ["nb_pieces_total", "nombre_pieces_principales", "pieces"])
    col_lat = first_col_existing(df, ["latitude", "lat", "y"])
    col_lon = first_col_existing(df, ["longitude", "lon", "lng", "x"])

    if col_prix is None or col_surface is None:
        return fallback_pool(), "mode démonstration intégré"

    work = pd.DataFrame()
    work["prix_m2"] = pd.to_numeric(df[col_prix], errors="coerce")
    work["surface_reference"] = pd.to_numeric(df[col_surface], errors="coerce")
    work["nom_commune"] = df[col_commune].astype(str) if col_commune else ""
    work["code_iris"] = df[col_iris].astype(str) if col_iris else ""
    work["type_bien"] = df[col_type].apply(normalise_type) if col_type else ""
    work["date_mutation"] = pd.to_datetime(df[col_date], errors="coerce") if col_date else pd.NaT
    work["nb_pieces_total"] = pd.to_numeric(df[col_pieces], errors="coerce") if col_pieces else np.nan
    work["latitude"] = pd.to_numeric(df[col_lat], errors="coerce") if col_lat else np.nan
    work["longitude"] = pd.to_numeric(df[col_lon], errors="coerce") if col_lon else np.nan

    if "demo_metropole" in df.columns:
        work["metropole"] = df["demo_metropole"].astype(str)
    else:
        work["metropole"] = np.where(work["nom_commune"].str.upper().str.contains("PARIS", na=False), "Paris", "")

    work = work.dropna(subset=["prix_m2", "surface_reference"])
    work = work[(work["prix_m2"] > 300) & (work["prix_m2"] <= 45000)]
    work["source"] = str(found.relative_to(PROJECT_ROOT)) if str(found).startswith(str(PROJECT_ROOT)) else str(found)

    if work.empty:
        return fallback_pool(), "mode démonstration intégré"
    return work, work["source"].iloc[0]

def default_case():
    return {
        "adresse": "10 avenue Victor Hugo",
        "cp": "75116",
        "metropole": "Paris",
        "commune": "PARIS 16",
        "iris": "751166409",
        "type_bien": "Appartement",
        "surface": 85.0,
        "pieces": 4,
        "dependance": "Non",
        "terrain": 0.0,
        "date_ref": pd.Timestamp.today().date(),
        "rayon_mode": "strict",
        "tolerance": 30,
        "valorisation_lancee": False,
    }

for k, v in default_case().items():
    st.session_state.setdefault(k, v)

def compute_comparables(params, n=30):
    pool, source = load_transaction_pool()
    comps = pool.copy()
    steps = []

    def apply_filter(mask, label, min_n=5):
        nonlocal comps
        candidate = comps[mask].copy()
        kept = len(candidate) >= min_n
        steps.append({"Filtre": label, "Effectif": int(len(candidate)), "Conservé": "Oui" if kept else "Non"})
        if kept:
            comps = candidate

    metropole = params["metropole"]
    commune = params["commune"]
    iris = params["iris"]
    type_bien = params["type_bien"]
    surface = float(params["surface"])
    pieces = int(params["pieces"])
    tolerance = float(params["tolerance"])
    date_ref = pd.Timestamp(params["date_ref"])
    rayon = radius_policy_km(metropole, params["rayon_mode"])

    if "metropole" in comps.columns and metropole:
        apply_filter(comps["metropole"].astype(str).eq(str(metropole)), f"métropole = {metropole}", 10)
    if commune:
        commune_key = str(commune).upper().replace(" ARRONDISSEMENT", "")
        apply_filter(comps["nom_commune"].astype(str).str.upper().str.contains(commune_key, regex=False, na=False), f"commune contient {commune}", 5)
    if iris:
        apply_filter(comps["code_iris"].astype(str).eq(str(iris)), f"IRIS = {iris}", 5)
    if type_bien:
        apply_filter(comps["type_bien"].apply(normalise_type).eq(type_bien), f"type = {type_bien}", 5)

    if "date_mutation" in comps.columns:
        d = pd.to_datetime(comps["date_mutation"], errors="coerce")
        if d.notna().any():
            apply_filter(d.le(date_ref), "antériorité temporelle", 5)

    surface_min = surface * (1 - tolerance / 100)
    surface_max = surface * (1 + tolerance / 100)
    apply_filter(
        pd.to_numeric(comps["surface_reference"], errors="coerce").between(surface_min, surface_max),
        f"surface entre {surface_min:.1f} et {surface_max:.1f} m²",
        5,
    )

    if "distance_km" not in comps.columns:
        comps["distance_km"] = np.nan

    if comps["distance_km"].notna().any():
        geo = comps[pd.to_numeric(comps["distance_km"], errors="coerce").le(rayon)].copy()
        steps.append({"Filtre": f"rayon ≤ {rayon:.2f} km", "Effectif": int(len(geo)), "Conservé": "Oui" if len(geo) >= 5 else "Non"})
        if len(geo) >= 5:
            comps = geo

    comps = comps.copy()
    comps["distance_surface"] = (pd.to_numeric(comps["surface_reference"], errors="coerce") - surface).abs() / max(surface, 1)
    comps["distance_pieces"] = (pd.to_numeric(comps["nb_pieces_total"], errors="coerce") - pieces).abs()
    comps["age_jours"] = (date_ref - pd.to_datetime(comps["date_mutation"], errors="coerce")).dt.days.clip(lower=0)
    comps["distance_km"] = pd.to_numeric(comps["distance_km"], errors="coerce")

    rank_surface = comps["distance_surface"].rank(pct=True, method="average")
    rank_pieces = comps["distance_pieces"].fillna(comps["distance_pieces"].median()).rank(pct=True, method="average")
    rank_age = comps["age_jours"].fillna(comps["age_jours"].median()).rank(pct=True, method="average")
    rank_geo = comps["distance_km"].fillna(comps["distance_km"].median()).rank(pct=True, method="average")

    penalty = 0.35 * rank_surface + 0.20 * rank_pieces + 0.25 * rank_age + 0.20 * rank_geo
    comps["score_comparabilite"] = (1 - penalty).clip(0, 1).round(2)

    cols = ["date_mutation", "nom_commune", "code_iris", "type_bien", "surface_reference", "nb_pieces_total", "prix_m2", "distance_km", "score_comparabilite"]
    result = comps.sort_values(["score_comparabilite", "distance_surface"], ascending=[False, True]).head(n)
    result = result[[c for c in cols if c in result.columns]].copy()
    result["date_mutation"] = pd.to_datetime(result["date_mutation"], errors="coerce").dt.strftime("%Y-%m-%d")
    return result, pd.DataFrame(steps), source, rayon

def compute_estimation(params):
    comps, steps, source, rayon = compute_comparables(params, n=30)
    surface = float(params["surface"])
    prix = pd.to_numeric(comps["prix_m2"], errors="coerce").dropna()
    if len(prix):
        prix_m2 = float(prix.median())
        q25 = float(prix.quantile(0.25))
        q75 = float(prix.quantile(0.75))
    else:
        prix_m2, q25, q75 = 7860, 5109, 10611
    confiance = int(np.clip(45 + min(len(prix), 30) * 1.2 - abs(float(params["tolerance"]) - 30) * 0.2, 42, 88))
    return {
        "prix_m2": prix_m2,
        "valeur": prix_m2 * surface,
        "low": q25,
        "high": q75,
        "valeur_low": q25 * surface,
        "valeur_high": q75 * surface,
        "confiance": confiance,
        "n_comparables": len(comps),
        "comps": comps,
        "steps": steps,
        "source": source,
        "rayon": rayon,
    }


image_candidates = [
    PROJECT_ROOT / "streamlit_app" / "Illustration_compagnon immo.png",
    PROJECT_ROOT / "Illustration_compagnon immo.png",
    Path("streamlit_app") / "Illustration_compagnon immo.png",
    Path("Illustration_compagnon immo.png"),
    PROJECT_ROOT / "streamlit_app" / "image_soutenance.png",
    PROJECT_ROOT / "image_soutenance.png",
    Path("image_soutenance.png"),
    PROJECT_ROOT / "streamlit_app" / "image.png",
    PROJECT_ROOT / "image.png",
    Path("image.png"),
]
hero_img = None
for img_path in image_candidates:
    if img_path.exists():
        hero_img = Image.open(img_path)
        break

pipeline_df = pd.DataFrame({
    "Étape": [
        "Lignes DVF brutes",
        "Mutations reconstruites",
        "Transactions résidentielles",
        "Mutations après nettoyage",
        "Base enrichie"
    ],
    "Volume": [20382915, 7319609, 4019581, 3925350, 3885803]
})

familles_df = pd.DataFrame({
    "Famille": ["B1 – Bien", "B2 – Temporalité", "B3 – Territoire", "B4 – Socio-économie", "B5 – Comparables", "B6 – Financement"],
    "Question métier": [
        "Que décrit le logement lui-même ?",
        "À quel moment du cycle la transaction intervient-elle ?",
        "Dans quel environnement territorial le bien s’inscrit-il ?",
        "Quel est le profil socio-économique du territoire ?",
        "Que disent les ventes réellement comparables déjà observées ?",
        "Quelles sont les conditions de financement du marché ?"
    ],
    "Exemples de variables": [
        "surface, pièces, type de bien, dépendances, terrain",
        "année, trimestre, saisonnalité, ancienneté, dynamique récente",
        "commune, IRIS, typologie de marché, liquidité, tension",
        "revenus, densité, équipements, structure résidentielle",
        "prix médians passés, rayon, récence, profondeur, scores",
        "taux, variations, tension macro-financière"
    ]
})

resultats_df = pd.DataFrame({
    "Scénario": [
        "B1 seul",
        "B1 + B2",
        "B1 + B3",
        "B1 + B2 + B3 + B4",
        "B5 seul",
        "B1 + B5",
        "Scénario complet",
        "Version optimisée"
    ],
    "R²": [0.128, 0.127, 0.576, 0.681, 0.592, 0.737, 0.745, 0.7567],
    "MAE (€/m²)": [1198, None, 840, 716, 831, 638, 627, 611],
    "RMSE (€/m²)": [1760, None, None, None, None, None, 951, 929]
})

split_resume_df = pd.DataFrame({
    "Validation": ["Split aléatoire", "Split temporel 2025", "Split temporel 2025 avec taux"],
    "Finalité": [
        "Pouvoir explicatif moyen des variables",
        "Généralisation sur une année future",
        "Généralisation avec conditions de financement"
    ],
    "R²": [0.756733, 0.749782, 0.752836],
    "MAE (€/m²)": [611.285624, 616.593589, 612.568414],
    "RMSE (€/m²)": [929.473570, 936.172629, 930.442315]
})

split_graph_df = pd.DataFrame({
    "Scénario": [
        "B1 seul",
        "B1+B2",
        "B1+B3",
        "B1+B4",
        "B5 seul",
        "B1+B5",
        "B1+B2+B5",
        "B1+B2+B3+B4",
        "Complet",
        "Complet+taux"
    ],
    "Split aléatoire": [0.127538, 0.126542, 0.576123, 0.666464, 0.591448, 0.736626, 0.736200, 0.680950, 0.756733, 0.756389],
    "Split temporel 2025": [0.133293, 0.144627, 0.575969, 0.662830, 0.583604, 0.738026, 0.731783, 0.676454, 0.749782, 0.752836]
})

split_graph_long_df = split_graph_df.melt(
    id_vars="Scénario",
    value_vars=["Split aléatoire", "Split temporel 2025"],
    var_name="Stratégie",
    value_name="R²"
)

comparables_reels_df = pd.DataFrame({
    "date_mutation": ["2025-09-23", "2024-04-22", "2021-06-01", "2024-09-25", "2024-10-10", "2023-12-01"],
    "nom_commune": ["PARIS 16E ARRONDISSEMENT"] * 6,
    "code_iris": ["751166409"] * 6,
    "type_bien": ["Appartement"] * 6,
    "surface_reference": [76.88, 84.43, 84.54, 85.28, 66.00, 80.04],
    "nb_pieces_total": [4, 4, 4, 4, 3, 4],
    "prix_m2": [7540, 7110, 6620, 8020, 7350, 7860],
    "distance_km": [0.12, 0.18, 0.22, 0.25, 0.28, 0.30],
    "score_comparabilite": [0.94, 0.92, 0.88, 0.91, 0.85, 0.90]
})

pool_filters_df = pd.DataFrame({
    "Filtre": ["métropole = Paris", "commune = PARIS 16E ARRONDISSEMENT", "IRIS = 751166409", "type = Appartement", "antériorité temporelle", "surface ±35%"],
    "Effectif": [120776, 9034, 163, 163, 163, 39]
})

metropoles_df = pd.DataFrame({
    "Métropole": ["Paris", "Marseille", "Toulouse", "Nice", "Lyon", "Nantes", "Montpellier", "Bordeaux", "Lille", "Rennes"],
    "Transactions": [120937, 62300, 40165, 38700, 35368, 26580, 23864, 23339, 18489, 17250],
    "Prix médian (€/m²)": [6586, 2739, 3049, 3979, 3350, 3467, 3066, 4525, 3170, 3422],
    "Q25": [4864, 1644, 2239, 2550, 2185, 2200, 1958, 3596, 2249, 1997],
    "Q75": [9501, 3958, 2239, 5346, 5095, 4392, 3973, 5486, 4180, 4501],
    "Surface médiane": [64, 69, 64, 62, 84, 70, 66, 65, 66, 73],
    "Revenu médian réel (€)": [32420, 21570, 23240, 21950, 26160, 25850, 21360, 25700, 23350, 25080]
})

perf_metropoles_df = pd.DataFrame({
    "Métropole": ["Toulouse", "Montpellier", "Rennes", "Lille", "Nantes", "Lyon", "Marseille", "Bordeaux", "Nice", "Paris"],
    "n_test": [7888, 4512, 3354, 3454, 4951, 6787, 11693, 4504, 7410, 24891],
    "MAE": [548, 549, 598, 599, 599, 732, 735, 833, 904, 1323],
    "MAPE": [20.6, 21.9, 21.9, 23.9, 22.3, 23.4, 26.5, 24.0, 24.7, 26.3],
    "R²": [0.686, 0.657, 0.703, 0.594, 0.647, 0.618, 0.602, 0.393, 0.611, 0.544]
})

st.sidebar.title("Support de soutenance")
st.sidebar.caption("Version finale V8")
page = st.sidebar.radio(
    "Parcours",
    [
        "1. Problématique",
        "2. De la donnée administrative à la base analytique",
        "3. Formalisation du raisonnement métier",
        "4. Scénarios et résultats",
        "5. Pouvoir prédictif",
        "6. Démonstration – Saisie du bien",
        "7. Démonstration – Estimation",
        "8. Démonstration – Territoire homogène",
        "9. Démonstration – Comparables",
        "10. Démonstration – Marchés et métropoles"
    ],
    key="parcours_soutenance_v9_finale"
    )

if page == "1. Problématique":
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Comprendre la formation des prix immobiliers</div>
        <div class="hero-subtitle">Quand la donnée rencontre l’expertise immobilière.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="big-question">
    Comment formaliser, à partir des données de transactions, une approche de la valorisation immobilière
    qui soit à la fois solide sur le plan analytique, explicable dans ses mécanismes et pertinente au regard
    des pratiques professionnelles ?
    <br><br>
    L’objectif n’est pas seulement de prédire un prix, mais de comprendre ce qui le produit afin d’en apprécier
    la justesse et la capacité de projection.
    </div>
    """, unsafe_allow_html=True)

    # --- Blocs corrigés (remplacement de l'image) ---
    c1, c2, c3 = st.columns(3)

    c1.markdown(
        '<div class="card"><h4>Compréhension</h4>'
        '<p>Identifier les mécanismes qui structurent la valeur.</p></div>',
        unsafe_allow_html=True
    )

    c2.markdown(
        '<div class="card"><h4>Formalisation</h4>'
        '<p>Traduire l’expertise immobilière en variables exploitables.</p></div>',
        unsafe_allow_html=True
    )

    c3.markdown(
        '<div class="card"><h4>Mesure</h4>'
        '<p>Comparer la contribution réelle de chaque famille d’information.</p></div>',
        unsafe_allow_html=True
    )


elif page == "2. De la donnée administrative à la base analytique":
    st.title("De la donnée administrative à la base analytique")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("DVF brut", "20,4 M lignes")
    c2.metric("Mutations", "7,32 M")
    c3.metric("Résidentiel", "4,02 M")
    c4.metric("Nettoyé", "3,93 M")
    c5.metric("Base enrichie", "3,89 M")

    fig = px.funnel(pipeline_df, x="Volume", y="Étape")
    fig.update_layout(height=460, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Chaîne méthodologique")
    steps = [
        "DVF : donnée administrative brute",
        "Reconstruction de l’unité économique de mutation",
        "Sélection du résidentiel secondaire",
        "Contrôles qualité et bornes métier",
        "Enrichissements externes : INSEE, IRIS, DPE, taux",
        "Feature Store immobilier : familles B1 à B6",
        "Scénarios analytiques et validation"
    ]
    for index, step in enumerate(steps):
        st.markdown(f'<div class="flow">{step}</div>', unsafe_allow_html=True)
        if index < len(steps) - 1:
            st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)

elif page == "3. Formalisation du raisonnement métier":
    st.title("Formalisation du raisonnement métier")

    st.markdown("""
    <div class="big-question">
    Explorer et formaliser les principaux mécanismes de valorisation immobilière consiste à transformer
    des raisonnements métier en variables mesurables, comparables et auditables.
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(familles_df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="conclusion">
    Chaque famille de variables représente une hypothèse sur la formation de la valeur :
    le bien, le temps, le territoire, la socio-économie, les comparables et les conditions de financement.
    </div>
    """, unsafe_allow_html=True)

elif page == "4. Scénarios et résultats":
    st.title("Évaluer ce qui explique réellement la formation du prix")

    st.markdown("""
    <div class="big-question">
    L’objectif n’est pas seulement de mesurer la performance prédictive d’un modèle,
    mais d’identifier ce qui explique réellement la formation du prix.
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(resultats_df, use_container_width=True, hide_index=True)

    fig = px.bar(
        resultats_df.sort_values("R²"),
        x="R²",
        y="Scénario",
        orientation="h",
        text="R²",
        title="Contribution progressive des familles de variables"
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(height=520, xaxis_range=[0, 0.82])
    st.plotly_chart(fig, use_container_width=True)

elif page == "5. Pouvoir prédictif":
    st.title("Pouvoir prédictif")

    c1, c2, c3 = st.columns(3)
    c1.metric("R² optimisé aléatoire", "0,7567")
    c2.metric("R² temporel 2025", "0,7498")
    c3.metric("R² temporel avec taux", "0,7528")

    st.dataframe(split_resume_df, use_container_width=True, hide_index=True)

    fig = px.line(
        split_graph_long_df,
        x="Scénario",
        y="R²",
        color="Stratégie",
        markers=True,
        title="Comparaison des R² par scénario : split aléatoire et split temporel 2025"
    )
    fig.update_layout(height=520, xaxis_tickangle=-35, yaxis_range=[-0.1, 0.85])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="conclusion">
    La proximité entre split aléatoire et split temporel 2025 conforte la robustesse du dispositif.
    Le split aléatoire mesure le pouvoir explicatif moyen des variables ; le split temporel vérifie leur capacité
    à se généraliser sur une année future.
    </div>
    """, unsafe_allow_html=True)

elif page == "6. Démonstration – Saisie du bien":
    st.title("Saisir un bien")

    c1, c2, c3 = st.columns(3)
    st.session_state.adresse = c1.text_input("Adresse", st.session_state.adresse)
    st.session_state.cp = c2.text_input("Code postal", st.session_state.cp)
    st.session_state.metropole = c3.selectbox(
        "Métropole",
        ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Montpellier", "Bordeaux", "Lille", "Rennes"],
        index=["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Montpellier", "Bordeaux", "Lille", "Rennes"].index(st.session_state.metropole)
        if st.session_state.metropole in ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Montpellier", "Bordeaux", "Lille", "Rennes"] else 0
    )

    c4, c5, c6 = st.columns(3)
    st.session_state.commune = c4.text_input("Repli de la commune", st.session_state.commune)
    st.session_state.iris = c5.text_input("Repli IRIS", st.session_state.iris)
    st.session_state.type_bien = c6.selectbox("Type de bien", ["Appartement", "Maison"], index=0 if st.session_state.type_bien == "Appartement" else 1)

    c7, c8, c9 = st.columns(3)
    st.session_state.surface = c7.number_input("Surface m²", value=float(st.session_state.surface), min_value=9.0, max_value=500.0)
    st.session_state.pieces = c8.number_input("Nombre de pièces", value=int(st.session_state.pieces), min_value=1, max_value=12)
    st.session_state.dependance = c9.selectbox("Dépendance", ["Non", "Oui"], index=0 if st.session_state.dependance == "Non" else 1)

    c10, c11, c12 = st.columns(3)
    st.session_state.terrain = c10.number_input("Terrain m²", value=float(st.session_state.terrain), min_value=0.0)
    st.session_state.date_ref = c11.date_input("Date de référence", st.session_state.date_ref)
    st.session_state.rayon_mode = c12.selectbox("Rayon", ["strict", "standard"], index=0 if st.session_state.rayon_mode == "strict" else 1)

    st.session_state.tolerance = st.slider("Tolérance surface (%)", 10, 60, int(st.session_state.tolerance))
    rayon = radius_policy_km(st.session_state.metropole, st.session_state.rayon_mode)
    st.info(f"Rayon appliqué pour la démonstration : {rayon:.2f} km")

    if st.button("Lancer la valorisation"):
        st.session_state.valorisation_lancee = True
        st.session_state.resultat = compute_estimation(st.session_state)
        st.success("Valorisation recalculée avec les critères saisis.")

elif page == "7. Démonstration – Estimation":
    st.title("Estimation et fourchette")
    resultat = compute_estimation(st.session_state)

    m1, m2, m3 = st.columns(3)
    m1.metric("Prix estimé", f"{resultat['prix_m2']:,.0f} €/m²".replace(",", " "))
    m2.metric("Valeur estimée", f"{resultat['valeur']:,.0f} €".replace(",", " "))
    m3.metric("Confiance indicative", f"{resultat['confiance']} %")

    m4, m5, m6 = st.columns(3)
    m4.metric("Borne basse", f"{resultat['low']:,.0f} €/m²".replace(",", " "))
    m5.metric("Borne haute", f"{resultat['high']:,.0f} €/m²".replace(",", " "))
    m6.metric("Comparables retenus", str(resultat["n_comparables"]))

    st.caption(f"Source utilisée : {resultat['source']}")
    st.markdown("""
    <div class="conclusion">
    La valeur centrale est recalculée à partir du micro-marché retenu. La fourchette dépend de la dispersion des comparables.
    </div>
    """, unsafe_allow_html=True)

elif page == "8. Démonstration – Territoire homogène":
    st.title("Territoire homogène")
    resultat = compute_estimation(st.session_state)

    c1, c2, c3 = st.columns(3)
    c1.metric("Métropole", st.session_state.metropole)
    c2.metric("Commune", st.session_state.commune)
    c3.metric("IRIS", st.session_state.iris)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Pool final", str(resultat["n_comparables"]))
    d2.metric("Prix médian pool", f"{resultat['prix_m2']:,.0f} €/m²".replace(",", " "))
    d3.metric("Rayon", f"{resultat['rayon']:.2f} km")
    d4.metric("Tolérance surface", f"±{st.session_state.tolerance} %")

    st.dataframe(resultat["steps"], use_container_width=True, hide_index=True)

elif page == "9. Démonstration – Comparables":
    st.title("Comparables réels")
    resultat = compute_estimation(st.session_state)
    comparables = resultat["comps"]

    st.caption(
        f"Critères actifs : {st.session_state.surface:.0f} m², {st.session_state.pieces} pièces, "
        f"{st.session_state.type_bien}, tolérance ±{st.session_state.tolerance} %, rayon {resultat['rayon']:.2f} km."
    )
    st.dataframe(comparables, use_container_width=True, hide_index=True)

    if not comparables.empty:
        fig = px.scatter(
            comparables,
            x="distance_km",
            y="prix_m2",
            size="score_comparabilite",
            color="surface_reference",
            hover_data=["date_mutation", "nb_pieces_total", "score_comparabilite"],
            title="Comparables retenus : distance, prix et surface"
        )
        fig.add_hline(y=resultat["prix_m2"], line_dash="dot")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucun comparable exploitable avec ces critères. Élargir la tolérance ou le rayon.")

elif page == "10. Démonstration – Marchés et métropoles":
    st.title("Marchés et métropoles")
    st.dataframe(metropoles_df, use_container_width=True, hide_index=True)

    fig1 = px.bar(metropoles_df.sort_values("Prix médian (€/m²)", ascending=False), x="Métropole", y="Prix médian (€/m²)", title="Prix médian au m² par métropole")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(metropoles_df, x="Transactions", y="Prix médian (€/m²)", size="Transactions", hover_name="Métropole", title="Volume et niveau de prix")
    st.plotly_chart(fig2, use_container_width=True)


