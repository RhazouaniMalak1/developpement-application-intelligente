"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.

Lancement (depuis la racine du projet) : python -m streamlit run ui/app.py
"""
import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings

st.set_page_config(page_title="MaintAI", page_icon="🔧")
st.title("MaintAI · prédiction de panne")


@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lu une seule fois : Streamlit relance tout le script à chaque clic
    return pd.read_csv(path)


with st.sidebar:
    url = st.text_input("URL de l'API", "http://localhost:8000")
    cle = st.text_input("Clé API", type="password")

onglet_donnees, onglet_prediction = st.tabs(["Données", "Prédiction"])

# Sprint 1 : explorer les données
with onglet_donnees:
    df = charger(get_settings().data_path)
    
    # 1. Trois indicateurs côte à côte
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de relevés", len(df))
    col2.metric("Taux de panne", f"{df['failure'].mean() * 100:.2f} %")
    col3.metric("Température moyenne", f"{df['temperature_c'].mean():.1f} °C")

    st.divider()

    # 2. Liste déroulante pour choisir une variable parmi FEATURES
    var_choisie = st.selectbox("Variable à analyser", FEATURES)

    # 3. Taux de panne par tranche de cette variable en barres
    df["tranche"] = pd.cut(df[var_choisie], bins=10)
    par_tranche = df.groupby("tranche", observed=False)
    graphique_tranches = par_tranche.agg(
        moyenne_variable=(var_choisie, "mean"),
        taux_panne=("failure", "mean"),
    ).dropna(subset=["moyenne_variable"])
    etiquette_moyenne = f"Moyenne de {var_choisie}"
    graphique_tranches[etiquette_moyenne] = graphique_tranches["moyenne_variable"].map(
        lambda moyenne: f"{moyenne:.2f}"
    )
    graphique_tranches["Taux de panne (%)"] = graphique_tranches["taux_panne"] * 100
    st.bar_chart(graphique_tranches, x=etiquette_moyenne, y="Taux de panne (%)")

    # 4. Nuage de points température / vibration, coloré par panne
    st.scatter_chart(df, x="temperature_c", y="vibration_mm_s", color="failure")


# Sprint 2 : demander une prédiction à l'API
with onglet_prediction:
    with st.form("releve"):
        releve = {
            "temperature_c": st.slider("Température (°C)", -40.0, 150.0, 72.0),
            "vibration_mm_s": st.slider("Vibration (mm/s)", 0.0, 50.0, 6.0),
            "load_pct": st.slider("Charge (%)", 0.0, 100.0, 85.0),
            "runtime_hours": st.number_input("Heures de fonctionnement", 0, 100_000, 15000),
        }
        envoye = st.form_submit_button("Prédire")

    if envoye:
        try:
            client = MaintaiClient(url, api_key=cle if cle else None)
            res = client.predict(releve)
            
            prob = res.get("probability", res.get("failure_probability", res.get("failure", 0.0)))
            if isinstance(prob, bool):
                pct = 100.0 if prob else 0.0
            else:
                pct = round(float(prob) * 100)

            st.metric("Probabilité de panne", f"{pct} %")
            
            if pct > 50.0:
                st.error("ALERTE : risque de panne élevé !")
            else:
                st.success("Fonctionnement normal.")

        except APIError as e:
            st.warning(f"Erreur {e.code} : {e.detail}")
        except httpx.HTTPError:
            st.error("API injoignable, vérifiez l'URL du serveur.")