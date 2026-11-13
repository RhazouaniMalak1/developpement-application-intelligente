# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G1 · **Membres :** Hiba Hamdaoui · **Date :** 11/11/2026

> Les informations de groupe et celles propres à la pull request sont à compléter avant le rendu.

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` lors de la validation finale :

```
23 passed, 2 warnings in 27.12s
```

Cette exécution finale ne comporte aucun test en échec. La sortie du tout premier lancement, avant l'implémentation des sprints, n'a pas été conservée : il n'est donc pas possible d'indiquer précisément quels tests échouaient alors ni leurs messages.

## 2. Lancer Streamlit

Avec `streamlit run ui/app.py`, le navigateur affiche une erreur d'import :

```
ModuleNotFoundError: No module named 'maintai'
```

Depuis la racine du projet, `python -m streamlit run ui/app.py` lance Streamlit avec l'interpréteur Python courant et le répertoire du projet dans le chemin de recherche des modules. Le package `maintai` peut alors être importé. Cette forme évite aussi de lancer par erreur la commande `streamlit` provenant d'un autre environnement Python.

## 3. Sprint 1 : l'onglet « Données »

Code de l'onglet « Données » :

```python
with onglet_donnees:
    df = charger(get_settings().data_path)

    colonnes = st.columns(3)
    colonnes[0].metric("Nombre de relevés", len(df))
    colonnes[1].metric("Taux de panne", f"{df['failure'].mean() * 100:.1f} %")
    colonnes[2].metric("Température moyenne", f"{df['temperature_c'].mean():.1f} °C")

    variable = st.selectbox("Variable à analyser", FEATURES)
    tranches = pd.cut(df[variable], bins=10)
    stats_par_tranche = (
        df.assign(tranche=tranches)
        .groupby("tranche", observed=False)
        .agg(
            moyenne_variable=(variable, "mean"),
            taux_panne=("failure", "mean"),
        )
    )
    chart = stats_par_tranche["taux_panne"].mul(100)
    chart.index = stats_par_tranche["moyenne_variable"].round(1)
    st.bar_chart(chart.rename("taux de panne (%)"))

    st.scatter_chart(df, x="temperature_c", y="vibration_mm_s", color="failure")
```

Valeurs calculées à partir de `data/sensors.csv` :

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5000 |
| Taux de panne | 13.6 % |
| Température moyenne | 59.8 °C |

Avec `vibration_mm_s`, le taux de panne augmente nettement dans les tranches de vibration plus élevées. Le graphique utilise 10 tranches et affiche leur valeur moyenne sur l'axe horizontal plutôt que leurs bornes d'intervalle.

Streamlit relance le script lorsqu'une interaction valide est soumise. Les curseurs de prédiction étant dans un formulaire, les déplacer seuls ne relance pas le script : il faut soumettre le formulaire. Le `print("relance")` apparaîtrait dans le terminal lors de chaque relance.

`@st.cache_data` met en cache le résultat de `charger` pour éviter de relire et retraiter le CSV à chaque relance tant que les arguments de la fonction et les données mises en cache restent valides.

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` de `maintai/client.py` :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse,
    httpx.HTTPError si elle est injoignable."""
    headers = {}
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    if r.status_code != 200:
        raise APIError(
            r.status_code,
            r.json().get("detail")
        )

    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
23 passed, 2 warnings in 27.12s
```

Comportement attendu avec l'API :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| Valeurs par défaut, bonne clé | La probabilité calculée par le modèle, arrondie en pourcentage, puis une alerte si elle atteint le seuil configuré, sinon un message indiquant que le système semble stable. |
| Valeurs par défaut, fausse clé | Un avertissement indiquant l'erreur API 401 et le détail « Clé API absente ou invalide ». |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Une erreur indiquant que l'API est injoignable. |

Le navigateur ne contacte pas directement l'API pour la prédiction : le code Python exécuté par Streamlit envoie la requête HTTP avec `httpx`. CORS est une restriction appliquée par les navigateurs aux requêtes inter-origines ; elle ne bloque pas cet appel serveur-à-serveur.

## 5. Questions de compréhension

1. **Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**  
   Dans le TP2, le JavaScript exécuté dans le navigateur envoie la requête avec `fetch`. Dans Streamlit, le code Python côté serveur l'envoie avec `MaintaiClient` et `httpx`.

2. **Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?**  
   Ils utilisent le `TestClient` de FastAPI, injecté dans `MaintaiClient`. Les requêtes sont traitées directement en mémoire par l'application ASGI, sans démarrer un serveur réseau avec uvicorn.

3. **Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?**  
   Pour une démonstration rapide, je choisirais Streamlit : l'interface et les graphiques peuvent être réalisés directement en Python. Pour une application quotidienne destinée aux techniciens, je choisirais plutôt une interface web dédiée, conçue pour leurs tâches et utilisable sur leurs appareils ; elle permet un contrôle plus précis de l'expérience et de l'intégration au système existant.

## 6. Le rendu Git

- **Lien de la pull request :
- **Le tag `tp3` existe sur GitHub :** oui.
- **`git status` avant le commit : 

