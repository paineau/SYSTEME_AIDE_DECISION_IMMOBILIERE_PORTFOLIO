# Version finale - application de soutenance
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from PIL import Image
import unicodedata

st.set_page_config(
    page_title="Comprendre la formation des prix immobiliers",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
:root {
    --ink:#172033;
    --muted:#5c667a;
    --line:#dde3ee;
    --panel:#ffffff;
    --soft:#f6f8fb;
    --accent:#1f5fbf;
    --accent-2:#0f8b8d;
    --gold:#b7791f;
}
.block-container {padding-top: 1rem; padding-bottom: 2.4rem; max-width: 1280px;}
[data-testid="stSidebar"] {background:#f7f9fc; border-right:1px solid #e5eaf2;}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {color:var(--ink);}
h1 {font-size:2.05rem !important; color:var(--ink); letter-spacing:0; margin-bottom:.35rem;}
h2 {font-size:1.25rem !important; color:var(--ink); margin-top:1.2rem; padding-top:.35rem; border-top:1px solid var(--line);}
h3 {font-size:1.05rem !important; color:var(--ink);}
.hero-box {
    background: linear-gradient(135deg, #111827 0%, #173b72 58%, #0f8b8d 100%);
    color: white;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 1.2rem;
    box-shadow:0 18px 48px rgba(23,32,51,0.18);
}
.hero-title {font-size: 2.25rem; font-weight: 800; margin-bottom: 0.45rem; letter-spacing:0;}
.hero-subtitle {font-size: 1.08rem; line-height: 1.55; color:#eef5ff;}
.executive-kicker {color:var(--accent); font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.35rem;}
.big-question {
    background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);
    border:1px solid var(--line);
    border-left:6px solid var(--accent);
    border-radius:8px;
    padding:1.15rem 1.35rem;
    font-size:1.06rem;
    line-height:1.62;
    margin:1rem 0 1.1rem 0;
    color:var(--ink);
    box-shadow:0 8px 22px rgba(23,32,51,0.06);
}
.card {
    background:white;
    border:1px solid var(--line);
    border-radius:8px;
    padding:1rem;
    box-shadow:0 8px 24px rgba(23,32,51,0.05);
    height:100%;
}
.card h4 {margin:.05rem 0 .45rem 0; color:var(--ink); font-size:1rem;}
.card p {color:var(--muted); line-height:1.48; margin-bottom:0;}
.note {color:var(--muted); font-size:0.92rem;}
.flow {
    background:white;
    border:1px solid var(--line);
    border-radius:8px;
    padding:1rem;
    margin:0.4rem 0;
    text-align:center;
    font-weight:700;
}
.arrow {text-align:center; font-size:1.6rem; color:var(--accent); margin:-0.15rem 0;}
.conclusion {
    background:#f5f9ff;
    border:1px solid #c8dcff;
    border-left:6px solid var(--accent-2);
    border-radius:8px;
    padding:1rem 1.2rem;
    margin:1rem 0 .8rem 0;
    color:var(--ink);
    line-height:1.55;
    font-weight:600;
}
.objective-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.85rem; margin:1rem 0 1.3rem 0;}
.objective-card {background:#fff; border:1px solid var(--line); border-radius:8px; padding:1rem; box-shadow:0 7px 20px rgba(23,32,51,.05);}
.objective-card b {display:block; color:var(--accent); margin-bottom:.38rem; font-size:.92rem;}
.objective-card span {display:block; color:var(--ink); line-height:1.42; font-size:.95rem;}
.section-lead {color:var(--muted); margin:.1rem 0 1rem 0; font-size:1rem; line-height:1.5;}
.img-card {
    background:white;
    border:1px solid var(--line);
    border-radius:8px;
    padding:0.7rem;
    box-shadow:0 8px 24px rgba(23,32,51,0.06);
    margin:0.35rem 0 1.05rem 0;
}
.img-card img {
    display:block;
    max-width:100%;
    height:auto;
    margin:auto;
    border-radius:6px;
}
.img-caption {
    text-align:center;
    color:var(--muted);
    font-size:0.82rem;
    margin-top:0.35rem;
}
@media (max-width: 900px) {
    .objective-grid {grid-template-columns:1fr;}
    .hero-title {font-size:1.65rem;}
    h1 {font-size:1.65rem !important;}
}
</style>
""", unsafe_allow_html=True)

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

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


IMAGE_DIR_CANDIDATES = [
    APP_DIR,
    Path.cwd(),
    PROJECT_ROOT / "streamlit_app",
    PROJECT_ROOT,
]

PAGE_IMAGES = {
    "1. Problématique": [
        "image_soutenance.png", "image_soutenance.jpg", "image_soutenance.jpeg",
        "01_page_de_garde.png", "page_de_garde.png", "page_de_garde.jpg", "page_de_garde.jpeg"
    ],
    "2. De la donnée administrative à la base analytique": [
        "02_mutations_temps.png", "02_mutation_temps.png",
        "03_mutation_temps_territoire.png", "03_mutations_temps_territoire.png", "02_mutation_temps_territoire.png",
        "04_transformation_dvf.png",
        "05_boxplot_résidentiel.png", "05_boxplot_residentiel.png",
    ],
    "3. Formalisation du raisonnement métier": [
        "06_illustration_territoire.png",
        "06_démarche_comparable.png", "06_demarche_comparable.png",
        "07_sélection_données.png", "07_selection_donnees.png", "07_sélection _données.png",
    ],
    "4. Sélection, scénarios et résultats": [
        "07_selection.png", "07_sélection.png",
        "07_scenario.png", "07_scénario.png",
        "08_contribution_famille.png",
    ],
    "5. Pouvoir prédictif": [
        "08_robustesse.png", "08_robustesse.jpg",
        "10_résidus.png", "10_residus.png",
        "11_antifuite.png", "11_anti_fuite.png",
    ],
    "10. Démonstration – Marchés et métropoles": ["05_boxplot_résidentiel.png", "05_boxplot_residentiel.png"],
}

def normalise_filename(name):
    return unicodedata.normalize("NFC", name).casefold()

def find_image(filename):
    for base in IMAGE_DIR_CANDIDATES:
        candidate = base / filename
        if candidate.exists():
            return candidate
        if base.exists():
            expected = normalise_filename(filename)
            for item in base.iterdir():
                if item.is_file() and normalise_filename(item.name) == expected:
                    return item
    return None

def find_first_image(filenames):
    for filename in filenames:
        img = find_image(filename)
        if img is not None:
            return img
    return None

def show_safe_image(filenames, max_width_px=None, caption=None):
    img = find_first_image(filenames)
    if img is None:
        st.info("Image à déposer dans le dossier de l’application : " + " ou ".join(filenames))
        return False

    cap = caption if caption is not None else img.name
    caption_arg = cap if cap else None
    if max_width_px:
        st.image(str(img), width=int(max_width_px), caption=caption_arg)
    else:
        st.image(str(img), use_container_width=True, caption=caption_arg)
    return True

def show_page_images(page_name, max_width_px=None):
    displayed = set()
    for filename in PAGE_IMAGES.get(page_name, []):
        img = find_image(filename)
        if img is not None and img not in displayed:
            return show_safe_image([filename], max_width_px=max_width_px)
    return False

def show_image_group(filenames, width=None):
    return show_safe_image(filenames, max_width_px=width)

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

st.sidebar.title("Vers une valorisation experte augmentée ?")
st.sidebar.caption("Version finale")
page = st.sidebar.radio(
    "Parcours",
    [
        "1. Problématique",
        "2. De la donnée administrative à la base analytique",
        "3. Formalisation du raisonnement métier",
        "4. Sélection, scénarios et résultats",
        "5. Pouvoir prédictif",
        "6. Démonstration – Saisie du bien",
        "7. Démonstration – Estimation",
        "8. Démonstration – Territoire homogène",
        "9. Démonstration – Comparables",
        "10. Démonstration – Marchés et métropoles"
    ],
    key="parcours_soutenance_finale"
    )

if page == "1. Problématique":
    cover = find_first_image([
        "image_soutenance.png", "image_soutenance.jpg", "image_soutenance.jpeg",
        "01_page_de_garde.png", "page_de_garde.png", "page_de_garde.jpg", "page_de_garde.jpeg"
    ])
    if cover is not None:
        left, center, right = st.columns([0.7, 2.6, 0.7])
        with center:
            show_safe_image([
                "image_soutenance.png", "image_soutenance.jpg", "image_soutenance.jpeg",
                "01_page_de_garde.png", "page_de_garde.png", "page_de_garde.jpg", "page_de_garde.jpeg"
            ], max_width_px=912, caption="")
    else:
        st.info("Image à déposer dans le dossier de l’application : image_soutenance.png ou image_soutenance.jpg")

    st.title("1. Problématique")
    st.markdown('<div class="executive-kicker">Système d’aide à la décision immobilière</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="big-question">
    En matière immobilière, l’objectif n’est pas tant de prédire un prix. Il faut être en mesure de l'expliquer.<br>
    L'enjeu et l’intérêt du projet à mes yeux étaient donc d'articuler expertise métier, donnée transactionnelle et valorisation experte
    pour comprendre ce qui forme réellement la valeur, le traduire en variables exploitables, puis mesurer ce que chaque famille d'information
    apporte réellement à l'estimation.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="objective-grid">
        <div class="objective-card"><b>Métiers</b><span>Mobiliser les logiques de l'expertise immobilière et les adapter aux méthodes de la Data Science.</span></div>
        <div class="objective-card"><b>Données</b><span>Transformer la donnée transactionnelle en base analytique fiable et exploitable.</span></div>
        <div class="objective-card"><b>Valorisation experte</b><span>Produire une estimation cohérente, explicable et crédible en phase avec les pratiques professionnelles.</span></div>
        <div class="objective-card"><b>Comprendre</b><span>Comprendre avant de prédire ce qui structure la formation des prix.</span></div>
        <div class="objective-card"><b>Formaliser</b><span>Traduire le raisonnement métier en variables explicables et « auditables ».</span></div>
        <div class="objective-card"><b>Mesurer</b><span>Quantifier l'apport réel de chaque famille d'information dans la valeur immobilière.</span></div>
    </div>
    """, unsafe_allow_html=True)

elif page == "2. De la donnée administrative à la base analytique":
    st.title("2. De la donnée administrative à la base analytique")
    st.markdown('<p class="section-lead"><b>Problématique :</b> Passer d’une source administrative exhaustive à une base analytique exploitable, homogène et orientée métier.</p>', unsafe_allow_html=True)

    st.markdown("## 1. Famille de données")
    c1, c2 = st.columns(2)
    with c1:
        show_image_group(["02_mutation_temps.png", "02_mutations_temps.png"], width=520)
    with c2:
        show_image_group(["02_mutation_temp_territoire.png", "02_mutation_temps_territoire.png", "02_mutations_temps_territoire.png"], width=520)

    st.markdown("## 2. Illustration Territoire")
    show_image_group(["04_transformation_dvf.png"], width=980)

    st.markdown("## 3. De l’exhaustivité administrative à la pertinence analytique")
    show_image_group(["04_triangle_inversé.png", "04_triangle_inverse.png", "04_triangle_inversé.jpg", "04_triangle_inverse.jpg"], width=540)

    st.markdown("## 4. Visualisation du périmètre de l’analyse")
    show_image_group(["05_boxplot_résidentiel.png", "05_boxplot_residentiel.png", "05_boxplot_résidentiel.jpg", "05_boxplot_residentiel.jpg"], width=900)

    st.markdown("""
    <div class="conclusion">
    L’homogénéisation du marché résidentiel extrait de la DVF transforme les attributs du bien en véritables signaux économiques :
    précis, cohérents, et immédiatement mobilisables pour expliquer les prix.
    </div>
    """, unsafe_allow_html=True)

elif page == "3. Formalisation du raisonnement métier":
    st.title("3. Formalisation du raisonnement métier")
    st.markdown('<p class="section-lead"><b>Problématique :</b> Structurer le raisonnement de l’expert en familles de variables lisibles, contrôlables et mesurables.</p>', unsafe_allow_html=True)

    st.markdown("## 1. Famille de données")
    show_image_group([
        "05_familles_données.png",
        "05_familles_donnees.png",
        "05_Familles_données.png",
        "05_Famille données.png",
        "05_Famille donnees.png",
        "05_famille_données.png",
        "05_famille_donnees.png",
        "05_Famille_données.png",
        "05_Famille_donnees.png",
    ], width=960)

    st.markdown("## 2. Illustration Territoire")
    show_image_group([
        "06_illustration territoire.png",
        "06_illustration_territoire.png",
        "06_illustration territoire.jpg",
        "06_illustration_territoire.jpg",
    ], width=920)

    st.markdown("""
    <div class="conclusion">
    Le marché immobilier n'est pas un marché unique, mais une mosaïque de marchés locaux.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 3. Focus comparables")
    show_image_group([
        "05_base_comparable.png",
        "05_base comparable.png",
        "06_démarche_comparable.png",
        "06_demarche_comparable.png",
        "05_base_comparable.jpg",
        "05_base comparable.jpg",
    ], width=384)

elif page == "4. Sélection, scénarios et résultats":
    st.title("4. Sélection, scénarios et résultats")
    st.markdown('<p class="section-lead"><b>Problématique :</b> Comparez les scénarios pour objectiver ce que chaque famille d’information apporte à la précision finale.</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("## 1. Sélection")
        show_image_group([
            "07_selection.png",
            "07_sélection.png",
            "07_selection.jpg",
            "07_sélection.jpg",
        ], width=560)
    with c2:
        st.markdown("## 2. Scénarios")
        show_image_group([
            "07_scenarios.png",
            "07_scenario.png",
            "07_scénarios.png",
            "07_scénario.png",
            "07_scenarios.jpg",
            "07_scenario.jpg",
        ], width=560)

    st.markdown("## 3. Résultats et contribution de chaque famille")
    show_image_group([
        "08_contribution_famille.png",
        "08_contribution_familles.png",
        "08_contribution_famillespng.png",
        "08_contribution_famille.jpg",
    ], width=588)

    st.markdown("""
    <div class="conclusion">
    Le R² de 0,745 traduit une bonne capacité explicative : le modèle parvient à capturer environ 75 % de la variance du prix au m².
    L’écart très faible entre le R² train et test (0,0098) suggère une généralisation correcte, sans surapprentissage notable :
    les performances restent stables entre l’entraînement et la validation.<br><br>
    La MAE montre que le modèle présente une erreur moyenne d’environ 610 €/m² sur l’ensemble des prédictions.
    La RMSE, plus sensible aux écarts importants, atteint 930 €/m², ce qui indique que certaines erreurs ponctuelles sont
    nettement plus élevées que la moyenne.
    </div>
    """, unsafe_allow_html=True)

elif page == "5. Pouvoir prédictif":
    st.title("5. Pouvoir prédictif")
    st.markdown('<p class="section-lead">Contrôler la robustesse du modèle, la structure des erreurs et l’absence de fuite d’information.</p>', unsafe_allow_html=True)

    st.markdown("## 1. Comparaison split temporel / aléatoire")
    show_image_group([
        "08_robustesse.png",
        "08_robustesse.jpg",
        "08_robustesse.jpeg",
    ], width=980)

    st.markdown("## 2. Analyse des résidus")
    show_image_group([
        "10_résidus.png",
        "10_residus.png",
        "10_résidus.jpg",
        "10_residus.jpg",
        "10_résidus.jpeg",
        "10_residus.jpeg",
    ], width=980)

    st.markdown("## 3. Anti-fuite")
    show_image_group([
        "11_anti_fuite.png",
        "11_antifuite.png",
        "11_anti_fuite.jpg",
        "11_antifuite.jpg",
    ], width=780)

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

    st.markdown("""
    <div class="conclusion">
    Le prix raconte une histoire. Le volume de transactions en révèle la fiabilité. La data science relie les deux.
    </div>
    """, unsafe_allow_html=True)
