"""Suivi reproductible des entraînements avec MLflow.

Chaque entraînement est enregistré sous forme de run dans l'expérience ``maintai`` par défaut.
Les paramètres, les métriques, l'empreinte MD5 des données et le modèle sont conservés
pour pouvoir comparer plusieurs versions du jeu de données et plusieurs réglages.

Les runs utilisent l'URI de tracking configuré dans l'environnement (``MLFLOW_TRACKING_URI``).
Sans configuration explicite, MLflow les stocke localement dans ``mlruns``. Ils peuvent être
consultés depuis l'interface graphique avec la commande ``mlflow ui``.
"""
import hashlib
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # coupe un message d'information de MLflow

import mlflow
import mlflow.sklearn

EXPERIMENT = "maintai"
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]  # nécessaire pour --model forest


def file_md5(path: Path) -> str:
    """Calcule l'empreinte MD5 d'un fichier de données.

    Cette empreinte correspond à celle utilisée par DVC pour identifier une version
    du fichier dans son fichier ``.dvc``.

    Args:
        path: Chemin du fichier dont on souhaite calculer l'empreinte.

    Returns:
        Empreinte MD5 représentée sur 32 caractères hexadécimaux.

    Raises:
        FileNotFoundError: Si ``path`` n'existe pas.
        IsADirectoryError: Si ``path`` désigne un dossier.
    """
    path = Path(path)
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


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
