# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G1 · **Membres :** Hamdaoui Hiba · **Date :** 28/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.  
> Collez les sorties du terminal entre les lignes de trois accents graves.

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place :

```text
======================================== 3 failed, 10 passed, 1 warning in 7.35s ========================================
```

Dans `tests/test_api.py`, 10 tests sur 13 passent déjà alors que rien n'est écrit. Les noms exacts des tests sont à relever dans le fichier `tests/test_api.py`.

Les deux tests qui attendent un code `422` peuvent passer pour une mauvaise raison : le paramètre `extra="forbid"` de Pydantic refuse les champs supplémentaires qui ne sont pas déclarés dans le schéma. Cependant, il ne vérifie pas à lui seul les limites physiques des valeurs des capteurs. Sans les contraintes `ge` et `le`, une valeur hors limites peut être acceptée si son type est correct.

Le troisième test en échec doit être identifié en consultant le résultat détaillé de `pytest`.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min/max des données) |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | Plage de température plausible pour une machine industrielle. |
| `vibration_mm_s` | `float` | 0 | 100 | La vibration mesurée ne peut pas être négative ; 100 mm/s est une limite supérieure de validation. |
| `load_pct` | `float` | 0 | 100 | Le pourcentage de charge est compris entre 0 % et 100 %. |
| `runtime_hours` | `float` | 0 | 100000 | Le temps de fonctionnement cumulé ne peut pas être négatif ; 100 000 heures est une limite de validation choisie pour le TP. |

Ces bornes sont des limites de validation de l'API et ne constituent pas nécessairement des limites de sécurité universelles pour toutes les machines industrielles.

Après avoir écrit `schemas.py` seul, exécuter `python -m pytest` et relever le résultat réel :

```text
============================================= 13 passed, 1 warning in 5.78s ============================================```

Les tests qui échouent peuvent maintenant signaler les fonctionnalités restantes à implémenter, notamment la fonction `predict()`. C'est un bon signe lorsque les tests détectent précisément les fonctionnalités manquantes, car ils vérifient alors le comportement attendu de l'API.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Corps de la fonction `predict()` :

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

**Pourquoi répondre 503 et pas 500 quand le modèle manque ?**

Le code HTTP `503 Service Unavailable` indique que le service est temporairement indisponible parce que le modèle n'est pas chargé. Le code `500 Internal Server Error` indique plutôt une erreur interne inattendue du serveur.

**Pourquoi le modèle est-il chargé une seule fois au démarrage et pas à chaque requête ?**

Le chargement d'un modèle peut prendre du temps et utiliser beaucoup de mémoire. Le charger une seule fois au démarrage permet de le réutiliser pour toutes les requêtes, de réduire le temps de réponse et d'éviter des chargements inutiles.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```text
============================================= 13 passed, 1 warning in 5.78s ============================================
```

## 5. L'API en marche

Après avoir exécuté les commandes suivantes :

```powershell
python -m maintai.dataset
python -m maintai.train
uvicorn maintai.api.main:app --reload
```

Ouvrir `http://localhost:8000/docs` et tester les requêtes suivantes.

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---|---|
| `GET /health` | `200` si l'API fonctionne | `{"status":"ok","model_loaded":true}` si le modèle est chargé. |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | `200` si la prédiction réussit | JSON contenant `failure_probability`, `alert`, `threshold` et `model_version`. Les valeurs dépendent du modèle entraîné. |
| `POST /v1/predict` avec une température de `500` | `422` attendu | JSON de validation indiquant que la température dépasse la limite maximale de 150 °C. |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | `404` attendu | `{"detail":"Not Found"}` |

Les codes et réponses doivent être confirmés à partir des résultats réels de l'API.

**Dans `/docs`, où voit-on les bornes choisies ?**

Les bornes sont visibles dans le schéma de la requête `POST /v1/predict`, au niveau du modèle `SensorReading`. Elles apparaissent dans la documentation OpenAPI générée grâce aux contraintes `ge` et `le` définies dans les champs Pydantic.

## 6. Questions de compréhension

### 1. REST et FastAPI : quelle est la différence ?

REST est un style architectural qui définit des principes de conception pour les API web. FastAPI est un framework Python permettant de développer des API web, notamment des API respectant les principes REST.

### 2. Le schéma Pydantic sert à trois choses. Lesquelles ?

- Valider les types des données reçues et vérifier leurs bornes.
- Refuser les données invalides et, avec `extra="forbid"`, les champs supplémentaires interdits.
- Générer la documentation du schéma utilisée par OpenAPI et Swagger UI.

### 3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?

- `localhost` désigne la machine locale sur laquelle l'API est exécutée.
- `8000` désigne le port utilisé par défaut par Uvicorn dans notre commande.
- `/v1/predict` désigne le chemin de l'endpoint de prédiction de la version 1 de l'API.

### 4. Pourquoi `/v1` dans l'adresse ?

`/v1` indique la version de l'API. Cela permet de faire évoluer l'API à l'avenir sans nécessairement casser les clients qui utilisent une ancienne version.

### 5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?

- `maintai.api.main` désigne le module Python qui contient le code de l'API.
- `app` désigne l'objet `FastAPI` créé dans ce module et lancé par Uvicorn.

## 7. Le rendu Git

- **Lien de la pull request :** https://github.com/RhazouaniMalak1/developpement-application-intelligente
- **Le tag `tp1` existe sur GitHub :** oui  
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?** 

## 8. Ce qui reste flou

Je dois encore mieux comprendre le chargement du modèle au démarrage de l'API, le passage des données validées au prédicteur et la transformation du résultat en réponse JSON. Je souhaite également mieux comprendre comment les tests automatisés vérifient les différents codes HTTP et les cas d'erreur.