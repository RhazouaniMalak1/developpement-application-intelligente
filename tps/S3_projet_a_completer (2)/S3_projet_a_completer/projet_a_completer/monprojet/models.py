"""Les modèles à comparer.

À vous d'écrire candidates(). Les tests de tests/test_models.py disent ce qui est attendu.
"""
from monprojet import config  # noqa: F401  (config.TASK, config.SEED)

from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor


def candidates() -> dict:
    """Renvoie un dictionnaire {nom: modèle scikit-learn non entraîné}.

    Attendu :
    - le PREMIER modèle est la baseline : le modèle le plus simple possible
      (DummyClassifier pour une classification, DummyRegressor pour une régression) ;
    - au moins trois vrais modèles ensuite, adaptés à config.TASK ;
    - random_state=config.SEED pour les modèles qui ont du hasard.

    Pistes : sklearn.dummy, sklearn.linear_model, sklearn.ensemble, sklearn.neighbors, sklearn.tree.
    """
    models = {}

    if config.TASK == "classification":

        models["baseline"] = DummyClassifier(strategy="most_frequent")
        
        models["logistic_regression"] = LogisticRegression(random_state=config.SEED)
        models["decision_tree"] = DecisionTreeClassifier(random_state=config.SEED)
        models["random_forest"] = RandomForestClassifier(random_state=config.SEED)
        models["knn"] = KNeighborsClassifier()

    elif config.TASK == "regression":
       
        models["baseline"] = DummyRegressor(strategy="mean")
        
        models["ridge"] = Ridge(random_state=config.SEED)
        models["decision_tree"] = DecisionTreeRegressor(random_state=config.SEED)
        models["random_forest"] = RandomForestRegressor(random_state=config.SEED)
        models["knn"] = KNeighborsRegressor()

    else:
        raise ValueError(f"Tâche inconnue ou non supportée : {config.TASK}")

    return models