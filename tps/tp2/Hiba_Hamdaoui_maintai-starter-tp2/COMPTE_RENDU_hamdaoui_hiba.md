# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G1  ·  **Membres :** Hamdaoui Hiba  ·  **Date :** 04/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant : je supprime vibration | 422 | 422 |
| 2 | valeur absurde : temperature=500  | 422 | 422 |
| 3 | texte au lieu d'un nombre temperature="chaud" | 422 | 422 |
| 4 | champ en trop : j'ajoute un champs "nom_machine"="A"| 422 | 422 |
| 5 | mauvaise route http://localhost:8000/hiba | 404 | 404({"detail":"Not Found"}) |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

non

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
======================== 5 passed in 4.59s ========================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

@pytest.mark.parametrize permet d'exécuter la même fonction de test plusieurs fois avec des données et des résultats attendus différents. Pytest compte 5 tests pour notre fonction, car CAS_REFUSES contient 5 cas de test différents.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
PIE790 [*] Unnecessary `pass` statement
  --> maintai\api\schemas.py:22:5
   |
20 |     load_pct: float = Field(ge=0, le=100, description="Charge en pourcentage")
21 |     runtime_hours: float = Field(ge=0, le=100000, description="Temps de fonctionnement en heures")
22 |     pass
   |     ^^^^
help: Remove unnecessary `pass`
   |
21 |     runtime_hours: float = Field(ge=0, le=100000, description="Temps de fonctionnement en heures")
   -     pass
22 |
   |

UP017 [*] Use `datetime.UTC` alias
  --> maintai\train.py:58:36
   |
56 |         "target": TARGET,
57 |         "threshold": settings.threshold,
58 |         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
   |                                    ^^^^^^^^^^^^
59 |         "sklearn_version": sklearn.__version__,
60 |     }
   |
help: Convert to `datetime.UTC` alias
   |
5  | import json
   - from datetime import datetime, timezone
6  + from datetime import datetime, timezone, UTC
7  |
--------------------------------------------------------------------------------
57 |         "threshold": settings.threshold,
   -         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
58 +         "trained_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
59 |         "sklearn_version": sklearn.__version__,
   |

I001 [*] Import block is un-sorted or un-formatted
 --> tests\test_casser.py:1:1
  |
1 | import pytest
  | ^^^^^^^^^^^^^
2 | VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}
3 | CAS_REFUSES = [
  |
help: Organize imports
  |
1 | import pytest
2 +
3 | VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}
  |

Found 3 errors.
[*] 3 fixable with `--fix`.
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

ruff check . analyse statiquement le code pour détecter les erreurs, les imports inutilisés et les problèmes de qualité et de style.



python -m pytest exécute les tests automatisés pour vérifier que les fonctions et l'API produisent les résultats attendus.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
================================ 18 passed in 4.80s =======================================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Dans l'état actuel, aucun : les 18 tests passent. Les deux tests concernés par l'authentification sont `test_missing_key_is_rejected` et `test_wrong_key_is_rejected`; avant la mise en place de la vérification de clé, chacun aurait reçu 200 au lieu de 401 (avec le modèle chargé).

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    # TODO (TP2) : Comparez x_api_key à get_settings().api_key avec secrets.compare_digest : 401 si la clé est absente ou fausse, 500 si le serveur n'a pas de clé configurée
    api_key = get_settings().api_key
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Clé API non configurée sur le serveur"
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou absente"
        )

