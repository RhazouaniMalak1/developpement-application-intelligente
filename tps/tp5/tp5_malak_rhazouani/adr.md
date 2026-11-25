# ADR — Choix du modèle après grid search

**Date :** 25/11/2026  
**Statut :** accepté  
**Données :** `data/sensors.csv` — `data_md5` : `ae74b12fbac80f976732f9290c532a0d`

## Contexte

MaintAI prédit les pannes de machines à partir de la température, des vibrations,
de la charge et du temps de fonctionnement. Une panne manquée étant plus coûteuse
qu'une fausse alerte, le recall est le critère prioritaire.

## Recherche effectuée

La commande `python -m maintai.train --grid-search` évalue 30 configurations.
Les 8 000 exemples d'entraînement sont séparés en un sous-ensemble d'ajustement
et un sous-ensemble de validation (25 %), avec une graine fixe (`42`). Le jeu de
test de 2 000 exemples reste indépendant de cette sélection.

La grille compare :

- **Régression logistique** : `C` parmi `0.01`, `0.1`, `1`, `10`, `100` et seuil
  parmi `0.2`, `0.3`, `0.4`.
- **Random Forest** : profondeur maximale parmi illimitée, `5`, `10`, `15`, `20`,
  avec 200 arbres, et les mêmes trois seuils.

Le meilleur recall de validation est sélectionné; les égalités sont départagées
par la précision, puis l'accuracy. Seules les six meilleures configurations sont
affichées dans le terminal. Les 30 candidats sont enregistrés dans MLflow; le
modèle retenu est ensuite réentraîné sur l'ensemble d'entraînement. Le run retenu
contient le modèle final dans l'artefact `final_model`.

## Décision

Le modèle retenu est une **régression logistique** précédée d'une standardisation
des variables (`StandardScaler`).

| Hyperparamètre | Valeur choisie | Description |
|---|---:|---|
| `C` | `0.1` | Inverse de la force de régularisation; cette valeur régularise davantage que `C=1`. |
| Seuil d'alerte | `0.2` | Une panne est prédite si sa probabilité estimée atteint au moins 20 %. |
| `max_iter` | `1000` | Nombre maximal d'itérations du solveur de la régression logistique. |

Configuration retenue dans le code :

```python
model = build_model(kind="logreg", C=0.1)
threshold = 0.2
```

Le seuil de `0.2` privilégie la détection des pannes, au prix d'une précision plus
faible. Les performances mesurées sur le jeu de test sont :

| Jeu de test | Accuracy | Recall | Précision |
|---|---:|---:|---:|
| Modèle retenu | `0.887` | `0.792` | `0.553` |
| Baseline (classe majoritaire) | `0.868` | `0.000` | — |

## Traçabilité

- **Run MLflow retenu :** `c634a1820979426291973b5e9a180af7`
- **Recall de validation :** `0.845` (précision `0.591`, accuracy `0.902`)
- **Version des données :** `ae74b12fbac80f976732f9290c532a0d`

## Conséquences

Le seuil bas détecte davantage de pannes, mais augmente les fausses alertes. Il
faudra suivre le compromis recall/précision sur de nouvelles données. Toute
comparaison future devra conserver un jeu de test indépendant et identifier la
version du dataset utilisée.


# ADR 004 : Choix du modèle de prédiction

Date : 25/11/2026 · Auteurs : MALAK RHAZOUANI

> Décision historique basée sur les runs avant la grid search. Elle est remplacée
> par la décision documentée dans [`adr.md`](../../adr.md).

## Contexte

Le projet consiste à développer un modèle capable de prédire les pannes des équipements industriels. Il faut choisir un modèle avec de bonnes performances, notamment en termes de recall et de precision, tout en gardant une trace des expériences avec MLflow.

## Options étudiées

1. **Logistic Regression (logreg)** : modèle simple et rapide à entraîner. Il donne de bons résultats, mais ses performances dépendent du seuil de décision choisi.
2. **Random Forest (forest)** : permet de détecter les relations plus complexes dans les données, mais ses résultats peuvent être différents de ceux de la régression logistique.

## Décision

Le modèle retenu est **Logistic Regression (logreg)** avec un seuil de décision de **0.3** et un paramètre `C = 1.0`.

Ce choix correspond au run v2 enregistré dans MLflow.

- Identifiant du run : `8886db5296b04322a1ecfde44128e2fb`
- Version des données : v2
- `data_md5` : `ae74b12fbac80f976732f9290c532a0d`
- Nombre de données d'entraînement : 8 000
- Accuracy : 0.908
- Recall : 0.728
- Precision : 0.635

## Conséquences

Ce choix permet de conserver un modèle identifié et reproductible grâce à MLflow. Il facilite le suivi des performances et la comparaison avec les prochaines expériences.

Il faudra surveiller particulièrement le recall, car il est important de détecter les pannes et de limiter les pannes non détectées. Les performances devront également être vérifiées avec de nouvelles données.