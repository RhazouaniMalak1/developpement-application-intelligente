"""Suivi des entraînements dans l'expérience MLflow « maintai ».

Avec la configuration locale par défaut du TP, MLflow conserve les métadonnées
dans `mlflow.db` et les artefacts dans `mlruns/`. Depuis la racine du projet,
`mlflow ui` permet de consulter et de comparer les entraînements.
La variable `MLFLOW_TRACKING_URI` permet de choisir un autre stockage.
"""
import hashlib
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # coupe un message d'information de MLflow

import mlflow
import mlflow.sklearn

EXPERIMENT = "maintai"
# skops doit autoriser ce type interne pour recharger une forêt aléatoire.
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]


def file_md5(path: Path) -> str:
    """Calcule le MD5 du fichier pour le comparer à celui enregistré par DVC.

    La lecture par blocs de 1 Mio évite de charger tout le fichier en mémoire.
    """
    digest = hashlib.md5()
    with open(path, "rb") as data_file:
        for block in iter(lambda: data_file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


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
