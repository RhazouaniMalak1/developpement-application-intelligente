
"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.

Lancement (depuis la racine du projet) : python -m streamlit run ui/app.py
"""

import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings


st.set_page_config(
    page_title="MaintAI",
    page_icon="🔧"
)

st.title("MaintAI · prédiction de panne")


@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lu une seule fois : Streamlit relance tout le script à chaque clic
    return pd.read_csv(path)


with st.sidebar:
    url = st.text_input(
        "URL de l'API",
        "http://localhost:8000"
    )

    cle = st.text_input(
        "Clé API",
        type="password"
    )


onglet_donnees, onglet_prediction = st.tabs(
    ["Données", "Prédiction"]
)


# =========================================================
# Sprint 1 : explorer les données
# =========================================================

with onglet_donnees:

    df = charger(get_settings().data_path)

    # TODO TP3 sprint 1 :
    #   1. trois indicateurs côte à côte (st.columns, puis .metric) :
    #      le nombre de relevés, le taux de panne (df.failure.mean()), la température moyenne

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Nombre de relevés",
            len(df)
        )

    with col2:
        st.metric(
            "Taux de panne",
            f"{df.failure.mean() * 100:.2f} %"
        )

    with col3:
        st.metric(
            "Température moyenne",
            f"{df.temperature_c.mean():.2f} °C"
        )

    #   2. une liste déroulante (st.selectbox) pour choisir une variable parmi FEATURES

    variable = st.selectbox(
        "Choisir une variable",
        FEATURES
    )

    #   3. le taux de panne par tranche de cette variable (pd.cut, groupby), en barres (st.bar_chart)

    tranches = pd.cut(
        df[variable],
        bins=10
    )

    taux_panne = (
        df.groupby(tranches, observed=True)
        .agg(
            moyenne=(variable, "mean"),
            taux_panne=("failure", "mean"),
        )
        .reset_index()
    )

    taux_panne["taux_panne"] *= 100
    taux_panne["moyenne"] = taux_panne["moyenne"].round(1)

    etiquettes = taux_panne["moyenne"].map(lambda moyenne: f"{moyenne:g}").tolist()
    etiquettes[0] = ""
    taux_panne.index = etiquettes

    st.subheader(
        f"Taux de panne selon la moyenne de {variable}"
    )

    st.bar_chart(taux_panne, y="taux_panne")

    #   4. un nuage de points température / vibration, coloré par panne (st.scatter_chart)

    st.subheader(
        "Température / Vibration selon la panne"
    )

    scatter_df = df[
        ["temperature_c", "vibration_mm_s", "failure"]
    ].copy()

    scatter_df["failure"] = scatter_df["failure"].map({
        0: "Pas de panne",
        1: "Panne"
    })

    st.scatter_chart(
        scatter_df,
        x="temperature_c",
        y="vibration_mm_s",
        color="failure"
    )


# =========================================================
# Sprint 2 : demander une prédiction à l'API
# =========================================================

with onglet_prediction:

    with st.form("releve"):

        releve = {
            "temperature_c": st.slider(
                "Température (°C)",
                -40.0,
                150.0,
                72.0
            ),

            "vibration_mm_s": st.slider(
                "Vibration (mm/s)",
                0.0,
                50.0,
                6.0
            ),

            "load_pct": st.slider(
                "Charge (%)",
                0.0,
                100.0,
                85.0
            ),

            "runtime_hours": st.number_input(
                "Heures de fonctionnement",
                0,
                100_000,
                15000
            ),
        }

        envoye = st.form_submit_button("Prédire")

    if envoye:

        # TODO TP3 sprint 2 :
        #   1. créer MaintaiClient(url, api_key=cle) et appeler .predict(releve)

        try:

            client = MaintaiClient(
                url,
                api_key=cle
            )

            resultat = client.predict(releve)

            #   2. APIError → st.warning avec le code et le message ;
            #      httpx.HTTPError → st.error("API injoignable ...")

            #   3. sinon : st.metric("Probabilité de panne", f"{pct} %"),
            #      puis st.error (alerte) ou st.success (normal)

            # Récupération de la probabilité de panne
            pct = resultat["failure_probability"] * 100

            # Affichage de la probabilité
            st.metric(
                "Probabilité de panne",
                f"{pct:.0f} %"
            )

            # Affichage du résultat selon l'alerte retournée par l'API
            if resultat.get("alert", False):

                st.error(
                    "ALERTE : Risque de panne detecte."
                )

            else:

                st.success(
                    "Fonctionnement normal."
                )

        except APIError as e:

            st.warning(
                f"Erreur API ({e.status_code}) : {e.detail}"
            )

        # httpx.HTTPError → st.error("API injoignable ...")

        except httpx.HTTPError as e:

            st.error(
                f"API injoignable : {e}"
            )
