# TP0 : maintAI

# Sélection du modèle

Date : 27/10/2026 · Membre : Imane Mekkaoui

## Contexte
Le but du projet est de déterminer, à partir des mesures d’une machine, si une panne risque de se produire. Le rappel est la mesure la plus importante, puisqu’il faut détecter autant de pannes que possible.

## Données et méthode de découpage
L’analyse s’appuie sur le fichier `data/exemple_pannes.csv`, qui comporte 5 000 observations et 5 colonnes. Les quatre variables numériques — `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours` — sont utilisées pour prédire la variable `failure`. Les données sont séparées aléatoirement : 80 % pour l’entraînement et 20 % pour le test, soit 1 000 observations dans le jeu de test.

## Performances sur le jeu de test

| Modèle | Métrique principale : rappel | Autres métriques |
|---|---:|---|
| Baseline | 0,000 | Exactitude : 0,824 ; précision : 0,000 ; F1 : 0,000 |
| Régression logistique | 0,574 | Exactitude : 0,889 ; précision : 0,737 ; F1 : 0,645 |
| Arbre de décision | 0,597 | Exactitude : 0,839 ; précision : 0,538 ; F1 : 0,566 |
| Forêt aléatoire | 0,545 | Exactitude : 0,873 ; précision : 0,671 ; F1 : 0,602 |
| K plus proches voisins (KNN) | 0,540 | Exactitude : 0,878 ; précision : 0,699 ; F1 : 0,609 |

## Modèle retenu
Je retiens l’arbre de décision, qui présente le rappel le plus élevé, à 0,597. Il dépasse ainsi la baseline de 0,597. Le critère fixé — obtenir sur le jeu de test un rappel supérieur à celui de la baseline — est donc respecté. Le projet ne précise pas d’autre seuil numérique.

## Limites de l’analyse
Les résultats reposent sur un unique découpage aléatoire, et le fichier fourni ne renseigne pas sur la provenance des données. Les performances observées ne permettent donc pas d’assurer que le modèle donnera des résultats comparables sur d’autres machines ou sur de nouvelles données.

# TP0 : CantineAI

**Nom :** Mekkaoui Imane
**Groupe :** G

## Problématique
L’objectif est d’estimer, pour une date donnée, le nombre de repas à préparer afin de limiter à la fois le gaspillage et le risque de manquer de repas.

## Performances sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Ridge | 22,623 | 28,545 | 0,880 |
| Random Forest | 31,845 | 41,540 | 0,746 |
| KNN | 36,212 | 46,037 | 0,688 |
| Decision Tree | 46,000 | 59,710 | 0,475 |
| Baseline | 70,271 | 88,416 | -0,151 |

## Modèle choisi et justification
Le modèle **Ridge** est mon choix, puisqu’il obtient les meilleurs résultats. Son MAE de 22,623 repas signifie que ses estimations s’éloignent en moyenne d’environ 23 repas de la valeur réelle. Avec un R² de 0,880, il rend compte d’une grande partie des variations du nombre de repas servis.

## Le critère (rappel ≥ 0,75) est-il respecté ?
Les résultats disponibles ne permettent pas de vérifier ce critère directement : le rappel s’applique à un problème de classification, alors qu’ici le modèle prédit un nombre de repas, ce qui correspond à une tâche de régression. Il reste à déterminer si ce seuil de rappel se rapporte à une autre partie du TP ou si une tâche de classification est aussi demandée.

## Points à clarifier
Il faut encore déterminer si une erreur moyenne d’environ 23 repas est acceptable pour la cantine, en tenant compte des conséquences du gaspillage et des repas manquants. Il serait également utile d’étudier les erreurs les plus importantes et de vérifier le comportement du modèle lorsqu’il est appliqué à des dates ultérieures.
