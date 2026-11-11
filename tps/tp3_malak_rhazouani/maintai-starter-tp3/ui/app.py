
import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings


# --------------------------------------------------
# Configuration de la page
# --------------------------------------------------

print("relance")

st.set_page_config(
    page_title="MaintAI - Prédiction de panne",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ MaintAI · prédiction de panne")


# --------------------------------------------------
# Chargement des données
# --------------------------------------------------

@st.cache_data
def charger(chemin):
    """Charge le fichier CSV contenant les relevés des capteurs."""
    return pd.read_csv(chemin)


# --------------------------------------------------
# Paramètres de connexion à l'API
# --------------------------------------------------

with st.sidebar:
    st.header("⚙️ Configuration")

    url = st.text_input(
        "URL de l'API",
        value="http://127.0.0.1:8000"
    )

    cle = st.text_input(
        "Clé API",
        type="password"
    )


# --------------------------------------------------
# Création des deux onglets
# --------------------------------------------------

onglet_donnees, onglet_prediction = st.tabs(
    ["Données", "Prédiction"]
)


# ==================================================
# SPRINT 1 : ONGLET DONNÉES
# ==================================================

with onglet_donnees:

    df = charger(get_settings().data_path)

    # 1. Affichage des trois indicateurs

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Nombre de relevés",
            len(df)
        )

    with col2:
        st.metric(
            "Taux de panne",
            f"{df['failure'].mean() * 100:.1f} %"
        )

    with col3:
        st.metric(
            "Température moyenne",
            f"{df['temperature_c'].mean():.1f} °C"
        )

    st.divider()

    # 2. Choix de la variable à analyser

    st.subheader("Analyse du taux de panne")

    variable = st.selectbox(
        "Choisir une variable :",
        FEATURES
    )

    # 3. Calcul du taux de panne par tranche

    df_analyse = df.copy()

    df_analyse["tranche"] = pd.cut(
        df_analyse[variable],
        bins=5
    )

    taux_panne = (
        df_analyse.groupby("tranche", observed=False)["failure"]
        .mean() * 100
    )

    # Conversion des intervalles en texte
    # pour éviter les erreurs d'affichage Streamlit

    taux_panne.index = taux_panne.index.astype(str)

    st.bar_chart(taux_panne)

    st.divider()

    # 4. Nuage de points température / vibration

    st.subheader("Relation entre température et vibration")

    colonne_vibration = (
        "vibration_mm_s"
        if "vibration_mm_s" in df.columns
        else "vibration_mms"
    )

    st.scatter_chart(
        df,
        x="temperature_c",
        y=colonne_vibration,
        color="failure"
    )


# ==================================================
# SPRINT 2 : ONGLET PRÉDICTION
# ==================================================

with onglet_prediction:

    st.subheader("Prédire une panne")

    st.write(
        "Saisissez les valeurs des capteurs "
        "pour estimer le risque de panne."
    )

    with st.form("releve"):

        col1, col2 = st.columns(2)

        with col1:
            temperature = st.slider(
                "Température (°C)",
                min_value=0.0,
                max_value=150.0,
                value=72.0
            )

            vibration = st.slider(
                "Vibration (mm/s)",
                min_value=0.0,
                max_value=30.0,
                value=6.0
            )

        with col2:
            charge = st.slider(
                "Charge (%)",
                min_value=0.0,
                max_value=100.0,
                value=85.0
            )

            heures = st.number_input(
                "Heures de fonctionnement",
                min_value=0,
                value=15000
            )

        envoyer = st.form_submit_button(
            "🔍 Prédire",
            use_container_width=True
        )

    # Envoi de la demande à l'API

    if envoyer:

        releve = {
            "temperature_c": temperature,
            "vibration_mm_s": vibration,
            "load_pct": charge,
            "runtime_hours": heures
        }

        try:
            client = MaintaiClient(
                url,
                api_key=cle
            )

            resultat = client.predict(releve)

            st.success("Prédiction réalisée avec succès !")

            st.subheader("Résultat de la prédiction")

            if isinstance(resultat, dict):

                st.json(resultat)

                probabilite = resultat.get(
                    "failure_probability"
                )

                if probabilite is not None:
                    st.metric(
                        "Probabilité de panne",
                        f"{float(probabilite) * 100:.0f} %"
                    )

                prediction = resultat.get("prediction")

                if prediction is not None:
                    if prediction:
                        st.error("Risque de panne détecté.")
                    else:
                        st.success("Aucune panne détectée.")

        except APIError as erreur:
            st.error(f"Erreur API : {erreur}")

        except httpx.HTTPError as erreur:
            st.error(
                f"Impossible de contacter l'API : {erreur}"
            )

        except Exception as erreur:
            st.error(f"Erreur : {erreur}")
