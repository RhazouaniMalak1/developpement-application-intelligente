# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G1·  **Membres :** Mekkaoui Imane  ·  **Date :** 2026/2027

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant : je supprime vibration|422 |422 |
| 2 | valeur absurde : temperature = 500 | 422|422 |
| 3 | texte au lieu d'un nombre : vibration = imane |422 |422 |
| 4 | champ en trop : j'ai ajouter un champs weight = 50 | 422|422 |
| 5 | mauvaise route : http://localhost:8000/tp2| 404| 404 (Not Found) |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

NON

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
============================== 5 passed, 1 warning in 4.11s ==============================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

@pytest.mark.parametrize permet d’exécuter la même fonction de test plusieurs fois avec des données différentes.
pytest compte 5 tests pour test_requete_refusee, car CAS_REFUSES contient 5 cas. Chaque cas fournit une description, une URL, un corps de requête et le code HTTP attendu.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

ruff check . vérifie statiquement le code Python : style, imports inutilisés et certaines erreurs potentielles. Il n’exécute pas le programme.

python -m pytest exécute les tests pour vérifier que les fonctionnalités se comportent comme attendu. Les deux outils sont complémentaires : Ruff contrôle le code, pytest son comportement.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
=================================== 2 failed, 16 passed, 1 warning in 5.68s ===================================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Les deux tests qui échouent sont test_missing_key_is_rejected et test_wrong_key_is_rejected, dans test_security.py. Ils reçoivent 200 au lieu de 401.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    # TODO (TP2) : Comparez x_api_key à get_settings().api_key avec secrets.compare_digest : 401 si la clé est absente ou fausse, 500 si le serveur n'a pas de clé configurée
    api_key = get_settings().api_key
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )
    if x_api_key is None or not secrets.compare_digest(
        x_api_key.encode("utf-8"), api_key.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Deux tests échouent : celui qui vérifie l’absence de clé et celui qui vérifie une clé incorrecte. Ils reçoivent 200 au lieu de 401, car écrire require_api_key() dans security.py ne suffit pas : tant que cette fonction n’est pas ajoutée comme dépendance du router /v1, elle n’est pas appelée par les routes.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================= 18 passed, 1 warning in 5.82s =======================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---:|---|
| `GET /health`, sans clé | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-11-04T17:58:02Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Sans clé, l’API arrête le traitement dès l’authentification et renvoie 401. Avec la bonne clé, l’authentification passe, puis l’API valide les données : 500 °C dépasse la limite autorisée de 150 °C, donc elle renvoie 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

500 (Internal Server Error) Le serveur n’a pas chargé de clé, donc il ne peut pas vérifier celle envoyée par le client ; ce n’est pas une erreur de clé invalide (401).

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  // TODO (TP2) : Envoyez reading en POST JSON à <url>/v1/predict avec l'en-tête X-API-Key (fetch), puis affichez le résultat ou l'erreur avec show()
  const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
  const key = document.getElementById("key").value;

  try {
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key
      },
      body: JSON.stringify(reading)
    });
    const result = await response.json();

    if (!response.ok) {
      const detail = typeof result.detail === "string"
        ? result.detail
        : JSON.stringify(result.detail ?? result);
      show("err", `Erreur ${response.status} : ${detail}`);
      return;
    }

    const probability = (result.failure_probability * 100).toFixed(1);
    const message = `${result.alert ? "Alerte" : "Pas d’alerte"} — probabilité de panne : ${probability} %`;
    show(result.alert ? "alert" : "ok", message);
  } catch (error) {
    show("err", `Impossible de contacter l’API : ${error.message}`);
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | Alerte — probabilité de panne : 94.8 % |
| 500 °C, bonne clé |Erreur 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}] |
| relevé normal, fausse clé | Erreur 401 : Clé API absente ou invalide|

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche : Impossible de contacter l’API : Failed to fetch
La console (F12) affiche : Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

curl.exe n’applique pas la politique CORS : il envoie la requête et affiche la réponse du serveur. CORS est une règle appliquée par les navigateurs pour contrôler les requêtes initiées par une page web. Ainsi, l’API peut répondre à curl.exe, tandis que le navigateur bloque la réponse destinée à la page servie sur http://localhost:5501

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

4 tests échouent : les requêtes vers /v1/predict reçoivent 401 (clé API absente) au lieu du 422 attendu pour les données invalides.

Le cas « mauvaise route » passe : /tp2 n’existe pas et renvoie 404, comme attendu.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
=========== 5 passed, 1 warning in 1.94s ===========
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 signifie que l’authentification a échoué (clé absente ou invalide). 422 signifie que la requête est comprise, mais que ses données ne respectent pas les règles de validation. 403 signifie que l’utilisateur est authentifié, mais qu’il n’a pas l’autorisation d’accéder à la ressource.

2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   La clé est un secret : la mettre dans le code ou Git risquerait de la divulguer. Le fichier .env contient la vraie clé locale et ne doit pas être commité. .env.example contient un exemple ou des valeurs fictives pour montrer quelles variables configurer ; celui-là est commité.

3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Un en-tête comme X-API-Key est préférable à une URL, car les URL peuvent être enregistrées dans l’historique du navigateur, les journaux de serveurs ou des outils d’analyse.

4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   secrets.compare_digest compare les clés en temps constant, ce qui réduit le risque qu’un attaquant devine la clé en mesurant la durée de comparaison.

5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est définie par le schéma (http/https), le nom d’hôte et le port. http://localhost:5500 et http://localhost:8000 sont donc deux origines différentes, car leurs ports diffèrent.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui / non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

…
