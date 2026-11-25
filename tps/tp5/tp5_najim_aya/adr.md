# ADR — Modèle MaintAI retenu après recherche sur grille

## Contexte

MaintAI estime la probabilité d'une panne à partir de mesures de capteurs. Une panne manquée
est plus coûteuse qu'une fausse alerte ; le nombre de faux négatifs doit donc guider le choix,
tout en gardant visibles les faux positifs.

La recherche a été effectuée sur le CSV configuré (`data/sensors.csv`), version v2 de 8 000
relevés, empreinte MD5 `93fdeef2cac1893c4f720c16457eea75`. Le jeu a été séparé de manière
stratifiée avec la graine 42 : 4 800 observations pour l'entraînement, 1 600 pour la validation
et 1 600 pour un test réservé. Trente combinaisons ont été suivies dans l'expérience MLflow
`maintai-grid-search`.

## Décision

Retenir la **régression logistique** avec le prétraitement `StandardScaler`, régularisation
`C=0.01`, `max_iter=1000` et seuil d'alerte `0.20`. L'alerte est positive lorsque la
probabilité estimée de panne est supérieure ou égale à ce seuil.

Le classement minimise les faux négatifs, puis les faux positifs. Cette configuration produit
le plus petit nombre de pannes manquées sur la validation : **35 FN**, contre 37 pour la
deuxième configuration (forêt aléatoire à 200 arbres, seuil 0.20). Son compromis est de
générer **150 FP** sur la validation.

| Jeu | Rappel | Précision | Accuracy | FP | FN | Marge absolue moyenne |
|---|---:|---:|---:|---:|---:|---:|
| Validation | 0.829 | 0.531 | 0.884 | 150 | 35 | 0.167214 |
| Test réservé | 0.809 | 0.554 | 0.892 | 133 | 39 | 0.172178 |

Le test réservé confirme un rappel de 0.809 : le choix détecte une large majorité des pannes,
mais conserve un compromis réel avec les fausses alertes (133 FP). Le gagnant est enregistré
dans MLflow sous l'identifiant `368ef39467c94206b8712037a5027994`, avec l'empreinte des données
ci-dessus. Le modèle réentraîné sur entraînement et validation est également joint à ce run ;
les scores du test y sont enregistrés sans créer de run supplémentaire.

## Conséquences

- Le seuil bas favorise le rappel, mais augmente les interventions déclenchées à tort.
- Les performances sont liées à la version des données ; toute nouvelle version doit être
  réévaluée au lieu de supposer que ces scores resteront identiques.
- Le jeu de test reste réservé à l'évaluation finale et ne sert pas au classement des
  hyperparamètres.
- Pour reproduire la sélection, le réentraînement final et son évaluation :

  ```powershell
  .\.venv\Scripts\python.exe -m maintai.grid_search
  ```

- Pour relancer uniquement l'entraînement habituel avec les hyperparamètres retenus :

  ```powershell
  .\.venv\Scripts\python.exe -m maintai.train --model logreg --C 0.01 --threshold 0.20
  ```
