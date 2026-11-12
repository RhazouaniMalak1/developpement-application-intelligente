# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** 1  · **Membres :** Najim Aya· **Date :** 11/11/2026

> Les valeurs ci-dessous correspondent aux fichiers et données présents dans le projet au moment du compte rendu.

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` après l'installation et le lancement depuis la racine du projet :

```
23 passed
```

Les dépendances sont installées et les tests s'exécutent correctement depuis la racine du projet.

## 2. Lancer Streamlit

La commande `python -m streamlit run ui/app.py` lance l'application Streamlit depuis la racine du projet. Le tableau de bord MaintAI s'affiche dans le navigateur, sur http://localhost:8501.

## 3. Sprint 1 : l'onglet « Données »

Code de l'onglet « Données » :

```python
with onglet_donnees:
    df = charger(get_settings().data_path)

    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de relevés", len(df))
    col2.metric("Taux de panne", f"{df['failure'].mean() * 100:.2f} %")
    col3.metric("Température moyenne", f"{df['temperature_c'].mean():.1f} °C")

    st.divider()

    var_choisie = st.selectbox("Variable à analyser", FEATURES)

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

    st.scatter_chart(df, x="temperature_c", y="vibration_mm_s", color="failure")
```

Indicateurs calculés sur `data/sensors.csv` :

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.56 % |
| Température moyenne | 59.8 °C |

Quand `vibration_mm_s` augmente, le taux de panne augmente nettement dans les données : il passe d'environ 2 % dans le premier bin à plus de 80 % dans les bins élevés, et atteint 100 % dans plusieurs bins.

Après avoir ajouté `print("relance")` en haut de `ui/app.py`, le texte s'affiche dans le terminal au chargement et à chaque interaction qui provoque une nouvelle exécution. Cela montre que Streamlit relance le script pour mettre l'interface à jour.

`@st.cache_data` met en cache le résultat de `charger` pour le même chemin de données. Le script peut donc être relancé sans relire inutilement le CSV à chaque interaction.

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` de `maintai/client.py` :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
    headers = {}
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post("/v1/predict", json=reading, headers=headers)

    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise APIError(r.status_code, detail)

    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
23 passed
```

Avec l'API lancée et une clé correcte, les valeurs par défaut donnent une probabilité de panne de 94.75 % côté API. Streamlit l'affiche arrondie à `95 %` et affiche une alerte.

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | `Probabilité de panne : 95 %` et `ALERTE : risque de panne élevé !` |
| valeurs par défaut, fausse clé | Avertissement `Erreur 401 : Clé API absente ou invalide` |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | `API injoignable, vérifiez l'URL du serveur.` |

Le port 8501 n'a pas besoin d'être dans `MAINTAI_CORS_ORIGINS`, car l'appel à l'API est effectué par le code Python côté serveur Streamlit, pas directement par le navigateur. CORS concerne les requêtes initiées par le navigateur.

## 5. Questions de compréhension

1. Dans la page web du TP2, c'est le JavaScript exécuté dans le navigateur qui envoie la requête à l'API. Dans Streamlit, c'est le code Python de l'application qui envoie la requête.
2. Les tests de `test_client.py` n'ont pas besoin d'uvicorn : la fixture fournit un `TestClient` FastAPI au `MaintaiClient`. L'API est ainsi appelée directement dans le processus du test.
3. Pour une démonstration rapide à un client, je choisirais Streamlit, car l'interface de visualisation et de prédiction est rapide à construire et à modifier. Pour une application destinée aux techniciens, je choisirais plutôt une page HTML/JavaScript personnalisée si l'ergonomie, l'intégration dans un site existant ou l'accès depuis différents appareils sont prioritaires.

## 6. Le rendu Git

- Lien de la pull request :
- Le tag `tp3` existe sur GitHub : oui
- `git status` avant le commit :

## 7. Ce qui reste flou

Je souhaite savoir encore la gestion du cache quand le fichier csv change.
