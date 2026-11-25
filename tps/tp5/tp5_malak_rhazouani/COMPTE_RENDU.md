# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G1  ·  **Membres :** Malak rhazouani  ·  **Date :** 11/25/2026 15:24

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
================================= 5 failed, 27 passed, 2 warnings in 22.86s =================================
```

Quels tests échouent, et pourquoi ?

Les 5 tests qui échouent sont dans le fichier `test_tracking.py`. Ils concernent le suivi des entraînements avec MLflow : création d'un run, enregistrement des métriques, version des données, sauvegarde du modèle et modification des paramètres.

Ils échouent parce que la fonction `log_run()` n'enregistre pas correctement les entraînements dans MLflow. Aucun run n'est donc trouvé dans l'expérience `maintai`.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant `pip install -e .`, le package utilisait l'ancienne installation disponible dans l'environnement Python. Après cette commande, il pointe vers le dossier actuel du projet TP5. L'installation en mode editable permet de modifier le code source sans devoir réinstaller le package à chaque modification.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """
    Enregistre les informations d'un entraînement dans MLflow.

    Args:
        params (dict) : les paramètres utilisés pour entraîner le modèle.
        metrics (dict) : les résultats obtenus (accuracy, precision, recall...).
        model : le modèle Machine Learning entraîné.
        X_example : un exemple de données utilisé pour décrire les entrées du modèle.
        data_path (Path) : le chemin vers le fichier de données utilisé.

    Returns:
        str : l'identifiant unique du run MLflow.
    """

    # 1. Sélectionner l'expérience MLflow
    mlflow.set_experiment(EXPERIMENT)

    # 2. Démarrer un nouveau run
    with mlflow.start_run() as run:

        # 3. Enregistrer les paramètres du modèle
        mlflow.log_params(params)

        # 4. Calculer et enregistrer l'empreinte MD5 du fichier de données
        # Cela permet de connaître exactement la version des données utilisées.
        data_md5 = file_md5(data_path)
        mlflow.log_param("data_md5", data_md5)

        # 5. Enregistrer les métriques obtenues pendant l'entraînement
        mlflow.log_metrics(metrics)

        # 6. Enregistrer le modèle entraîné dans MLflow
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES
        )

        # 7. Récupérer l'identifiant du run
        run_id = run.info.run_id

    # 8. Retourner l'identifiant du run
    return run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
================================= 32 passed, 4 warnings in 62.01s (0:01:02) ==============================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` |0.75 | 0.622|0.904 |
| `python -m maintai.train --C 0.01` |0.691 |0.653 | 0.908|
| `python -m maintai.train --threshold 0.2` | 0.838|0.543 |0.543 |
| `python -m maintai.train --model forest` |0.728| 0.562| 0.886|
| (votre essai) | | | |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)
Je choisirais le run `python -m maintai.train --threshold 0.2`, car il possède le meilleur Recall (0.838). Dans le domaine de la maintenance, il est important de détecter le maximum de pannes pour éviter les problèmes sur les machines. Même si sa précision est plus faible, je préfère avoir quelques fausses alertes plutôt que de manquer une vraie panne.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le fichier `requirements.txt` permet de connaître les versions des bibliothèques utilisées pour entraîner le modèle, notamment Scikit-learn 
scikit-learn==1.8.0. Cela règle les problèmes de compatibilité rencontrés au TP4 lorsqu'on utilise un modèle entraîné avec une version différente de Scikit-learn. On peut ainsi retrouver le même environnement pour utiliser le modèle.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?
les runs sont enregistrés dans la base de données mlflow.db, située dans le dossier courant du projet.Non, normalement, on ne met pas mlflow.db ni les artefacts des runs dans Git.


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

ils sont identiques Cela signifie que le fichier utilisé pendant l'entraînement MLflow est exactement le même que celui suivi par DVC 

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Git suit les fichiers de référence (.dvc), tandis que DVC gère les données réelles. Cela permet de ne pas alourdir le dépôt Git.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:                                                                                                                                      
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | 4479074| 93fdeef2| 8 000|
| v2 |b2ec6a1| ae74b12f|10 000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

8 000 lignes

10 000 lignes
Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

Après avoir supprimé le fichier data/sensors.csv et le dossier .dvc/cache, j'ai exécuté dvc pull. La commande a échoué parce qu'aucun dépôt distant n'était configuré et que le cache local avait été supprimé. DVC ne pouvait donc pas récupérer le dataset. Cela montre l'importance de configurer un stockage distant pour sauvegarder et restaurer les données.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | 93fdeef2|0.908 | 0.728| 0.635|
| v2 |ae74b12f| 8 000	| 0.728|0.635 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

On ne peut pas dire que le modèle v2 est meilleur que le modèle v1, car les deux ont le même recall et la même precision. Il faut être prudent parce que les deux modèles ont été entraînés sur des données différentes. Les résultats peuvent donc varier à cause du dataset et pas seulement à cause du modèle. Pour faire une comparaison correcte, il faut garder les mêmes paramètres et utiliser le même jeu de test.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code.



DVC versionne les données.



MLflow suit les expériences et les performances des modèles.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   L'option --local permet de sauvegarder la configuration du stockage DVC uniquement sur l'ordinateur local, dans .dvc/config.local.

Cette configuration n'est pas partagée avec Git. Cela évite de partager des chemins locaux ou des informations personnelles propres à chaque ordinateur.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   …

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? oui / non

## 8. Ce qui reste flou

…





GRID SEARCH 

