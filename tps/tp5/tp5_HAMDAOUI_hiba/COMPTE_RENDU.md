# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G1  ·  **Membres :** Hamdaoui Hiba ·  **Date :** 25/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
=== 7 failed, 25 passed, 2 warnings in 27.87s ====
```

Quels tests échouent, et pourquoi ?

Les cinq tests de suivi MLflow échouent tant que `log_run` renvoie une chaîne vide et n'enregistre aucun run. Les deux échecs observés dans `tests/test_package.py` étaient dus à l'absence des métadonnées de la distribution `maintai` et de la commande `maintai-predict`. Après l'implémentation de `log_run` et l'installation en mode éditable, les 32 tests passent.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant l'installation dans le `.venv`, Python pouvait importer `maintai` depuis le dossier courant, mais aucune distribution installée ne fournissait ses métadonnées. Après l'installation, la distribution est enregistrée dans le `.venv` et l'import pointe vers les sources du TP5.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement et renvoie l'identifiant du run MLflow.

    `params` contient les réglages de l'entraînement et `metrics` les scores
    numériques d'évaluation. Le fichier `data_path` fournit l'empreinte
    `data_md5`, qui permet de retrouver la version des données utilisée.

    `model` est le pipeline scikit-learn déjà entraîné. `X_example` contient
    quelques lignes représentatives pour que MLflow puisse inférer la signature
    du modèle. Le modèle peut ensuite être rechargé via `runs:/<run_id>/model`.
    """
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
    return run.info.run_id

```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
==== 32 passed, 3 warnings in 59.71s =====
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.75 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |


Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je retiens la régression logistique avec `C=1.0` et un seuil d'alerte de `0.2`. Son rappel de **83,8 %**, le plus élevé des quatre essais, signifie qu'elle détecte environ 84 pannes sur 100. Avec le seuil par défaut de `0.3`, elle en détecte 75 sur 100. La précision baisse de 62,2 % à 54,3 %, ce qui signifie qu'une plus grande part des alertes est fausse. Ce compromis est cohérent avec le coût plus élevé d'une panne manquée.

Identifiant du run retenu : `2b8d67c7ac014a57939e560c62d0ed31`  
Empreinte des données (`data_md5`) : `73e0b7cb3c6f795c70c3ddf970b99c15`

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le fichier `requirements.txt` de l'artefact du run retenu indique `scikit-learn==1.8.0`. Au TP4, le modèle était livré séparément du paquet Python. Une autre machine pouvait disposer d'une version différente de scikit-learn, avec un risque d'incompatibilité au chargement du modèle. Les dépendances enregistrées avec le modèle permettent de recréer un environnement compatible.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

À la racine du projet, la base SQLite `mlflow.db` contient les métadonnées des runs, dont les paramètres, les métriques et les identifiants. Les modèles et leurs fichiers de dépendances sont dans `mlruns/1/models/`. Le fichier `.gitignore` exclut `mlflow.db` et `mlruns/`, car ce sont des résultats générés localement qui évoluent à chaque entraînement et dont les artefacts peuvent occuper beaucoup de place.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv

```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Pour la v1, le champ `md5` du descripteur DVC et le paramètre `data_md5` du run MLflow `bfa974d666e846a9b61ca7d70fbded5b` valent tous deux `73e0b7cb3c6f795c70c3ddf970b99c15`.

Les deux outils identifient donc le même contenu du CSV.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

data/sensors.csv contient les données. DVC les conserve dans son cache et peut les envoyer vers un stockage distant. Cela évite d’alourdir l’historique Git à chaque nouvelle version du CSV.

data/sensors.csv.dvc est un petit fichier que Git versionne avec le code. Il contient le chemin du CSV, sa taille et son empreinte MD5. Cette empreinte permet à DVC de retrouver la version exacte des données associée à chaque commit.

   

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:                                                                      
        changed outs:
                modified:           data\sensors.csv

```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | Aucun commit dans le dépôt local | `73e0b7cb` | 5 000 |
| v2 | Aucun commit dans le dépôt local | `93fdeef2` | 8 000 |

Le comptage exclut l'en-tête du CSV.

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Le dépôt local ne contient aucun commit. J'ai vérifié la restauration avec les descripteurs DVC des deux versions dans un dossier temporaire. La v1 contient **5 000 lignes de données**. Après restauration de la v2 avec `dvc checkout`, le CSV contient **8 000 lignes de données**.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

Dans un dossier temporaire sans CSV ni cache projet, `dvc pull` a récupéré la v2 depuis le stockage DVC configuré, rempli le cache et recréé le CSV de 8 000 lignes.

```text
A       data\sensors.csv
1 file fetched and 1 file added
```

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | `73e0b7cb` | 4 000 | 0.838 | 0.543 |
| v2 | `93fdeef2` | 6 400 | 0.824 | 0.567 |

