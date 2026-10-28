# TP0 : MaintAI

## Choix du modèle

**Date :** 27/10/2026  
**Membre :** Hiba Hamdaoui

## Contexte

L'objectif de MaintAI est de prévoir les pannes des machines à partir de différentes mesures. Le rappel est la métrique la plus importante, car il permet d'évaluer la capacité du modèle à détecter les pannes réelles.

## Données et découpage

Le jeu de données utilisé est `data/exemple_pannes.csv`. Il contient 5 000 lignes et 5 colonnes, dont quatre variables numériques : `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours`. Ces variables permettent de prédire la colonne `failure`.

Les données ont été divisées aléatoirement en deux parties : 80 % pour l'entraînement et 20 % pour le test, soit 1 000 lignes pour évaluer les modèles.

## Résultats sur le jeu de test

| Modèle | Rappel | Autres métriques |
|---|---:|---|
| Baseline | 0,000 | Exactitude : 0,824 ; précision : 0,000 ; F1 : 0,000 |
| Régression logistique | 0,574 | Exactitude : 0,889 ; précision : 0,737 ; F1 : 0,645 |
| Arbre de décision | 0,597 | Exactitude : 0,839 ; précision : 0,538 ; F1 : 0,566 |
| Forêt aléatoire | 0,545 | Exactitude : 0,873 ; précision : 0,671 ; F1 : 0,602 |
| KNN | 0,540 | Exactitude : 0,878 ; précision : 0,699 ; F1 : 0,609 |

## Modèle retenu et justification

Je choisis l'arbre de décision, car il obtient le meilleur rappel, avec un score de 0,597. Il détecte donc davantage de pannes que les autres modèles testés. La baseline ayant un rappel nul, le critère d'amélioration est bien respecté. Toutefois, les performances restent perfectibles et doivent être vérifiées sur d'autres jeux de données.

## Limites

Les résultats ont été obtenus à partir d'un seul découpage des données. De plus, l'origine du jeu de données n'est pas précisée. Il est donc nécessaire de réaliser d'autres tests pour vérifier si le modèle reste performant sur de nouvelles machines et dans des conditions réelles.

---

# TP0 : CantineAI

## Le problème

CantineAI vise à prévoir le nombre de repas nécessaires pour une date donnée. L'objectif est de mieux gérer les quantités préparées, de limiter le gaspillage alimentaire et d'éviter les repas manquants.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Ridge | 22,623 | 28,545 | 0,880 |
| Random Forest | 31,845 | 41,540 | 0,746 |
| KNN | 36,212 | 46,037 | 0,688 |
| Decision Tree | 46,000 | 59,710 | 0,475 |
| Baseline | 70,271 | 88,416 | -0,151 |

## Mon choix et sa justification

Je retiens le modèle Ridge, car il présente les meilleurs résultats parmi les modèles comparés. Son erreur absolue moyenne (MAE) est de 22,623, ce qui signifie que ses prédictions s'écartent en moyenne d'environ 23 repas des valeurs réelles.

Son coefficient R² de 0,880 montre également qu'il explique une grande partie des variations du nombre de repas. Il constitue donc le meilleur choix parmi les modèles évalués.

## Le critère (rappel ≥ 0,75) est-il atteint ?

Il n'est pas possible de vérifier ce critère avec les résultats disponibles. Le rappel est utilisé pour les problèmes de classification, tandis que CantineAI prédit un nombre de repas : il s'agit ici d'un problème de régression. Il faut donc vérifier si ce seuil concerne une autre partie du TP ou si une tâche de classification est également demandée.

## Ce qui reste à vérifier

Même si Ridge donne les meilleurs résultats, une erreur moyenne d'environ 23 repas peut avoir un impact sur l'organisation de la cantine. Il reste à déterminer si cette marge d'erreur est acceptable, à analyser les prédictions les moins précises et à tester le modèle sur des dates futures afin de vérifier sa fiabilité.