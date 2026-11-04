# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G1 
**Membres :** Najim Aya
**Date :** 04/11/2026

## 1. Activité 1 : casser son API (dans `TP/TP1`)

### Les cinq requêtes testées

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | Champ obligatoire manquant (`temperature_c`) | 422 | 422 |
| 2 | Température trop petite (`-50`) | 422 | 422 |
| 3 | Texte au lieu d'un nombre | 422 | Erreur de format JSON |
| 4 | Champ supplémentaire (`nom`) | 422 | 422 |
| 5 | Mauvaise route | 404 | 404 après correction du test |

### Une de mes prévisions était-elle fausse ? Laquelle, et pourquoi ?

Oui, ma prévision était fausse pour la troisième requête : j'ai obtenu une erreur de format JSON, ce qui montre que le JSON que j'avais envoyé était mal formé. Pour tester réellement le type de la donnée, il faut transmettre un JSON valide dans lequel un texte remplace le nombre attendu.

Pour la cinquième requête, mon test comportait une erreur : je me servais toujours de la route `/v1/predict`, alors que je voulais viser une route inexistante. Une fois le test corrigé, les cinq tests de requêtes refusées sont passés.

### Dernière ligne de `python -m pytest` avec `tests/test_casser.py`

Commande lancée dans le dossier `maintai-starter-tp1` :

```text
19 passed, 1 warning in 3.74s
```

Les 19 tests sont réussis. Un avertissement lié à `httpx` et à `starlette.testclient` s'affiche aussi, mais il ne fait échouer aucun test.

### À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize` sert à exécuter une même fonction de test sur plusieurs jeux de données, sans avoir à écrire une fonction par requête.

Dans mon fichier `test_casser.py`, j'ai défini cinq cas. Pytest lance donc cinq tests distincts pour cette fonction, un par requête.

En tout, pytest a exécuté 19 tests dans le projet, puisque d'autres tests couvrent l'API, le client, les données et l'entraînement du modèle.

## 2. Ruff

### Sortie de `ruff check .` dans `TP/TP1`

À la première exécution, Ruff a relevé trois problèmes :

```text
PIE790 : instruction pass inutile dans maintai/api/schemas.py
UP017 : utilisation recommandée de datetime.UTC dans maintai/train.py
I001 : imports mal organisés dans tests/test_casser.py

Found 3 errors.
3 fixable with --fix.
```

J'ai ensuite lancé les commandes suivantes :

```powershell
ruff check . --fix
ruff format .
```

Ruff a signalé que cinq problèmes avaient été corrigés automatiquement et que 11 fichiers avaient été reformatés.

```text
Found 5 errors (5 fixed, 0 remaining).
11 files reformatted, 7 files left unchanged
```

### Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff check .` contrôle la qualité du code Python : il repère les problèmes de style, les imports mal rangés et certaines mauvaises pratiques, et peut en corriger une partie automatiquement grâce à l'option `--fix`.

`python -m pytest` lance les tests automatiques afin de s'assurer que le programme se comporte comme prévu.

Les deux outils se complètent : Ruff s'intéresse surtout à la qualité du code, pytest à son bon fonctionnement.

Après avoir installé Ruff, j'ai désactivé mon environnement virtuel avant de relancer pytest, ce qui a produit l'erreur `ModuleNotFoundError: No module named 'fastapi'`. Cela indique que Python utilisait un environnement dépourvu de FastAPI. Il faut donc réactiver le bon environnement virtuel avant de relancer les tests.

## Conclusion

J'ai appris à interpréter les codes HTTP, à automatiser les tests avec pytest et à améliorer la qualité du code Python avec Ruff.


## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
====== 2 failed, 16 passed, 1 warning in 4.85s ======
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Ils obtiennent un code 200 OK au lieu de 401 Unauthorized. La protection par clé API n'est pas encore branchée sur le routeur : le serveur traite donc la requête normalement, sans contrôler la clé.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""

    api_key = get_settings().api_key

    # 1. Vérifier que le serveur possède une clé API configurée
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    # 2. Refuser si la clé du client est absente
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante",
        )

    # 3. Comparer les clés de manière sécurisée
    if not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)],
)
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

La fonction `require_api_key` est bien définie, mais tant qu'elle n'est pas rattachée à `router = APIRouter(dependencies=[Depends(require_api_key)])`, FastAPI ne l'exécute jamais. Les routes `/v1/*` demeurent donc ouvertes à tous et répondent 200.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
====== 18 passed, 1 warning in 4.76s =======
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API manquante"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.9475,"alert":true,"threshold":0.3,"model_version":"2026-11-04T19:24:17Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API manquante"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

La dépendance d'authentification s'exécute avant la validation du corps de la requête. En l'absence de clé, FastAPI renvoie aussitôt un 401, sans même examiner la température. Avec la bonne clé, l'authentification passe, puis Pydantic refuse 500 °C par un 422, car `temperature_c` ne doit pas dépasser 150 °C.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

