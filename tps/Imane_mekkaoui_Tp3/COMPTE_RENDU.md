# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G1  ·  **Membres :**Imane Mekkaoui  ·  **Date :** 2026-2027

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
============================== 23 passed, 1 warning in 12.84s ===============================
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Aucun

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
Traceback:
File "C:\Users\dell\Documents\projet_app_intelligente\TP3\maintai-starter-tp3\ui\app.py", line 11, in <module>
    from maintai.client import APIError, MaintaiClient

```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

python -m streamlit utilise le Streamlit installé avec le Python actif. L’autre commande pouvait utiliser un autre Python, qui ne trouvait pas le module maintai

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Nombre de relevés", len(df))

with col2:
    st.metric("Taux de panne", f"{df.failure.mean() * 100:.2f} %")

with col3:
    st.metric("Température moyenne", f"{df.temperature_c.mean():.2f} °C")

variable = st.selectbox("Choisir une variable", FEATURES)

tranches = pd.cut(df[variable], bins=10)

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

st.subheader(f"Taux de panne selon la moyenne de {variable}")
st.bar_chart(taux_panne, y="taux_panne")

st.subheader("Température / Vibration selon la panne")

scatter_df = df[["temperature_c", "vibration_mm_s", "failure"]].copy()
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
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés |5000|
| Taux de panne |13.56 % |
| Température moyenne |59.80 °C|

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente globalement avec les vibrations : il passe d’environ 2 % pour une moyenne de 1,3 mm/s à 84 % autour de 9,7 mm/s, puis atteint 100 % dans les tranches supérieures. Ces dernières contiennent toutefois très peu de relevés

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Le message `relance` s'affiche dans le terminal. Streamlit réexécute le script quand on interagit avec un widget.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Il met en cache les données lues afin d'éviter de relire le fichier CSV à chaque réexécution.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
    headers = {}
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post("/v1/predict", json=reading, headers=headers)

    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except (ValueError, TypeError):
            detail = r.text
        raise APIError(r.status_code, detail)

    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
23 passed, 1 warning in 5.17s
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne : 95 %, avec une alerte. |
| valeurs par défaut, fausse clé | Erreur API (401) : clé absente ou invalide. |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Message « API injoignable ». |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

La requête est envoyée par le code Python côté serveur, pas directement par le navigateur. CORS ne s'applique pas à cet appel serveur-à-serveur.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   En TP2, c'est le JavaScript du navigateur. Dans Streamlit, c'est le code Python côté serveur.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   Ils utilisent un client de test qui appelle directement l'application FastAPI, sans démarrer de serveur.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   Pour une démonstration rapide, je choisirais Streamlit, car l'interface est simple à créer. Pour une application destinée aux techniciens, je choisirais une page web dédiée, plus facile à adapter à leurs besoins.

## 6. Le rendu Git

- Lien de la pull request : …
- Le tag `tp3` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? oui / non

## 7. Ce qui reste flou

À compléter si des questions restent après le TP.
