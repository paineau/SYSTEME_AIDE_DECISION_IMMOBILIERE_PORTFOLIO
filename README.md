````markdown
# SYSTÈME D’AIDE À LA DÉCISION IMMOBILIÈRE

Projet de modélisation et d’analyse du marché immobilier résidentiel français à partir des données DVF enrichies par des données territoriales, socio-économiques et transactionnelles.

---

## PRÉSENTATION GÉNÉRALE

Le marché immobilier constitue un système complexe influencé simultanément par :

- les caractéristiques intrinsèques des biens ;
- la structure territoriale ;
- les dynamiques locales de marché ;
- le contexte socio-économique ;
- les cycles temporels et macro-financiers.

Ce projet vise à construire un système d’aide à la décision immobilière capable d’explorer et de modéliser ces mécanismes à partir des données DVF enrichies.

L’objectif n’est pas de produire une “valeur d’expertise” automatique, mais de développer un démonstrateur analytique structuré permettant :

- d’analyser les déterminants de la valeur immobilière ;
- de mesurer l’apport incrémental des enrichissements territoriaux ;
- de construire des comparables immobiliers robustes ;
- de comparer différents scénarios de modélisation ;
- de proposer une approche explicable et gouvernée de la valorisation immobilière.

---

## POSITIONNEMENT MÉTHODOLOGIQUE

Le projet suit une logique incrémentale et gouvernée.

L’hypothèse directrice est volontairement simple :

> Le prix immobilier dépend des caractéristiques du bien, mais également du territoire, du temps, du contexte socio-économique et de la structure locale du marché.

L’ensemble du pipeline vise à mesurer quantitativement cette hypothèse.

La démarche repose notamment sur :

- une séparation temporelle train/test ;
- un contrôle des fuites de données ;
- une gouvernance centralisée des features ;
- des scénarios incrémentaux par familles de variables ;
- une analyse comparative des modèles ;
- une lecture métier des résidus et des erreurs.

---

## POSITIONNEMENT MÉTIER

Le projet s’inscrit dans une logique de rapprochement entre expertise immobilière et data science appliquée.

Il mobilise une expérience métier couvrant notamment :

- le financement immobilier ;
- l’analyse d’opérations immobilières ;
- la gestion d’immeubles ;
- les problématiques de pathologie du bâtiment ;
- l’assurance construction ;
- les garanties financières d’achèvement ;
- les marchés immobiliers professionnels et résidentiels.

La valeur immobilière y est analysée comme le résultat d’interactions complexes entre le bien, son environnement et son marché.

---

## ARCHITECTURE ANALYTIQUE

Le pipeline transforme progressivement les données DVF brutes en un système de modélisation gouverné.

```text
DVF brutes
   ↓
Nettoyage résidentiel
   ↓
Variables intrinsèques du bien (B1)
   ↓
Maillage territorial IRIS
   ↓
Enrichissements territoriaux (B2)
   ↓
Typologies de marchés immobiliers (B3)
   ↓
Variables temporelles et taux (B4 / B6)
   ↓
Construction des comparables immobiliers
   ↓
Features comparables (B5)
   ↓
Sélection des features et scénarios
   ↓
Feature Store gouverné
   ↓
Préprocessing et modélisation
   ↓
Contrôle antifuite et analyse des performances
```

Cette structuration permet :
- d’isoler les différentes familles de variables ;
- de mesurer l’apport incrémental des enrichissements ;
- de limiter les risques de fuite de données ;
- de garantir la reproductibilité du pipeline analytique.

---

## STRUCTURE DU PIPELINE

1. **00_cadrage_projet.ipynb** — cadrage général et problématique ;

2. **01_import_et_exploration_dvf.ipynb** — importation et exploration des données DVF ;

3. **02_nettoyage_et_filtrage_residentiel.ipynb** — nettoyage des transactions et sélection du périmètre résidentiel ;

4. **03_definition_variables_bien_B1.ipynb** — création des variables intrinsèques du bien ;

5. **04_rattachement_maillage_iris.ipynb** — rattachement géographique IRIS ;

