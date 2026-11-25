# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** 1 ·  **Membres :** Najim Aya  ·  **Date :** 25/11/2026 **l'heure:** 18:15
> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Première exécution de `python -m pytest` (avec l'interpréteur Python global) :

```
 7 failed, 25 passed, 2 warnings in 26.00s
```

Quels tests échouent, et pourquoi ?
Lors de cette première exécution, 7 tests échouaient : les 2 tests de `test_package.py` ne
trouvaient pas les métadonnées et la commande du package installé. Les 5 tests de
`test_tracking.py` ne retrouvaient aucun run MLflow (MLflow signalait qu'il ne pouvait pas
récupérer l'expérience `maintai`). La commande `python` utilisait alors l'interpréteur Python
global et non celui de `.venv`. En relançant les tests de tracking avec `.venv`, ils passaient :
ce n'était donc pas un échec persistant de `log_run`.

Après installation éditable dans `.venv` et exécution avec son interpréteur, la suite du sprint 1
passait (32 tests). La suite actuelle comprend deux tests supplémentaires pour la grille.
Après l'ajout de la grille, la dernière exécution complète a donné `34 passed, 4 warnings` ;
les deux tests de grille ont également repassé séparément après leur dernière modification.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?
Avant : la distribution n'était pas installée dans l'environnement virtuel. Depuis la racine du
projet, Python pouvait importer le code source local, mais les métadonnées d'installation et
l'entry point `maintai-predict` n'étaient pas enregistrés.

Après `pip install -e .` avec l'interpréteur de `.venv`, la distribution est installée en mode
éditable et pointe vers le code source `maintai/` du projet.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(
    params: dict[str, Any],
    metrics: dict[str, float],
    model: Any,
    X_example: Any,
    data_path: Path,
    experiment_name: str = EXPERIMENT,
) -> str:
    """Enregistre un entraînement complet dans une nouvelle run MLflow.

    La run contient les paramètres d'entraînement, les métriques calculées, une
    empreinte de la version des données et le modèle entraîné avec un exemple
    d'entrée. L'utilisation d'un contexte MLflow garantit que la run est correctement
    fermée même en cas d'erreur.

    Args:
        params: Paramètres du modèle ou de l'entraînement à enregistrer.
        metrics: Mesures numériques produites lors de l'évaluation.
        model: Modèle scikit-learn entraîné à sauvegarder.
        X_example: Petit échantillon d'entrées servant d'exemple au modèle MLflow.
        data_path: Chemin du jeu de données utilisé pour cet entraînement.
        experiment_name: Nom de l'expérience MLflow à utiliser.

    Returns:
        Identifiant unique de la run MLflow créée.

    Raises:
        FileNotFoundError: Si le fichier de données n'existe pas.
        mlflow.exceptions.MlflowException: En cas d'erreur de communication avec MLflow.
    """
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(Path(data_path)))
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
===================== 32 passed, 4 warnings in 47.56s ======================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` |0.75|0.622|0.904|
| `python -m maintai.train --C 0.01` |0.691|0.653|0.908|
| `python -m maintai.train --threshold 0.2` |0.838|0.543|0.882|
| `python -m maintai.train --model forest` |0.728|0.562|0.886|

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisis le run python -m maintai.train --threshold 0.2, car c'est celui qui a le meilleur recall (0.838). Comme une panne manquée coûte plus cher qu'une fausse alerte, il vaut mieux maximiser le recall pour détecter le maximum de pannes possibles, même si la précision baisse un peu (0.543).

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Version indiquée dans `requirements.txt` du modèle MLflow : `scikit-learn==1.8.0`.

Cela documente la version de scikit-learn utilisée pour sérialiser le modèle et réduit les
risques d'incompatibilité au chargement dans un autre environnement.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans la configuration actuelle, MLflow stocke les paramètres et métriques dans `mlflow.db` et
les artefacts des runs (dont les modèles) dans `mlruns/`.

Ces fichiers ne vont pas dans Git : ils sont générés localement et les modèles peuvent être
lourds. Les règles `.gitignore` les excluent du dépôt.

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

Dans cet extrait historique de la v1, l'empreinte `73e0b7cb3c6f795c70c3ddf970b99c15`
correspond au paramètre `data_md5` du run MLflow v1. Après l'ajout de la v2, le fichier `.dvc`
actuel porte l'empreinte `93fdeef2cac1893c4f720c16457eea75`, identique à celle du run MLflow v2.
Le hash relie ainsi chaque run à la version exacte de son CSV.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

data/sensors.csv est ignoré par Git car c'est un fichier de données lourd qui alourdirait le dépôt.

data/sensors.csv.dvc va dans Git car c'est un tout petit fichier texte contenant seulement l'empreinte (md5) des données, ce qui permet de versionner la référence du dataset sans stocker le fichier lui-même.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | Non disponible : aucun commit Git dans le dépôt | 73e0b7cb | 5000 |
| v2 | Non disponible : aucun commit Git dans le dépôt | 93fdeef2 | 8000 |

Le jeu de données généré contient bien 8 000 relevés et son empreinte MD5 est `93fdeef2cac1893c4f720c16457eea75`. La version précédente est toujours dans le cache DVC : son empreinte est `73e0b7cb3c6f795c70c3ddf970b99c15` et elle contient 5 000 relevés. Le dépôt n'ayant encore aucun commit Git, les commandes `git checkout <commit> -- data/sensors.csv.dvc` et `dvc checkout` ne peuvent pas être exécutées avec des identifiants de commit. Il faut d'abord enregistrer les versions successives du fichier `.dvc` dans Git.

Le dépôt DVC local (`stockage`) contient actuellement l'objet de la v2. Si `data/sensors.csv` et le cache local sont absents, `dvc pull` peut récupérer cette version depuis le dépôt distant et restaurer le fichier (8 000 relevés), car l'objet correspondant y est présent. La commande `dvc status --cloud` confirme : `Cache and remote 'stockage' are in sync.`

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision | accuracy |
|---|---|---:|---:|---:|---:|
| v1 (`logreg`, C=1, seuil=0.2) | 73e0b7cb | 4000 | 0.838 | 0.543 | 0.882 |
| v2 (`logreg`, C=1, seuil=0.2) | 93fdeef2 | 6400 | 0.824 | 0.567 | 0.897 |

Les deux runs utilisent la régression logistique avec `C=1` et un seuil de `0.2`, mais la v2
donne ici un rappel légèrement inférieur (0.824 contre 0.838) et une précision et une accuracy
supérieures. On ne peut pas conclure que la v2 est globalement « meilleure » : les jeux de
données n'ont ni la même taille ni les mêmes observations, et leurs partitions de test ne
contiennent pas les mêmes relevés. Il faut interpréter ces scores selon le coût des faux négatifs
et, pour une comparaison stricte, évaluer sur un jeu de test commun et indépendant.

Run MLflow v1 : `e96f38aebb4646ce86617f8717ae704a` ; run v2 : `f068330f92594d588ec7c542487f4942`.

## 5. Décision : l'ADR 004

Pour la première comparaison MLflow sur la v1, le choix est la régression logistique (`C=1`,
seuil `0.2`), run `e96f38aebb4646ce86617f8717ae704a`, `data_md5` =
`73e0b7cb3c6f795c70c3ddf970b99c15`. La décision de la recherche sur grille, menée ensuite sur
la v2, est documentée séparément dans `adr.md` : régression logistique, `C=0.01`, seuil `0.20`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code et les petits fichiers de description, notamment le pointeur `.dvc`.
   DVC conserve les versions des données volumineuses dans son cache/remote et versionne leur
   empreinte et leur chemin via le fichier `.dvc`. MLflow garde les expériences : paramètres,
   métriques, empreinte des données et artefacts de modèle.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   `--local` place l'URL du stockage dans `.dvc/config.local`, un fichier local non partagé par
   Git, afin de ne pas imposer un chemin propre à une machine. Pour partager les données, il faut
   configurer un remote accessible à tous (par exemple stockage objet ou serveur partagé) et
   fournir les accès de manière sécurisée.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code et le prétraitement sont dans le package `maintai/` (et peuvent être distribués en
   wheel) ; le modèle sérialisé, qui inclut le scaler, est dans `models/model.joblib` ; les
   dépendances et le contrat du modèle sont décrits dans `requirements.txt` et
   `models/model_info.json`. La provenance des données est référencée séparément par DVC.

## 7. Le rendu Git

- Lien de la pull request : non disponible dans ce workspace (aucun remote Git configuré et aucun commit).
- Le tag `tp5` existe sur GitHub : non vérifiable ici ; aucun tag local ni remote Git configuré.
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` et `.dvc/cache` sont ignorés par les règles Git et n'apparaissent pas comme fichiers à ajouter. Attention : le dossier `%USERPROFILE%/` du remote DVC local apparaît, lui, comme non suivi ; ne pas l'ajouter au dépôt.

## 8. Ce qui reste flou

Le remote DVC est configuré localement (`--local`) et n'est donc pas partagé avec le groupe.
De plus, son URL se résout actuellement vers un dossier littéralement nommé `%USERPROFILE%` dans
le projet ; ce dossier apparaît comme non suivi dans `git status`. Il ne faut pas le committer.
Il faudra corriger ce chemin local et définir un stockage distant commun avec des accès
sécurisés avant de récupérer les données sur une autre machine.

## Recherche sur grille avec 30 essais

Lancer la recherche depuis PowerShell, à la racine du projet :

```powershell
.\.venv\Scripts\python.exe -m maintai.grid_search
```

La grille explore cinq valeurs de régularisation `C` pour la régression logistique, chacune
combinée à cinq seuils : `5 × 5 = 25` essais. Elle ajoute une forêt aléatoire de 200 arbres
évaluée aux cinq mêmes seuils : `1 × 5 = 5` essais, soit **30 runs MLflow** dans
`maintai-grid-search`. Chaque configuration de modèle est entraînée une seule fois ; les cinq
seuils sont appliqués aux mêmes probabilités de validation.

```python
LOGREG_C_VALUES = (0.01, 0.1, 1.0, 10.0, 100.0)
THRESHOLDS = (0.20, 0.25, 0.30, 0.35, 0.40)
EXPECTED_RUNS = len(LOGREG_C_VALUES) * len(THRESHOLDS) + len(THRESHOLDS)
```

`C` contrôle la régularisation de la régression logistique : une valeur plus petite renforce
la régularisation. Le seuil transforme la probabilité estimée en alerte : le modèle prédit une
panne lorsque la probabilité atteint ou dépasse le seuil. Un seuil plus bas tend à détecter plus
de pannes, mais peut aussi générer davantage de fausses alertes.

Le découpage est stratifié et reproductible avec la graine 42 : **60 % entraînement (4 800
relevés), 20 % validation (1 600) et 20 % test réservé (1 600)**. La validation sert à comparer
les 30 combinaisons ; le test n'est utilisé qu'après le choix du gagnant. Le classement donne la
priorité au plus petit nombre de faux négatifs, puis au plus petit nombre de faux positifs.

La marge signée de chaque observation est la probabilité de panne moins le seuil. Le tableau
affiche la moyenne des valeurs absolues :

```python
margins = probabilities - threshold
mean_absolute_margin = float(np.abs(margins).mean())
```

```python
ranked_runs = sorted(all_runs, key=lambda item: (item["fn"], item["fp"]))
```

Les six premières combinaisons mesurées sur la v2 du jeu de données :

| Rang | Modèle | C | Arbres | Seuil | Rappel | Précision | Accuracy | FP | FN | Marge abs. moyenne |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Régression logistique | 0.01 | — | 0.20 | 0.829 | 0.531 | 0.884 | 150 | 35 | 0.167214 |
| 2 | Forêt aléatoire | — | 200 | 0.20 | 0.820 | 0.519 | 0.879 | 156 | 37 | 0.211600 |
| 3 | Régression logistique | 1.0 | — | 0.20 | 0.805 | 0.543 | 0.888 | 139 | 40 | 0.210183 |
| 4 | Régression logistique | 10.0 | — | 0.20 | 0.805 | 0.543 | 0.888 | 139 | 40 | 0.211013 |
| 5 | Régression logistique | 100.0 | — | 0.20 | 0.805 | 0.543 | 0.888 | 139 | 40 | 0.211098 |
| 6 | Régression logistique | 0.1 | — | 0.20 | 0.805 | 0.537 | 0.886 | 142 | 40 | 0.202945 |

**Gagnant :** régression logistique (`C=0.01`, seuil `0.20`). Elle minimise les pannes manquées
sur la validation (35 FN), devant la forêt (37 FN). Ce choix privilégie la détection des pannes
au prix de 150 fausses alertes. Après réentraînement sur les 6 400 relevés d'entraînement et de
validation réunis, le résultat sur le test réservé est : **rappel 0.809, précision 0.554,
accuracy 0.892, FP 133, FN 39**, marge absolue moyenne `0.172178`. Ces métriques de test sont
ajoutées au run gagnant ; elles ne génèrent pas de 31e run.

Run MLflow gagnant : `368ef39467c94206b8712037a5027994`. Empreinte du CSV utilisé :
`93fdeef2cac1893c4f720c16457eea75`.