Le serveur répond 500 avec `{"detail":"Clé API non configurée sur le serveur"}`. Ce n'est pas un 401 parce que le serveur ne trouve aucune variable `MAINTAI_API_KEY` dans son environnement. Avant de comparer la clé du client, `require_api_key()` contrôle d'abord la configuration du serveur, et signale un problème de configuration par un 500.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const button = document.getElementById("go");

  try {
    const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
    const key = document.getElementById("key").value.trim();
    const reading = Object.fromEntries(
      FEATURES.map(f => [f, Number(document.getElementById(f).value)])
    );

    button.disabled = true;
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key
      },
      body: JSON.stringify(reading)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail = typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail ?? data);

      if (response.status === 401) {
        show("err", "Erreur 401 : clé API absente ou invalide.");
      } else if (response.status === 503) {
        show("err", "Erreur 503 : le modèle n'est pas chargé.");
      } else {
        show("err", `Erreur HTTP ${response.status} : ${detail}`);
      }
      return;
    }

    show("ok", JSON.stringify(data, null, 2));
  } catch (error) {
    show("err", "Impossible de contacter l'API.\n" + error.message);
  } finally {
    button.disabled = false;
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | La page montre le JSON complet de la prédiction : probabilité, alerte, seuil et version du modèle, par exemple. |
| 500 °C, bonne clé | `Erreur HTTP 422 :` suivi du détail précisant que `temperature_c` doit être inférieur ou égal à 150 °C. |
| relevé normal, fausse clé | `Erreur 401 : clé API absente ou invalide.` |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

Servie sur le port 5501, la page n'arrive pas à interroger l'API située sur le port 8000. La console affiche une erreur CORS précisant que la requête issue de l'origine `http://localhost:5501` n'est pas autorisée par l'API.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

`curl.exe` est un simple client HTTP en ligne de commande, et la politique CORS du navigateur ne s'applique pas à lui. CORS ne concerne que les scripts qui s'exécutent dans une page web. La réponse existe bel et bien : c'est le navigateur qui en bloque la lecture, ou l'envoi de la requête, quand l'origine n'est pas autorisée.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Sans `headers=HEADERS`, quatre tests échouent et reçoivent un 401 à la place du résultat attendu : l'authentification bloque les cas de données invalides avant leur validation. Le cas de la mauvaise route passe malgré tout avec un 404, car aucune route correspondante n'existe, donc rien n'est à protéger.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
====== 18 passed, 1 warning in 2.81s ======
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   Un 401 indique que l'identité n'est pas prouvée : la clé est absente ou invalide. Un 422 indique que l'identité est valide, mais que le corps de la requête ne respecte pas le schéma Pydantic. Un 403 indique que l'identité est reconnue, mais que l'accès ou l'opération demandée n'est pas permis.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   `.env` renferme la configuration locale, dont la vraie clé API, et Git l'ignore. `.env.example` contient une clé fictive à remplacer ainsi que les variables attendues ; il peut être commité pour documenter la configuration. Les vraies clés ne doivent jamais figurer dans le code source ni dans le dépôt.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Avec un en-tête `X-API-Key`, le secret n'apparaît ni dans l'URL, ni dans les favoris, ni dans l'historique du navigateur, ni dans certains logs. Une clé placée dans l'URL serait bien plus facilement exposée. En production, les échanges doivent en plus passer par HTTPS.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   `secrets.compare_digest` compare les chaînes en temps constant, ce qui réduit le risque d'attaques par mesure du temps lors de la vérification d'un secret. Il évite ainsi l'arrêt anticipé de la comparaison que peut provoquer `==`.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est le triplet `(schéma, nom de domaine, port)`. Ces deux URLs ont le même schéma et le même domaine, mais pas le même port : il ne s'agit donc pas de la même origine.

## 8. Le rendu Git

- Lien de la pull request : le dépôt est publié sur main.
- Le tag `tp2` existe sur GitHub : à renseigner sur GitHub
- `git status` avant le commit : le fichier `.env` n'apparaissait pas, car `.gitignore` l'exclut
- Qui a relu la pull request, et quel commentaire a-t-il laissé ? aucune pull request n'a été créée.

## 9. Ce qui reste flou

Je voudrais encore clarifier le mécanisme exact de CORS (qui décide de bloquer la requête, le navigateur ou le serveur, et comment l'API déclare les origines autorisées), ainsi que l'ordre complet d'exécution d'une requête, notamment pourquoi une mauvaise route renvoie 404 même sans clé alors que les routes protégées renvoient 401 avant la validation du corps en 422. Je voudrais aussi mieux distinguer ce qui se passe côté client (page web, `curl.exe`) et côté serveur (uvicorn, FastAPI) pour savoir où se fait chaque vérification.