```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API invalide ou absente"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API invalide ou absente"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.9475,"alert":true,"threshold":0.3,"model_version":"2026-11-04T17:55:59Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API invalide ou absente"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | Erreur de validation Pydantic : `temperature_c` doit être inférieur ou égal à 150. |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Sans clé, la dépendance d'authentification refuse d'abord la requête et renvoie 401. Avec une clé valide, la requête passe l'authentification puis la validation Pydantic détecte que 500 °C dépasse la limite de 150 °C et renvoie 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

500 : sans le fichier `.env`, `MAINTAI_API_KEY` n'est pas configurée côté serveur. Le contrôle renvoie une erreur de configuration serveur avant de comparer la clé fournie; 401 correspond à une clé absente ou incorrecte lorsque le serveur a bien une clé configurée.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
addEventListener("click", async () => {
  const reading = Object.fromEntries(
    FEATURES.map(f => [f, Number(document.getElementById(f).value)])
  );

  const url = document.getElementById("url").value.replace(/\/$/, "");
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

    const data = await response.json();

    if (!response.ok) {
      show("alert", `Erreur ${response.status} : ${data.detail || "Erreur inconnue"}`);
      return;
    }

    show("ok", JSON.stringify(data, null, 2));

  } catch (error) {
    show("err", `Impossible de contacter l'API : ${error.message}`);
  }
})
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | Un résultat JSON contenant `failure_probability: 0.9475`, `alert: true`, `threshold: 0.3` et `model_version: "2026-11-04T17:55:59Z"` pour l'exemple fourni et le modèle chargé. |
| 500 °C, bonne clé | `Erreur 422` et le détail de validation indiquant que la température doit être inférieure ou égale à 150. |
| relevé normal, fausse clé | `Erreur 401 : Clé API invalide ou absente`. |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page ne peut pas lire la réponse et affiche généralement `Impossible de contacter l'API : Failed to fetch`. La console indique que la requête est bloquée par la politique CORS : l'origine `http://localhost:5501` n'est pas autorisée par l'API. Le texte exact dépend du navigateur.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

`curl.exe` n'est pas un navigateur et n'applique pas la politique CORS. CORS est une restriction imposée par les navigateurs aux scripts web; l'API peut donc répondre à curl tout en refusant au navigateur l'accès à la réponse.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Quatre tests échouent : les quatre requêtes qui atteignent `/v1/predict` reçoivent 401 avant la validation du corps. Le cas de la mauvaise route passe quand même avec 404, car aucune route ne correspond et elle n'atteint donc pas la dépendance de sécurité du router `/v1`.

Le fichier `test_casser.py` n'est pas présent dans le dépôt fourni, donc l'exécution après sa copie avec `headers=HEADERS` n'est pas vérifiable ici. La suite actuelle du dépôt (sans ces cinq cas supplémentaires) se termine ainsi :

```
============================= 18 passed in 28.52s =============================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 signifie que l'authentification est absente ou invalide. 422 signifie que la requête a été comprise, mais que ses données ne respectent pas les règles de validation. 403 signifie que l'identité est connue ou la requête authentifiée, mais que l'accès à la ressource n'est pas autorisé.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   Une clé est un secret : la placer dans le code ou dans Git la rendrait visible et difficile à révoquer. `.env` contient la vraie valeur locale et doit rester ignoré par Git; `.env.example` fournit des noms de variables et des valeurs fictives, et peut être commité. Il faut remplacer la valeur d'exemple avant d'utiliser l'API.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Un en-tête dédié (`X-API-Key`) évite d'exposer la clé dans l'historique du navigateur, les journaux d'accès, les favoris ou les URL partagées. En production, la connexion doit aussi être protégée par HTTPS.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   Il effectue une comparaison conçue pour ne pas révéler progressivement des informations via les différences de temps d'exécution liées au nombre de caractères déjà comparés, réduisant ainsi les fuites temporelles.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est définie par le schéma, l'hôte et le port. Ces deux URL ont le même schéma et le même hôte, mais des ports différents : ce sont donc deux origines distinctes.

## 8. Le rendu Git

- Lien de la pull request : aucun, le dépôt est publié directement sur `main`.
- Le tag `tp2` existe sur GitHub : non vérifié; aucun tag n'a été créé dans le cadre de ce rendu.
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non, il est ignoré par `.gitignore`.
- Qui a relu la pull request, et quel commentaire a-t-il laissé ? Aucun commentaire disponible; aucune pull request n'a été créée.


## 9. Ce qui reste flou

Je voudrais encore clarifier comment choisir et réévaluer le seuil de décision en fonction du coût relatif des fausses alertes et des pannes manquées, ainsi que la validation du modèle sur de vrais relevés de capteurs avant tout usage opérationnel.
