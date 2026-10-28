# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G1 · **Membres :** Najim Aya · **Date :** 28/10/2026

> Chaque section est à compléter dans ce document, qui sera joint à la pull request du TP1.  
> Les résultats du terminal doivent être copiés entre deux lignes de trois accents graves.

---

## 1. Mise en place

Voici la dernière ligne affichée par `python -m pytest` juste après l'installation :

```text
======================================== 3 failed, 10 passed, 1 warning in 7.35s ========================================
```

Sur les 13 tests de `tests/test_api.py`, 10 sont déjà verts alors qu'aucune ligne de code n'a encore été écrite. Pour connaître leurs noms exacts, il suffit d'ouvrir le fichier `tests/test_api.py`.

Il est possible que les deux tests attendant une réponse `422` réussissent sans que ce soit mérité : avec `extra="forbid"`, Pydantic rejette tout champ absent du schéma, mais cette option ne contrôle pas les limites physiques des mesures. Tant que les contraintes `ge` et `le` n'existent pas, une valeur aberrante passe sans problème dès lors que son type est correct.

Quant au troisième test qui échoue, on l'identifie en lisant le détail de la sortie de `pytest`.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min/max des données) |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | Fourchette de températures vraisemblable pour un équipement industriel. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vibration ne peut pas être négative ; 100 mm/s est un plafond choisi pour la validation. |
| `load_pct` | `float` | 0 | 100 | Une charge exprimée en pourcentage reste comprise entre 0 % et 100 %. |
| `runtime_hours` | `float` | 0 | 100000 | Une durée de fonctionnement cumulée est forcément positive ; le plafond de 100 000 heures a été fixé pour ce TP. |

Ces valeurs limites n'ont d'autre rôle que de filtrer les entrées de l'API : elles ne constituent pas des seuils de sécurité applicables à toutes les machines industrielles.

Après l'écriture du seul fichier `schemas.py`, l'exécution de `python -m pytest` a produit le résultat suivant :

```text
============================================= 13 passed, 1 warning in 5.78s ============================================
```

Quand des tests échouent, ils révèlent ce qu'il reste à implémenter, comme la fonction `predict()`. Qu'ils désignent avec précision les éléments manquants est plutôt rassurant : cela démontre qu'ils vérifient réellement le comportement attendu de l'API.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Voici le code de la fonction `predict()` :

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

   predictor = state.get("predictor")
    if not predictor:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return predictor.predict(reading.model_dump())
```

**Quand le modèle est absent, pourquoi répondre 503 et non 500 ?**

Le code `503 Service Unavailable` indique une indisponibilité passagère du service, ici due à l'absence du modèle en mémoire. Le code `500 Internal Server Error`, lui, renvoie à un dysfonctionnement inattendu du côté du serveur.

**Pourquoi le modèle est-il chargé une unique fois au lancement plutôt qu'à chaque requête ?**

Un modèle peut mettre du temps à se charger et occuper beaucoup de mémoire. Le charger une seule fois au démarrage permet de le partager entre toutes les requêtes : les réponses sont plus rapides et on évite de répéter une opération coûteuse.

## 4. Les tests

Voici la dernière ligne de `python -m pytest` à l'issue du TP :

```text
============================================= 13 passed, 1 warning in 5.78s ============================================
```

## 5. L'API en marche

Une fois les commandes suivantes lancées :

```powershell
python -m maintai.dataset
python -m maintai.train
uvicorn maintai.api.main:app --reload
```

on ouvre `http://localhost:8000/docs` pour essayer les requêtes du tableau ci-dessous.

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---|---|
| `GET /health` | `200` quand l'API tourne | `{"status":"ok","model_loaded":true}` lorsque le modèle est bien chargé. |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | `200` quand la prédiction réussit | Un JSON avec `failure_probability`, `alert`, `threshold` et `model_version`, dont les valeurs changent selon le modèle entraîné. |
| `POST /v1/predict` avec une température de `500` | `422` attendu | Un JSON d'erreur de validation signalant que la température dépasse le maximum autorisé de 150 °C. |
| `POST /v1/predicte` (adresse mal orthographiée) | `404` attendu | `{"detail":"Not Found"}` |

Ces codes et ces réponses doivent encore être comparés à ce que renvoie réellement l'API.

**Où les bornes retenues apparaissent-elles dans `/docs` ?**

On les trouve dans le schéma de la requête `POST /v1/predict`, plus précisément dans le modèle `SensorReading`. La documentation OpenAPI, générée automatiquement, les affiche grâce aux contraintes `ge` et `le` placées sur les champs Pydantic.

## 6. Questions de compréhension

### 1. REST et FastAPI : quelle est la différence ?

REST désigne un style d'architecture, c'est-à-dire un ensemble de principes pour concevoir des API web. FastAPI, de son côté, est un framework Python qui permet de construire ces API, notamment des API conformes à REST.

### 2. Le schéma Pydantic sert à trois choses. Lesquelles ?

- Vérifier le type des données entrantes et le respect des bornes fixées.
- Écarter les données incorrectes, y compris les champs en trop interdits par `extra="forbid"`.
- Alimenter la documentation du schéma que reprennent OpenAPI et Swagger UI.

### 3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?

- `localhost` représente l'ordinateur local, celui où l'API s'exécute.
- `8000` est le numéro de port qu'Uvicorn emploie par défaut avec notre commande.
- `/v1/predict` est le chemin menant au point d'entrée de prédiction de la première version de l'API.

### 4. Pourquoi `/v1` dans l'adresse ?

`/v1` indique la version de l'API. Grâce à lui, on peut publier des évolutions futures sans forcément perturber les clients qui utilisent encore l'ancienne version.

### 5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?

- `maintai.api.main` est le module Python dans lequel se trouve le code de l'API.
- `app` est l'objet `FastAPI` créé dans ce module, que démarre Uvicorn.

## 7. Le rendu Git

- **Lien de la pull request :** https://github.com/RhazouaniMalak1/developpement-application-intelligente
- **Présence du tag `tp1` sur GitHub :** oui  
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?** 

## 8. Ce qui reste flou

Certains points restent à approfondir : la manière dont le modèle est chargé au lancement de l'API, le chemin que suivent les données validées jusqu'au prédicteur, et la façon dont le résultat est converti en réponse JSON. Je voudrais aussi mieux comprendre comment les tests automatisés vérifient les différents codes HTTP ainsi que les cas d'erreur.