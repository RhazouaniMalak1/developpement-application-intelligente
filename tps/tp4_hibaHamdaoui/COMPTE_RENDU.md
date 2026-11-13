# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G1  ·  **Membres :** Hamdaoui Hiba  ·  **Date :** 11/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
27 passed in 11.13s
```

Quels sont les deux tests qui peuvent échouer si le package n'est pas encore installé ?

Dans cette réalisation, aucun test n'a échoué, car j'ai aussi installé le package avec `pip install -e .` avant de lancer les tests. Sans cette étape, `test_installed_version_matches_the_code` et `test_command_is_declared` échouent : Python ne trouve pas les informations du package ni la commande `maintai-predict`.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "joblib>=1.5",
    "numpy>=2.4",
    "pandas>=3.0",
    "scikit-learn>=1.8",
]

[project.scripts]
maintai-predict = "maintai.cli:main"

[project.optional-dependencies]
api = ["fastapi>=0.115", "httpx>=0.28", "uvicorn[standard]>=0.30"]
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

Ce ne sont pas des dépendances nécessaires pour utiliser la prédiction de base. `pytest` sert aux tests, et FastAPI ainsi que `httpx` ne sont utiles que pour les fonctions liées à l'API et au client HTTP ; ils sont donc optionnels.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de pannes à partir de relevés de capteurs
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
27 passed in 15.15s
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

La commande affiche `Probabilité de panne : 95 % (ALERTE)`. Python affiche le chemin `C:\Users\ad\Downloads\maintai-starter-tp4\maintai\__init__.py`. Avec l'installation éditable, il utilise donc directement le code du dossier du projet.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le changement est visible. L'installation éditable pointe vers les fichiers du projet, qui sont utilisés directement sans réinstaller le package.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
maintai-0.2.0-py3-none-any.whl
maintai-0.2.0.tar.gz
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le modèle, les tests et `ui/` n'y sont pas. Le wheel contient le package `maintai` et ses métadonnées, car la configuration setuptools inclut seulement `maintai*`. Le modèle doit être fourni séparément.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `Modèle introuvable` sous `...\site-packages\models\model.joblib`, puis un message indiquant d'entraîner le modèle ou de renseigner `MAINTAI_MODELS_DIR`. |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | Des avertissements `InconsistentVersionWarning`, puis `Probabilité de panne : 95 % (ALERTE)`. La dépendance `scikit-learn>=1.8` installe une version plus récente (1.9.1 dans notre essai). |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)`, sans avertissement. |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Il apparaît si le modèle a été enregistré avec une version de scikit-learn différente de celle utilisée pour le charger. La ligne `"sklearn_version": "1.8.0"` indique la version utilisée pour entraîner et enregistrer ce modèle. L'avertissement apparaît avec la version 1.9.1 installée par défaut, puis disparaît après l'installation de la version 1.8.0.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   `requirements.txt` fixe les versions de l'environnement complet du projet, y compris les outils de test et l'API. `dependencies` liste les bibliothèques nécessaires au fonctionnement de base du package, avec des versions minimales.
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   `pip install -e .` installe le package en mode éditable et utilise le code du dossier du projet. Installer le wheel installe une copie construite du package, qui ne change pas quand on modifie les fichiers sources.
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   C'est une commande créée par pip qui appelle une fonction du package. Sous Windows, pip place `maintai-predict.exe` dans le dossier `Scripts` de l'environnement Python. Dans l'environnement utilisé ici : `C:\Users\ad\AppData\Local\Programs\Python\Python313\Scripts\maintai-predict.exe`.

## 5. Le rendu Git

- Lien de la pull request : .
- Le tag `tp4` existe sur GitHub :oui
- `git status` avant le commit : .


