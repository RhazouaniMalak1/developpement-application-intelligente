# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** ... · **Membre :** RHAZOUANI MALAK · **Date :** 11/11/2026

> Les éléments indiqués « à compléter » doivent être vérifiés avant le
> rendu.

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

``` text
5 failed, 18 passed, 1 warning in 13.05s
```

**Quels fichiers de tests échouent, et quelle erreur donnent-ils ?**

Les tests qui échouent concernent principalement deux parties du projet
:

-   `test_client.py` : les tests de la méthode `predict()` échouent
    parce que cette méthode n'était pas encore implémentée. Elle
    retournait une erreur `NotImplementedError`.
-   Les tests de l'interface Streamlit : certains tests échouent à cause
    de l'affichage du graphique et parce que la partie prédiction
    n'était pas encore complètement développée.

Les autres tests passent correctement. Cela montre que certaines
fonctionnalités étaient déjà opérationnelles, mais qu'il restait des
éléments à compléter.

## 2. Lancer Streamlit

**Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le
navigateur ?**

La commande provoque une erreur :

``` text
ModuleNotFoundError: No module named 'maintai'
```

**Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette
commande fonctionne-t-elle et pas la première ?**

La première commande utilise directement la commande Streamlit
disponible dans le système. Elle peut donc utiliser un environnement
Python différent de celui de notre projet.

Avec `python -m streamlit run ui/app.py`, on demande à Python d'exécuter
Streamlit avec l'interpréteur actuellement activé, c'est-à-dire celui de
notre environnement virtuel `.venv`.

Cela permet d'utiliser les bonnes dépendances et de retrouver le package
`maintai`, à condition de lancer la commande depuis le dossier du
projet.

## 3. Sprint 1 : l'onglet « Données »

**Code de l'onglet « Données » :**

``` python
with onglet_donnees:
    df = charger(get_settings().data_path)

    # 1. Affichage des trois indicateurs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Nombre de relevés", len(df))

    with col2:
        st.metric("Taux de panne", f"{df.failure.mean() * 100:.1f} %")

    with col3:
        st.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

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

    st.bar_chart(taux_panne)

    st.divider()

    # 4. Nuage de points température / vibration
    st.subheader("Relation entre température et vibration")

    st.scatter_chart(
        df,
        x="temperature_c",
        y="vibration_mms",
        color="failure"
    )
```

**Résultats affichés :**

  Indicateur              Valeur affichée
  --------------------- -----------------
  Nombre de relevés                 5 000
  Taux de panne                    13,6 %
  Température moyenne             59,8 °C

**Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de
panne quand la vibration augmente ?**

On remarque que le taux de panne augmente globalement avec
l'augmentation du niveau de vibration. Pour les faibles vibrations, le
taux de panne est très faible, tandis que pour les vibrations plus
importantes, il devient beaucoup plus élevé.

Cela montre que les vibrations peuvent être un indicateur important pour
détecter les risques de panne des équipements. Cependant, cette
évolution n'est pas parfaitement régulière dans toutes les tranches.

**Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un
curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre
sur le fonctionnement de Streamlit ?**

Après avoir ajouté `print("relance")`, j'ai remarqué que Streamlit
réexécute le script lorsqu'une interaction provoque une relance.

Dans mon cas, les curseurs sont placés dans un formulaire (`st.form`).
Le script ne se relance donc pas immédiatement lorsque je déplace un
curseur. Il se relance lorsque je clique sur le bouton « Prédire ».

Cela montre que Streamlit fonctionne avec un système de réexécution du
script après certaines interactions de l'utilisateur.

**À quoi sert `@st.cache_data` sur la fonction `charger` ?**

`@st.cache_data` permet de conserver temporairement les données déjà
chargées. Ainsi, Streamlit n'a pas besoin de lire le fichier CSV à
chaque réexécution du script.

Cela permet de gagner du temps et d'améliorer les performances de
l'application.

## 4. Sprint 2 : l'onglet « Prédiction »

**Méthode `predict` (`maintai/client.py`) :**

``` python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé à l'API et retourne la prédiction."""

    # 1. Préparer les en-têtes
    headers = {}

    if self.api_key:
        headers["X-API-Key"] = self.api_key

    # 2. Envoyer la requête POST à l'API
    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    # 3. Vérifier le code de réponse
    if r.status_code != 200:
        detail = r.json().get("detail")
        raise APIError(r.status_code, detail)

    # 4. Retourner le résultat
    return r.json()
```