6. **05_enrichissement_territorial_B2.ipynb** — enrichissements territoriaux et socio-économiques ;

7. **06_typologies_marche_immobilier_B3.ipynb** — segmentation et typologies de marchés immobiliers ;

8. **07_variables_temporelles_B4_et_taux_B6.ipynb** — intégration des dynamiques temporelles et variables de taux ;

9. **08_00_construction_comparables_base_outil.ipynb** — construction des comparables immobiliers ;

10. **08_01_features_comparables_B5.ipynb** — création des variables issues des comparables ;

11. **09_features_comparables.ipynb** — consolidation des features comparables ;

12. **10_selection_features_et_scenarios.ipynb** — gouvernance des variables et scénarios de modélisation ;

13. **11_definition_feature_store.ipynb** — structuration du feature store final ;

14. **12_preprocessing_modelisation_prix_m2.ipynb** — preprocessing, benchmark, tuning et modélisation ;

15. **13_synthese_resultats_et_controle_antifuite_B5.ipynb** — synthèse finale et contrôle antifuite.

---

## STACK TECHNIQUE

### Data Science & Machine Learning
- Python
- Pandas
- NumPy
- Scikit-learn
- HistGradientBoosting
- RandomForest
- XGBoost / approches boosting

### Analyse territoriale & géospatiale
- GeoPandas
- Shapely
- Données IRIS / INSEE

### Visualisation & reporting
- Matplotlib
- Seaborn
- Jupyter Notebook

### Structuration projet
- Git / GitHub
- Streamlit
- Feature Store
- Pipeline analytique modulaire

---

## RÉSULTATS PRINCIPAUX

Le meilleur scénario (`S_FULL_SELECTED`) atteint environ :

- **R² ≈ 0.757**
- **MAE ≈ 611 €/m²**
- **RMSE ≈ 929 €/m²**
- **Erreur médiane ≈ 17 %**
- plusieurs millions de transactions exploitées.

Les résultats montrent notamment que :

- les comparables immobiliers locaux constituent le principal moteur prédictif ;
- les variables territoriales améliorent significativement la robustesse du modèle ;
- les modèles de boosting dominent largement les approches linéaires ;
- les variables temporelles et de taux jouent principalement un rôle de contexte macro-financier ;
- la structure locale du marché domine la formation des prix immobiliers.

Les analyses de résidus mettent également en évidence :

- une bonne robustesse sur le cœur du marché ;
- une hausse des erreurs sur les biens atypiques ou haut de gamme ;
- un comportement cohérent avec les mécanismes classiques des modèles immobiliers.

---

## GOUVERNANCE ET ROBUSTESSE

Le projet intègre plusieurs mécanismes de contrôle méthodologique :

- séparation temporelle stricte ;
- contrôle des variables interdites ;
- limitation des risques de fuite temporelle ;
- scénarios incrémentaux ;
- benchmark multi-modèles ;
- analyse des résidus ;
- validation de cohérence métier.

L’objectif est de conserver un pipeline :

- reproductible ;
- explicable ;
- industrialisable ;
- cohérent avec les contraintes métier de l’immobilier.

---

## PERSPECTIVES

Les prolongements envisagés incluent notamment :

- amélioration des comparables multi-échelles ;
- enrichissements macro-économiques supplémentaires ;
- expérimentation de modèles spatio-temporels ;
- développement d’une interface Streamlit interactive ;
- amélioration de l’explicabilité des modèles ;
- industrialisation progressive du pipeline ;
- structuration du projet sous forme de portfolio data immobilier.

---

## STRUCTURE DU PROJET

```text
SYSTEME_AIDE_DECISION_IMMOBILIERE/

├── notebooks/
├── data/
│   ├── raw/
│   ├── external/
│   ├── interim/
│   └── processed/
│
├── outputs/
│   ├── tables/
│   ├── figures/
│   ├── maps/
│   └── reports/
│
├── models/
├── config/
├── src/
├── docs/
├── streamlit_app/
└── archive_dev/
```