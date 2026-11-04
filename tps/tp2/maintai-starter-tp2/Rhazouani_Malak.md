
# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G1 
**Membres :** malak rhazouani
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

Oui, pour la troisième requête, le résultat obtenu était une erreur de format JSON. Cela signifie que le JSON envoyé était mal écrit. Pour vérifier le type de donnée, il faut envoyer un JSON valide contenant du texte à la place d'un nombre.

Pour la cinquième requête, j'ai eu une erreur dans mon test, car j'utilisais encore la route `/v1/predict` alors que je voulais tester une mauvaise route. J'ai corrigé le test et les cinq tests des requêtes refusées ont ensuite réussi.

### Dernière ligne de `python -m pytest` avec `tests/test_casser.py`

Commande exécutée dans le dossier `maintai-starter-tp1` :

```text
19 passed, 1 warning in 3.74s
```

Les 19 tests ont réussi. Un avertissement concernant `httpx` et `starlette.testclient` est également affiché, mais il n'empêche pas les tests de réussir.

### À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize` permet de tester plusieurs cas avec une seule fonction de test. Cela évite d'écrire une fonction différente pour chaque requête.

Dans mon fichier `test_casser.py`, j'ai utilisé cinq cas de test. Pytest exécute donc cinq tests différents pour cette fonction, un pour chaque requête.

Au total, pytest a exécuté 19 tests dans le projet, car il y a aussi des tests pour l'API, le client, les données et l'entraînement du modèle.

## 2. Ruff

### Sortie de `ruff check .` dans `TP/TP1`

Lors de la première exécution, Ruff a trouvé trois problèmes :

```text
PIE790 : instruction pass inutile dans maintai/api/schemas.py
UP017 : utilisation recommandée de datetime.UTC dans maintai/train.py
I001 : imports mal organisés dans tests/test_casser.py

Found 3 errors.
3 fixable with --fix.
```

J'ai ensuite exécuté les commandes suivantes :

```powershell
ruff check . --fix
ruff format .
```

Ruff a indiqué que cinq problèmes avaient été corrigés automatiquement et que 11 fichiers avaient été reformattés.

```text
Found 5 errors (5 fixed, 0 remaining).
11 files reformatted, 7 files left unchanged
```

### Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff check .` permet de vérifier la qualité du code Python. Il détecte notamment les problèmes de style, les imports mal organisés et certaines mauvaises pratiques. Il peut aussi corriger automatiquement certains problèmes avec l'option `--fix`.

`python -m pytest` permet d'exécuter les tests automatiques pour vérifier que le programme fonctionne correctement.

Les deux outils sont complémentaires : Ruff vérifie principalement la qualité du code, tandis que pytest vérifie son fonctionnement.

Après avoir installé Ruff, j'ai désactivé mon environnement virtuel avant de relancer pytest. J'ai alors obtenu l'erreur `ModuleNotFoundError: No module named 'fastapi'`. Cela signifie que Python utilisait un environnement dans lequel FastAPI n'était pas installé. Il faut réactiver le bon environnement virtuel avant de relancer les tests.

## Conclusion

 J'ai appris à interpréter les codes HTTP, à utiliser pytest pour automatiser les tests et à utiliser Ruff pour améliorer la qualité du code Python.


## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
====== 2 failed, 16 passed, 1 warning in 4.85s ======
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Ils reçoivent un code 200 OK au lieu de 401 Unauthorized, car la protection par clé API n'est pas encore appliquée au routeur : le serveur accepte et traite la requête normalement sans vérifier la clé.

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

La fonction require_api_key existe, mais tant qu'elle n'est pas injectée dans router = APIRouter(dependencies=[Depends(require_api_key)]), FastAPI ne l'appelle pas. Les routes /v1/* restent publiques et renvoient 200.

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

La dépendance d'authentification est exécutée avant la validation du corps. Sans clé, FastAPI répond immédiatement avec 401, avant de contrôler la température. Avec la bonne clé, la dépendance réussit, puis Pydantic rejette 500 °C avec 422, car `temperature_c` doit être inférieur ou égal à 150 °C.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

Le serveur retourne 500 avec le détail `{"detail":"Clé API non configurée sur le serveur"}`. Ce n'est pas 401, car le serveur ne trouve pas de clé `MAINTAI_API_KEY` dans son environnement. Avant de comparer la clé du client, `require_api_key()` vérifie donc la configuration du serveur et signale une erreur de configuration avec 500.

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
| relevé normal, bonne clé | La page affiche le JSON complet de la prédiction, par exemple la probabilité, l'alerte, le seuil et la version du modèle. |
| 500 °C, bonne clé | `Erreur HTTP 422 :` suivi du détail indiquant que `temperature_c` doit être inférieur ou égal à 150 °C. |
| relevé normal, fausse clé | `Erreur 401 : clé API absente ou invalide.` |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page servie sur le port 5501 ne peut pas effectuer la requête vers l'API du port 8000. La console affiche une erreur CORS indiquant que la requête provenant de l'origine `http://localhost:5501` n'est pas autorisée par l'API.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

`curl.exe` agit comme un client HTTP en ligne de commande et ne soumet pas ses requêtes à la politique CORS du navigateur. CORS est imposée uniquement aux scripts exécutés dans une page web. La réponse existe bien, mais le navigateur bloque sa lecture ou son envoi lorsque l'origine n'est pas autorisée.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Sans `headers=HEADERS`, quatre tests échouent avec le code 401 au lieu du résultat attendu. Les cas de données invalides sont d'abord bloqués par l'authentification. Le cas de mauvaise route passe quand même avec le code 404, puisqu'il n'existe aucune route correspondante à protéger.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
====== 18 passed, 1 warning in 2.81s ======
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 signifie que l'identité n'a pas été prouvée : la clé est absente ou invalide. 422 signifie que l'identité est valide, mais que le corps ne respecte pas le schéma Pydantic. 403 signifie que l'identité est connue, mais que l'accès ou l'opération demandée n'est pas autorisé.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   `.env` contient la configuration locale, notamment la vraie clé API, et est ignoré par Git. `.env.example` contient une clé fictive à remplacer et les variables attendues, et peut être commité pour documenter la configuration. Les vraies clés ne doivent jamais être placées dans le code source ni dans le dépôt.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Un en-tête `X-API-Key` évite que le secret apparaisse dans l'URL, les favoris, l'historique du navigateur ou certains logs. Une clé placée dans l'URL serait beaucoup plus facilement exposée. En production, l'échange doit également être effectué via HTTPS.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   `secrets.compare_digest` compare les chaînes en temps constant, ce qui limite les attaques par mesure du temps lors de la vérification d'un secret. Il évite les comparaisons courtes-circuitées possibles avec `==`.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est le triplet `(schéma, nom de domaine, port)`. Ces deux URLs utilisent le même schéma et le même domaine, mais des ports différents : ce ne sont donc pas la même origine.

## 8. Le rendu Git

- Lien de la pull request : 
- Le tag `tp2` existe sur GitHub : à renseigner sur GitHub
- `git status` avant le commit : le fichier `.env` n'apparaissait pas, car il est ignoré par `.gitignore`
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  
## 9. Ce qui reste flou

