# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
=================== 2 failed, 25 passed, 1 warning in 43.50s ===================
```

Quels sont les deux tests qui échouent, et pourquoi ?

Les deux tests qui échouent sont `test_installed_version_matches_the_code` et `test_command_is_declared` (dans `tests/test_package.py`).
Ils échouent parce que le package `maintai` n'a pas encore été installé dans l'environnement virtuel `.venv` (via `pip install -e .`), ses métadonnées et sa commande CLI `maintai-predict` sont donc introuvables.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "numpy>=1.26",
    "pandas>=2.2",
    "scikit-learn>=1.4",
    "joblib>=1.3",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

dependencies ne contient que les bibliothèques strictement indispensables à l'exécution du cœur du package (maintai/), afin de garder l'installation légère.

pytest et fastapi sont placés dans [project.optional-dependencies] car ils ne sont utiles que pour des usages spécifiques :

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Package de maintenance prédictive par apprentissage automatique.
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================= 27 passed, 1 warning in 9.01s ========================
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

maintai-predict 72 6 85 15000 : la commande est bien reconnue depuis n'importe quel dossier, mais indique Modèle introuvable : ...\models\model.joblib (le modèle n'ayant pas encore été entraîné via python -m maintai.train).

python -c "import maintai; print(maintai.__file__)" : affiche C:\Users\dell\Documents\projet_app_intelligente\TP4\maintai-starter-tp4\maintai\__init__.py.

Où Python trouve-t-il le code ? Directement dans le dossier source de développement (...\maintai-starter-tp4\maintai\), grâce à l'installation en mode éditable (pip install -e .).

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le nouveau message ([TEST EDITABLE] Modèle introuvable...) s'affiche immédiatement sans réinstallation.
Grâce à l'installation en mode éditable (pip install -e .), pip ne copie pas les fichiers dans site-packages mais crée un pointeur vers le dossier source (maintai/). Python exécute donc directement ton fichier modifié.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
Directory: C:\Users\dell\Documents\projet_app_intelligente\TP4\maintai-starter-tp4\dist

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        11/12/2026   7:47 PM          11658 maintai-0.2.0-py3-none-any.whl
-a----        11/12/2026   7:47 PM          12290 maintai-0.2.0.tar.gz
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

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | Modèle introuvable : C:\Users\dell\AppData\Local\Temp\essai\Lib\site-packages\models\model.joblib — Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR.|
| avec `MAINTAI_MODELS_DIR` vers vos `models` |Trois avertissements InconsistentVersionWarning: Trying to unpickle estimator ... from version 1.8.0 when using version 1.9.1, suivis de : Probabilité de panne : 95 % (ALERTE) |
| après `pip install scikit-learn==1.8.0` |Probabilité de panne : 95 % (ALERTE) (sans aucun avertissement InconsistentVersionWarning) |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Le modèle (model.joblib) a été entraîné et sauvegardé avec scikit-learn 1.8.0, alors que l'environnement essai a installé la dernière version (1.9.1) pour le charger. Ce décalage de version entre la sérialisation et le chargement déclenche l'alerte.

Ligne dans models/model_info.json : La ligne "sklearn_version": "1.8.0" (qui trace la version exacte utilisée lors de l'entraînement).

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   dependencies dans pyproject.toml définit les dépendances abstraites minimales dont le package a besoin pour fonctionner (ex. scikit-learn>=1.4), afin qu'il reste compatible avec d'autres projets lors de sa distribution.

requirements.txt fige généralement les versions exactes de tout l'environnement d'exécution (y compris les sous-dépendances) pour garantir une reproduction à l'identique sur un serveur ou une machine précise.
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   pip install -e . (mode éditable) ne copie pas le code dans site-packages : il crée un lien vers le dossier de développement, permettant de tester immédiatement chaque modification du code sans réinstaller.

pip install dist\maintai-0.2.0-py3-none-any.whl (installation standard depuis un wheel) copie une archive figée et autonome du code dans site-packages ; c'est le mode utilisé pour déployer le package en production.

3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   Un point d'entrée associe un nom de commande système (maintai-predict) à une fonction Python précise (maintai.cli:main), permettant de lancer le programme directement depuis n'importe quel terminal sans écrire python -m ....

Sur Windows, pip génère l'exécutable maintai-predict.exe dans le dossier Scripts\ de l'environnement virtuel actif (.venv\Scripts\maintai-predict.exe).

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? oui / non

## 6. Ce qui reste flou

…
