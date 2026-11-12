# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** …  
**Membres :** RHAZOUANI MALAK  
**Date :** 11/11/2026

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

**Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :**

```text
==================================== 2 failed, 25 passed, 1 warning in 24.14s =====================================
```

**Quels sont les deux tests qui échouent, et pourquoi ?**

- `test_installed_version_matches_the_code` : ce test vérifie que le package `maintai` est installé et que sa version correspond à celle déclarée dans le code (`maintai.__version__`). Au début, le package n'était pas encore installé correctement.
- `test_command_is_declared` : ce test vérifie que la commande `maintai-predict` est déclarée parmi les commandes disponibles. Elle n'était pas encore configurée dans `pyproject.toml`.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

**Vos sections `dependencies` et `[project.scripts]` :**

```toml
# Fiche d'identité du package maintai

[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "maintai"
dynamic = ["version"]
description = "Package Python pour la prédiction et l'analyse des données de maintenance industrielle."
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "pandas>=2.2",
    "numpy>=1.26",
    "scikit-learn>=1.5",
    "joblib>=1.4"
]

[project.optional-dependencies]
api = ["fastapi>=0.115", "uvicorn[standard]>=0.30"]
ui = ["streamlit>=1.40"]
dev = ["pytest>=8", "ruff"]

[project.scripts]
maintai-predict = "maintai.cli:main"

[tool.setuptools.dynamic]
version = {attr = "maintai.__version__"}

[tool.setuptools.packages.find]
include = ["maintai*"]
```

**Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?**

`pytest` sert à exécuter les tests pendant le développement. Il n'est donc pas nécessaire pour tous les utilisateurs du package. `fastapi` est utilisé uniquement si on souhaite lancer l'API. Ces deux bibliothèques sont placées dans les dépendances optionnelles (`dev` et `api`) pour éviter d'installer des bibliothèques qui ne sont pas toujours utiles.

**Sortie de `pip show maintai` :**

```text
Name: maintai
Version: 0.2.0
Summary: Package Python pour la prédiction et l'analyse des données de maintenance industrielle.
Home-page:
Author:
Author-email:
License:
Location: C:\Users\USER\Downloads\TP4\maintai-starter-tp4\.env\Lib\site-packages
Editable project location: C:\Users\USER\Downloads\TP4\maintai-starter-tp4
Requires: joblib, numpy, pandas, scikit-learn
Required-by:
```

**Dernière ligne de `python -m pytest` à la fin du sprint 1 :**

```text
========================================= 27 passed, 1 warning in 12.90s ==========================================
```

**Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?**

Lors de mes premiers essais dans un autre dossier, les commandes n'ont pas fonctionné car l'environnement virtuel contenant le package n'était pas correctement utilisé.

La commande `pip show maintai` confirme ensuite que le package a été installé en mode éditable. Son emplacement source est :

```text
C:\Users\USER\Downloads\TP4\maintai-starter-tp4\maintai\__init__.py
```

Python trouve donc le code directement dans le dossier source du projet grâce à l'installation en mode éditable.

**Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?**

La modification du message dans `maintai/cli.py` n'a pas pu être vérifiée jusqu'à l'affichage final, car le programme s'arrête avant la prédiction à cause de l'absence du modèle `model.joblib`.

Cependant, l'installation en mode éditable permet à Python d'utiliser directement les fichiers source du projet. Les modifications du code sont donc prises en compte sans réinstaller le package, dès que la partie modifiée est exécutée.

## 3. Sprint 2 : construire et installer le wheel

**Sortie de `dir dist` après `python -m build` :**

```text
Répertoire : C:\Users\USER\Downloads\TP4\maintai-starter-tp4\dist

Mode   LastWriteTime       Length Name
----   -------------       ------ ----
-a---- 11/11/2026 5:34 PM  11623  maintai-0.2.0-py3-none-any.whl
-a---- 11/11/2026 5:34 PM  12208  maintai-0.2.0.tar.gz
```