**Dernière ligne de `python -m pytest` à la fin du sprint 2 :**

``` text
23 passed, 1 warning in 4.89s
```

Tous les tests passent. Il reste seulement un avertissement qui ne
bloque pas l'exécution des tests.

**Essais réalisés avec l'API lancée :**

 
  Essai                               Ce qu'affiche Streamlit
  
  Valeurs par défaut, bonne clé       La prédiction fonctionne. La
                                      probabilité de panne affichée est
                                      de 98,65 %. Une alerte est
                                      déclenchée car `alert` vaut `true`.

  Valeurs par défaut, fausse clé      Erreur API : Erreur 401 : Clé API
                                      absente ou invalide.

  API arrêtée (Ctrl+C dans le         À compléter après l'essai :
  terminal d'Uvicorn)                 normalement, Streamlit affiche une
                                      erreur de connexion car l'API n'est
                                      plus disponible.
  -----------------------------------------------------------------------

**Résultat JSON obtenu avec la bonne clé :**

``` json
{
    "failure_probability": 0.9865,
    "alert": true,
    "threshold": 0.3,
    "model_version": "2026-11-11T16:42:39Z"
}
```

**Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la
prédiction fonctionne. Pourquoi ?**

La prédiction fonctionne parce que Streamlit communique avec l'API
FastAPI depuis le code Python, en utilisant la bibliothèque HTTPX.

La politique CORS concerne principalement les requêtes envoyées
directement par le navigateur. Dans notre cas, c'est le serveur Python
de Streamlit qui envoie la requête à FastAPI. C'est pour cette raison
que le port 8501 n'a pas besoin d'être ajouté dans la configuration CORS
pour cette communication.

## 5. Questions de compréhension

**1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans
Streamlit ?**

Dans le TP2, c'est le navigateur qui envoie la requête à l'API à l'aide
de JavaScript.

Dans le TP3, c'est le code Python de Streamlit qui envoie directement la
requête à FastAPI avec HTTPX.

La différence est donc que dans le TP2, la communication est faite
depuis le navigateur, alors que dans le TP3, elle est faite depuis le
serveur Python.

**2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin
d'Uvicorn ?**

Les tests de `test_client.py` peuvent utiliser un client HTTP simulé
pour tester les réponses de l'API.

Cela permet de vérifier le fonctionnement de la méthode `predict()`, les
données envoyées et la gestion des erreurs sans démarrer un vrai
serveur. Cette réponse est à confirmer avec le contenu de vos tests.

**3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle
choisiriez-vous pour une démonstration à un client ? Et pour
l'application d'un technicien de maintenance ? Pourquoi ?**

Pour une démonstration à un client, je choisirais Streamlit parce qu'il
permet de présenter rapidement les données, les graphiques et les
résultats des prédictions dans une interface simple et claire.

Pour une application utilisée quotidiennement par un technicien de
maintenance, je choisirais plutôt une interface HTML + JavaScript. Elle
permet de personnaliser davantage l'interface et de mieux l'adapter aux
besoins des utilisateurs.

Cependant, Streamlit reste une bonne solution pour créer rapidement un
prototype et tester les fonctionnalités du projet.

## 6. Le rendu Git

-   **Lien de la pull request :** à compléter avec le lien de votre pull
    request GitHub.
-   **Le tag `tp3` existe sur GitHub :** à vérifier (oui / non).
-   **`git status` avant le commit :** à vérifier. Les fichiers `.env`,
    `data/` ou `models/` ne doivent normalement pas être ajoutés au
    dépôt s'ils contiennent des informations de configuration, des
    données locales ou des modèles générés.

## 7. Ce qui reste flou

J'ai encore quelques points à mieux comprendre :

-   La différence entre les requêtes envoyées depuis le navigateur et
    celles envoyées depuis le serveur Python.
-   Le fonctionnement du chargement du modèle de Machine Learning dans
    l'API.
-   La gestion des erreurs lorsque l'API est arrêtée ou lorsque le
    modèle n'est pas disponible.
-   Le fonctionnement du cache Streamlit et les situations dans
    lesquelles les données sont rechargées.

Ce TP m'a permis de mieux comprendre comment relier une interface
Streamlit à une API FastAPI, afficher des données et utiliser un modèle
de Machine Learning pour réaliser une prédiction.
