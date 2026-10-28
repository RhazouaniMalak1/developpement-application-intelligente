# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G1 · **Membre :** Imane Mekkaoui · **Date :** 28/10/2026

> Complétez les différentes sections de ce document, puis soumettez-le avec la pull request du TP1.  
> Insérez les résultats du terminal entre les lignes de trois accents graves.

---

## 1. Mise en place

Dernière ligne affichée par `python -m pytest` après la mise en place :

```text
======================================== 3 failed, 10 passed, 1 warning in 7.35s ========================================
```

Dans `tests/test_api.py`, 10 tests sur 13 réussissent déjà avant même l’ajout de code. Il faut consulter ce fichier pour relever le nom précis des tests concernés.

Les deux tests qui s’attendent à recevoir le code `422` peuvent réussir pour une raison différente de celle recherchée : avec `extra="forbid"`, Pydantic rejette les champs absents du schéma, mais cette option ne suffit pas à vérifier que les mesures des capteurs respectent des limites physiques. Sans les contraintes `ge` et `le`, une valeur du mauvais intervalle, mais du bon type, risque d’être acceptée.

Pour connaître le troisième test en échec, il faut examiner le compte rendu détaillé de `pytest`.

## 2. Le schéma d’entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min/max des données) |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | Plage de température plausible pour une machine industrielle. |
| `vibration_mm_s` | `float` | 0 | 100 | La vibration mesurée ne peut pas être négative ; 100 mm/s est une limite supérieure de validation. |
| `load_pct` | `float` | 0 | 100 | Le pourcentage de charge est compris entre 0 % et 100 %. |
| `runtime_hours` | `float` | 0 | 100000 | Le temps de fonctionnement cumulé ne peut pas être négatif ; 100 000 heures est une limite de validation choisie pour le TP. |

Ces valeurs sont des bornes utilisées pour valider les entrées de l’API ; elles ne représentent pas des limites de sécurité qui s’appliqueraient universellement à toutes les machines industrielles.

Après avoir implémenté uniquement `schemas.py`, lancer `python -m pytest` et noter le résultat obtenu :

```text
============================================= 13 passed, 1 warning in 5.78s ============================================
```

Le résultat indique que les 13 tests passent après l’ajout du schéma. Les tests servent à vérifier que les fonctionnalités de l’API respectent le comportement attendu.

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

    return predictor.predict(reading.model_dump())
```

**Pourquoi utiliser le code 503 plutôt que 500 si le modèle n’est pas chargé ?**

Le code `503 Service Unavailable` signifie que le service ne peut temporairement pas répondre, ici parce que le modèle n’est pas disponible. À l’inverse, `500 Internal Server Error` signale généralement un problème interne inattendu du serveur.

**Pourquoi charger le modèle au démarrage une seule fois, plutôt qu’à chaque requête ?**

Le chargement d’un modèle peut être long et consommer beaucoup de mémoire. En le chargeant une seule fois au démarrage, l’API peut le réutiliser pour chaque requête, accélérer les réponses et éviter de répéter inutilement cette opération.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```text
============================================= 13 passed, 1 warning in 5.78s ============================================
```

## 5. L’API en marche

Après l’exécution des commandes suivantes :

```powershell
python -m maintai.dataset
python -m maintai.train
uvicorn maintai.api.main:app --reload
```

Ouvrir `http://localhost:8000/docs` et essayer les requêtes ci-dessous.

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---|---|
| `GET /health` | `200` si l’API fonctionne | `{"status":"ok","model_loaded":true}` si le modèle est chargé. |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | `200` si la prédiction réussit | JSON contenant `failure_probability`, `alert`, `threshold` et `model_version`. Les valeurs dépendent du modèle entraîné. |
| `POST /v1/predict` avec une température de `500` | `422` attendu | JSON de validation indiquant que la température dépasse la limite maximale de 150 °C. |
| `POST /v1/predicte` (faute de frappe dans l’adresse) | `404` attendu | `{"detail":"Not Found"}` |

Il faut vérifier les codes et le contenu des réponses à partir des résultats effectivement renvoyés par l’API.

**Dans `/docs`, à quel endroit les bornes choisies sont-elles indiquées ?**

Elles apparaissent dans le schéma de la requête `POST /v1/predict`, dans le modèle `SensorReading`. La documentation OpenAPI les affiche grâce aux contraintes `ge` et `le` définies dans les champs Pydantic.

## 6. Questions de compréhension

### 1. REST et FastAPI : quelle différence entre les deux ?

REST désigne un style d’architecture reposant sur des principes de conception d’API web. FastAPI est un framework Python qui sert à construire des API web, notamment celles qui suivent les principes REST.

### 2. Quelles sont les trois fonctions du schéma Pydantic ?

- Vérifier le type des données reçues et contrôler qu’elles respectent les bornes définies.
- Rejeter les données invalides et, avec `extra="forbid"`, refuser les champs supplémentaires non autorisés.
- Produire le schéma de documentation utilisé par OpenAPI et Swagger UI.

### 3. Dans `http://localhost:8000/v1/predict`, que signifient `localhost`, `8000` et `/v1/predict` ?

- `localhost` correspond à l’ordinateur sur lequel l’API est lancée.
- `8000` est le port utilisé par défaut par Uvicorn dans la commande donnée.
- `/v1/predict` est le chemin de l’endpoint de prédiction de la première version de l’API.

### 4. À quoi sert `/v1` dans l’adresse ?

`/v1` précise la version de l’API. Cette indication permet de faire évoluer l’API sans nécessairement interrompre les clients qui utilisent une version précédente.

### 5. Dans `uvicorn maintai.api.main:app`, que représentent `maintai.api.main` et `app` ?

- `maintai.api.main` désigne le module Python où se trouve le code de l’API.
- `app` est l’objet `FastAPI` défini dans ce module et exécuté par Uvicorn.

## 7. Le rendu Git

- **Lien de la pull request :** https://github.com/RhazouaniMalak1/developpement-application-intelligente
- **Le tag `tp1` existe sur GitHub :** oui  
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?**

## 8. Points restant à éclaircir

Je souhaite approfondir le chargement du modèle au démarrage de l’API, la transmission des données validées au prédicteur et la conversion de sa sortie en réponse JSON. Je veux aussi mieux comprendre de quelle manière les tests automatisés contrôlent les différents codes HTTP et les situations d’erreur.