**Contenu du wheel (`python -m zipfile -l dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?**

```text
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

Le wheel contient les fichiers Python du package `maintai`, ainsi que les informations nécessaires à son installation.

Le modèle, les tests et le dossier `ui/` ne sont pas présents. Cela s'explique par la configuration de setuptools :

```toml
[tool.setuptools.packages.find]
include = ["maintai*"]
```

Cette configuration sélectionne uniquement les packages dont le nom commence par `maintai`. Les autres dossiers situés à la racine du projet ne sont donc pas inclus dans le wheel.

**Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :**

| Étape | Ce qui s'affiche |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : C:\Users\USER\AppData\Local\Temp\essai\.venv\Lib\site-packages\models\model.joblib` |
| Avec `MAINTAI_MODELS_DIR` vers le dossier `models` | `Modèle introuvable : C:\Users\USER\Downloads\TP4\maintai-starter-tp4\models\model.joblib` |
| Après `pip install scikit-learn==1.8.0` | La version 1.8.0 est installée, mais le message `Modèle introuvable` apparaît encore. |

Le wheel a bien été installé dans un nouvel environnement virtuel avec la commande :

```powershell
python -m pip install "C:\Users\USER\Downloads\TP4\maintai-starter-tp4\dist\maintai-0.2.0-py3-none-any.whl"
```

La commande a affiché :

```text
Successfully installed cloudpickle-3.1.2 joblib-1.6.0 maintai-0.2.0 narwhals-2.28.0 numpy-2.4.6 pandas-3.1.1 python-dateutil-4.0.0 scikit-learn-1.9.1 scipy-1.17.1 threadpoolctl-3.8.0 tzdata-2026.6
```

Après installation de scikit-learn 1.8.0, la vérification a donné :

```text
(.venv) PS C:\Users\USER\AppData\Local\Temp\essai> python -c "import sklearn; print(sklearn.__version__)"
1.8.0
```

**D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?**

Cet avertissement apparaît lorsqu'un modèle sauvegardé avec une version de scikit-learn est chargé avec une version différente.

La ligne `"sklearn_version"` dans `models/model_info.json` permet normalement de connaître la version utilisée lors de l'entraînement du modèle et de la comparer avec celle installée au moment du chargement.

Dans mon cas, je n'ai pas pu observer cet avertissement, car le dossier `models` n'existe pas dans le projet. Les fichiers `model.joblib` et `model_info.json` sont donc absents. Le programme s'arrête avant le chargement du modèle.

## 4. Questions de compréhension

**1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?**

`requirements.txt` contient une liste de bibliothèques à installer pour préparer un environnement de travail. La section `dependencies` de `pyproject.toml` déclare les bibliothèques nécessaires au fonctionnement du package lorsqu'il est installé par un utilisateur.

**2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?**

Avec `pip install -e .`, le package est installé en mode éditable. Python utilise directement les fichiers source du projet et les modifications sont prises en compte sans réinstallation.

Avec l'installation du wheel, on installe une version construite du package. Si le code source est modifié après la création du wheel, ces modifications ne sont pas automatiquement intégrées dans le wheel déjà construit.

**3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?**

Un point d'entrée permet de créer une commande utilisable directement dans le terminal.

Dans notre projet, la ligne :

```toml
[project.scripts]
maintai-predict = "maintai.cli:main"
```

indique que la commande `maintai-predict` doit exécuter la fonction `main()` du fichier `maintai/cli.py`.

Sous Windows, pip crée le fichier `maintai-predict.exe` dans le dossier `Scripts` de l'environnement virtuel utilisé, par exemple :

```text
.venv\Scripts\maintai-predict.exe
```

## 5. Le rendu Git

- **Lien de la pull request :
- **Le tag `tp4` existe sur GitHub :** 
- **`git status` avant le commit :*

## 6. Ce qui reste flou

Le point qui reste à vérifier concerne le chargement du modèle dans un environnement neuf. Le dossier `models` et les fichiers `model.joblib` et `model_info.json` sont absents du projet. Je n'ai donc pas pu tester une prédiction complète ni observer l'avertissement `InconsistentVersionWarning`.


