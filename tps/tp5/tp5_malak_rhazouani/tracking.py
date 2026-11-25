"""Suivi des entraînements avec MLflow : chaque entraînement devient un « run » qu'on peut comparer.

Les runs sont enregistrés dans mlflow.db (dossier courant) ; on les regarde avec : mlflow ui
"""
import hashlib
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # coupe un message d'information de MLflow

import mlflow
import mlflow.sklearn

EXPERIMENT = "maintai"
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]  # nécessaire pour --model forest


def file_md5(path: Path) -> str:
    """Empreinte du fichier de données : la même que celle que DVC écrit dans le fichier .dvc."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()



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


def log_grid_search_run(params: dict, metrics: dict, data_path: Path) -> str:
    """Enregistre un candidat de recherche sans stocker son modèle intermédiaire."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        run_id = run.info.run_id
    return run_id


def log_search_model(run_id: str, model, X_example, metrics: dict) -> None:
    """Ajoute le modèle final et ses métriques de test au run du candidat retenu."""
    with mlflow.start_run(run_id=run_id):
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="final_model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
