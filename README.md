# 🌊 Prédiction précoce des risques d'inondation à Libreville

Système d'Intelligence Artificielle pour la prédiction des risques d'inondation à Libreville (Gabon), à partir de données météorologiques et géospatiales.

## 📋 Description du projet

Ce projet couvre l'ensemble d'une chaîne de traitement Data Science :

1. **Collecte automatisée** de 10 ans de données météorologiques via l'API [Open-Meteo](https://open-meteo.com)
2. **Construction d'une variable cible réelle** à partir d'une recherche documentaire (12 épisodes d'inondation confirmés entre 2015 et 2026)
3. **Comparaison de cinq algorithmes de Machine Learning**
4. **Construction d'un indice de risque géospatial** par quartier
5. **Développement d'un système d'alerte précoce** différencié par zone

## 🧠 Modèles comparés

| Modèle | Recall (détection) | F1-score |
|---|---|---|
| Régression Logistique | **0.87** | 0.17 |
| Arbre de Décision | 0.67 | 0.19 |
| SVM | 0.53 | 0.16 |
| Random Forest | 0.47 | **0.32** |
| XGBoost | 0.13 | 0.17 |

Le modèle de Régression Logistique a été retenu : dans un système d'alerte, détecter le plus grand nombre d'inondations réelles compte davantage qu'un score global élevé.

## 🔎 Un résultat méthodologique clé

Un test de validation sur une année complètement indépendante (2026, exclue de l'entraînement) a révélé un risque de **fuite d'information** lors d'un découpage aléatoire classique : certains épisodes d'inondation s'étalant sur plusieurs jours consécutifs, un découpage aléatoire peut artificiellement gonfler la performance mesurée. Une évaluation avec tolérance temporelle (±2 jours) a confirmé que le modèle capte néanmoins une tendance réelle.

## 🗺️ Indice de risque géospatial

Un indice de risque a été construit pour 12 quartiers de Libreville, combinant l'historique des inondations et l'altitude (récupérée via l'API Open-Elevation), puis visualisé sur une carte interactive (Folium).

## 🛠️ Technologies utilisées

- **Python** : pandas, scikit-learn, XGBoost, Folium, matplotlib
- **Jupyter Notebook**
- **Sources de données :** API Open-Meteo (météo), API Open-Elevation (altitude), recherche documentaire (presse locale, ReliefWeb, FloodList)

## 📁 Structure du projet

```
├── 01_collecte_donnees.ipynb          # Collecte, nettoyage, modélisation météo
├── 02_donnees_environnementales.ipynb # Indice de risque géospatial par quartier
├── 03_systeme_alerte.ipynb            # Système d'alerte combiné
├── donnees_meteo_libreville.csv       # Données météorologiques (2015-2026)
├── quartiers_risque_libreville.csv    # Indice de risque par quartier
└── carte_risque_inondation_libreville.html  # Carte interactive
```

## 🚀 Utilisation

```bash
pip install pandas requests scikit-learn xgboost folium matplotlib joblib
jupyter notebook
```
Ouvrir et exécuter les notebooks dans l'ordre (01 → 02 → 03).

## ⚠️ Limites assumées

- Seulement 76 jours d'inondation confirmés sur 4206 (déséquilibre des classes important)
- Coordonnées des quartiers approximatives (recherche de lieux généraliste, non cadastrale)
- Données météorologiques issues d'un modèle de réanalyse (ERA5), non de stations physiques locales

## 👤 Auteure

Eyang Ebona Vanessa — Master 1 Informatique, IFIM (Institut Facultaire d'Informatique et de Management)

*Projet tutoré réalisé sous la direction du Dr Djes-Frésy Bilenga Moukodouma.*
