"""
Script de collecte des données météorologiques historiques pour Libreville, Gabon
Source : API Open-Meteo (gratuite, sans clé API requise)
Usage : python collecte_donnees_meteo_libreville.py
"""

import requests
import pandas as pd
from datetime import date

# ----------------------------------------------------------------------
# 1. PARAMÈTRES
# ----------------------------------------------------------------------

# Coordonnées de Libreville, Gabon
LATITUDE = 0.4162
LONGITUDE = 9.4673

# Période de collecte (à ajuster selon les besoins du projet)
DATE_DEBUT = "2015-01-01"
DATE_FIN = date.today().isoformat()  # aujourd'hui

# Variables météo à récupérer (voir doc Open-Meteo pour la liste complète)
VARIABLES = [
    "precipitation_sum",        # cumul de pluie journalier (mm)
    "temperature_2m_max",       # température max (°C)
    "temperature_2m_min",       # température min (°C)
    "temperature_2m_mean",      # température moyenne (°C)
    "relative_humidity_2m_mean",# humidité relative moyenne (%)
    "wind_speed_10m_max",       # vitesse du vent max (km/h)
    "surface_pressure_mean",    # pression atmosphérique moyenne (hPa)
]

URL = "https://archive-api.open-meteo.com/v1/archive"

# ----------------------------------------------------------------------
# 2. DATES RÉELLES D'INONDATIONS CONFIRMÉES À LIBREVILLE (vérité terrain)
# ----------------------------------------------------------------------
# Sources : ReliefWeb, FloodList, Gabonreview, Cahiers Nantais (Menié Ovono & Pottier, 2019),
# Wikipédia "Inondations au Gabon". Liste non exhaustive : à compléter si possible avec
# les archives de L'Union, la Croix-Rouge gabonaise, ou la Direction Générale de la Météorologie.
#
# NB : certains événements sont connus seulement par mois (pas de jour précis) ;
# dans ce cas on couvre toute la période concernée par prudence.
DATES_INONDATIONS_CONNUES = [
    # (date_debut, date_fin, description)
    ("2015-11-12", "2015-11-12", "Inondation quartier Belle-Peinture"),
    ("2015-12-29", "2015-12-29", "Débordement des collecteurs, quartier Présidence"),
    ("2019-10-01", "2019-10-31", "Inondations saison des pluies (mois complet, date précise inconnue)"),
    ("2020-03-07", "2020-03-07", "Pluies diluviennes, Mont-Bouët/Marché central/Oloumi (marée haute renforçant l'inondation)"),
    ("2022-10-20", "2022-10-21", "Fortes pluies, glissement de terrain PK8 (7 morts)"),
    ("2022-10-26", "2022-10-27", "Débordement du canal de Nzeng-Ayong"),
    ("2023-11-01", "2023-11-30", "Inondations dans plusieurs quartiers (mois complet, date précise inconnue)"),
    ("2024-11-25", "2024-11-25", "Pluies torrentielles, ~1000 foyers touchés à Grand Libreville"),
    ("2025-01-19", "2025-01-19", "Inondations majeures, cité Mebiame"),
    ("2025-03-30", "2025-03-31", "Pluies meurtrières, glissements de terrain, Pk6/Alekery (2 morts)"),
    ("2025-11-04", "2025-11-04", "Inondations au marché de Mont-Bouët"),
    ("2026-01-26", "2026-01-28", "Pluies violentes, réunion interministérielle de crise (Nzeng-Ayong, PK8, Belle-Vue 2...)"),
]


def recuperer_donnees_meteo():
    """Interroge l'API Open-Meteo et retourne un DataFrame pandas."""

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": DATE_DEBUT,
        "end_date": DATE_FIN,
        "daily": ",".join(VARIABLES),
        "timezone": "Africa/Libreville",
    }

    print(f"Requête vers Open-Meteo pour Libreville ({DATE_DEBUT} -> {DATE_FIN})...")
    reponse = requests.get(URL, params=params, timeout=60)
    reponse.raise_for_status()  # lève une erreur si la requête échoue

    donnees = reponse.json()

    if "daily" not in donnees:
        raise ValueError("Réponse inattendue de l'API : pas de données 'daily'.")

    df = pd.DataFrame(donnees["daily"])
    df.rename(columns={"time": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])

    return df


def ajouter_variables_derivees(df):
    """Crée des variables utiles pour la prédiction du risque d'inondation."""

    df = df.sort_values("date").reset_index(drop=True)

    # Cumul de pluie sur plusieurs fenêtres temporelles (indices d'humidité du sol)
    df["pluie_cumul_3j"] = df["precipitation_sum"].rolling(window=3, min_periods=1).sum()
    df["pluie_cumul_7j"] = df["precipitation_sum"].rolling(window=7, min_periods=1).sum()
    df["pluie_cumul_15j"] = df["precipitation_sum"].rolling(window=15, min_periods=1).sum()

    # Moyenne mobile de l'humidité (indicateur de saturation des sols)
    df["humidite_moyenne_7j"] = df["relative_humidity_2m_mean"].rolling(window=7, min_periods=1).mean()

    # Amplitude thermique journalière
    df["amplitude_thermique"] = df["temperature_2m_max"] - df["temperature_2m_min"]

    # Variable PROXY (heuristique) : à n'utiliser qu'en complément, jamais seule.
    # Règle de départ : risque si cumul 3j > 50mm (seuil arbitraire, à calibrer/justifier
    # dans le rapport à partir de la littérature scientifique locale si possible).
    df["risque_proxy_pluviometrique"] = (df["pluie_cumul_3j"] > 50).astype(int)

    return df


def marquer_inondations_reelles(df):
    """Ajoute la vraie variable cible à partir des dates d'inondations historiquement confirmées."""

    df["inondation_reelle"] = 0

    for date_debut, date_fin, description in DATES_INONDATIONS_CONNUES:
        masque = (df["date"] >= date_debut) & (df["date"] <= date_fin)
        df.loc[masque, "inondation_reelle"] = 1
        nb_jours = masque.sum()
        print(f"  - {description} ({date_debut} -> {date_fin}) : {nb_jours} jour(s) marqué(s)")

    total = df["inondation_reelle"].sum()
    print(f"\nTotal de jours marqués comme 'inondation réelle' : {total} sur {len(df)} jours")
    print("⚠️  Ce nombre est volontairement faible : les inondations majeures sont des événements")
    print("    rares. C'est un vrai défi de modélisation (déséquilibre des classes), à traiter avec")
    print("    des techniques comme SMOTE ou en pondérant les classes dans le modèle.")

    return df


def main():
    df = recuperer_donnees_meteo()
    df = ajouter_variables_derivees(df)

    print("\nMarquage des dates d'inondations réelles connues :")
    df = marquer_inondations_reelles(df)

    chemin_sortie = "donnees_meteo_libreville.csv"
    df.to_csv(chemin_sortie, index=False, encoding="utf-8")

    print(f"\n✅ {len(df)} lignes récupérées.")
    print(f"✅ Fichier sauvegardé : {chemin_sortie}")
    print("\nAperçu des données :")
    print(df.head())
    print("\nColonnes disponibles :")
    print(list(df.columns))
    print("\nIMPORTANT pour ton rapport (chapitre 'Limites') :")
    print(" - 'inondation_reelle' = vérité terrain, basée sur des événements confirmés (rare).")
    print(" - 'risque_proxy_pluviometrique' = indicateur basé sur un seuil de pluie (à utiliser")
    print("   uniquement comme variable explicative ou complément, jamais comme vérité absolue).")


if __name__ == "__main__":
    main()