Les deux runs utilisent une régression logistique avec `C=1.0` et un seuil de `0.2`. Le run v1 est `2b8d67c7ac014a57939e560c62d0ed31` et le run v2 est `0b1f9dd56627449c913f0fbcfd78b151`.

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

La v2 obtient une précision plus élevée (56,7 % contre 54,3 %) et un rappel plus faible (82,4 % contre 83,8 %). Les scores proviennent de deux jeux de test différents, de 1 000 et 1 600 exemples. Une comparaison sur un même jeu de test indépendant permettrait de déterminer si ces écarts se retrouvent dans les mêmes conditions.

## 5. Décision : l'ADR 004

Le choix du modèle, du seuil et du run est documenté dans [l'ADR 004](docs/adr/004-choix-du-modele.md).

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code, la configuration et les descripteurs `.dvc`. DVC conserve les versions des fichiers de données. MLflow enregistre les paramètres, les métriques et les modèles de chaque entraînement.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   L'option `--local` place le chemin propre à la machine dans `.dvc/config.local`. Pour partager les données, le groupe a besoin d'un stockage DVC commun et des droits d'accès associés. Les descripteurs circulent via Git, et les données via `dvc push` et `dvc pull`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code de prédiction est livré dans le paquet Python, le modèle entraîné dans l'artefact MLflow et les versions des dépendances dans le fichier `requirements.txt` de cet artefact.



## 8. Ce qui reste flou

Il reste à déterminer si l'écart de rappel entre la v1 et la v2 se retrouve sur un même jeu de test indépendant.

# grid Search

Le script [`maintai/grid_search.py`](maintai/grid_search.py) exécute la grille et enregistre chaque combinaison dans l'expérience MLflow `maintai-grid-search`. La commande affiche uniquement les six premiers essais du classement et les scores du gagnant sur le test réservé.

```powershell
.\.venv\Scripts\python.exe -m maintai.grid_search
```

La grille combine cinq valeurs de `C` pour la régression logistique avec cinq seuils d'alerte (25 essais), puis applique les mêmes seuils à une forêt de 200 arbres (5 essais). Un `C` plus faible renforce la régularisation de la régression. Le seuil détermine la probabilité minimale à partir de laquelle la prédiction déclenche une alerte.

```python
C_VALUES = (0.01, 0.1, 1.0, 10.0, 100.0)
THRESHOLDS = (0.20, 0.25, 0.30, 0.35, 0.40)
configurations = [("logreg", c) for c in C_VALUES] + [("forest", None)]
```

Le CSV v2 est découpé de façon stratifiée en 4 800 lignes pour l'entraînement, 1 600 pour la validation et 1 600 pour le test, avec la graine `42`. La validation classe les essais par nombre croissant de faux négatifs (FN), puis de faux positifs (FP) en cas d'égalité. Une panne manquée correspond à un FN. Une fausse alerte correspond à un FP.

La marge de décision est la différence entre la probabilité estimée de panne et le seuil. Une marge proche de zéro indique une prédiction proche de la frontière d'alerte. La colonne **Marge abs.** donne la moyenne de la valeur absolue des marges sur la validation.

```python
margins = probabilities - threshold
_, fp, fn, _ = confusion_matrix(y_val, margins >= 0, labels=[0, 1]).ravel()
mean_abs_margin = float(abs(margins).mean())
results.sort(key=lambda row: (row[1]["false_negatives"], row[1]["false_positives"]))
top_six = results[:6]
```

| Rang | Modèle | `C` | Arbres | Seuil | Rappel | Précision | Accuracy | FP | FN | Marge abs. |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Régression logistique | 0,1 | — | 0,20 | 0,853 | 0,534 | 0,886 | 152 | 30 | 0,202 |
| 2 | Régression logistique | 0,01 | — | 0,20 | 0,853 | 0,527 | 0,884 | 156 | 30 | 0,166 |
| 3 | Régression logistique | 1,0 | — | 0,20 | 0,848 | 0,536 | 0,887 | 150 | 31 | 0,209 |
| 4 | Régression logistique | 10,0 | — | 0,20 | 0,843 | 0,536 | 0,887 | 149 | 32 | 0,210 |
| 5 | Régression logistique | 100,0 | — | 0,20 | 0,843 | 0,536 | 0,887 | 149 | 32 | 0,210 |
| 6 | Forêt aléatoire | — | 200 | 0,20 | 0,833 | 0,511 | 0,877 | 163 | 34 | 0,207 |

Les deux premiers essais manquent 30 pannes chacun. Le réglage `C=0.1` arrive premier parce qu'il produit quatre fausses alertes de moins. Après réentraînement sur les 6 400 lignes de développement, il obtient **82,9 % de rappel**, **55,9 % de précision** et **89,4 % d'accuracy** sur le test réservé. Le choix et sa justification figurent dans [`adr.md`](adr.md).


