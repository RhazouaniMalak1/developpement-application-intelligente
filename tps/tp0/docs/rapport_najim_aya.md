# TP0 : maintAI

# Choix du modèle

Date : 27/10/2026 · Membre : Najim Aya

## Contexte
L'objectif du projet est d'anticiper les pannes de machines grâce à leurs mesures. On privilégie le rappel, puisqu'il s'agit d'identifier un maximum de pannes réelles.

## Données et découpage
Le jeu de données 'data/exemple_pannes.csv' comprend 5 000 lignes réparties sur 5 colonnes. Les quatre variables numériques (temperature_c, vibration_mm_s, load_pct, runtime_hours) servent d'entrées pour prédire failure. La séparation est faite au hasard : 80 % des observations pour l'apprentissage, 20 % pour le test, soit 1 000 lignes.

## Résultats sur le jeu de test

| Modèle | Métrique principale : rappel | Autres métriques |
|---|---:|---|
| Baseline | 0,000 | Exactitude : 0,824 ; précision : 0,000 ; F1 : 0,000 |
| Régression logistique | 0,574 | Exactitude : 0,889 ; précision : 0,737 ; F1 : 0,645 |
| Arbre de décision | 0,597 | Exactitude : 0,839 ; précision : 0,538 ; F1 : 0,566 |
| Forêt aléatoire | 0,545 | Exactitude : 0,873 ; précision : 0,671 ; F1 : 0,602 |
| K plus proches voisins (KNN) | 0,540 | Exactitude : 0,878 ; précision : 0,699 ; F1 : 0,609 |

## Décision
Mon choix se porte sur l'arbre de décision, dont le rappel de 0,597 est le plus élevé, soit 0,597 de mieux que la baseline. La condition posée, à savoir faire mieux que la baseline en rappel sur le jeu de test, est donc satisfaite. Aucune autre valeur seuil n'est mentionnée dans le projet.

## Limites
Ces résultats proviennent d'une seule séparation aléatoire, et la source des données n'est pas documentée dans le fichier. On ne peut donc pas affirmer que les performances seraient identiques sur d'autres machines ou avec des données nouvelles.


# TP0 : CantineAI

**Nom :** AYA Najim  
**Groupe :** G

## Le problème

Le but est de prévoir combien de repas préparer à une date précise, de façon à réduire le gaspillage de nourriture sans se retrouver à court de repas.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Ridge | 22,623 | 28,545 | 0,880 |
| Random Forest | 31,845 | 41,540 | 0,746 |
| KNN | 36,212 | 46,037 | 0,688 |
| Decision Tree | 46,000 | 59,710 | 0,475 |
| Baseline | 70,271 | 88,416 | -0,151 |

## Mon choix, et pourquoi

J'opte pour le modèle **Ridge**, car c'est lui qui donne les meilleurs scores. Son MAE de 22,623 repas signifie qu'il se trompe en moyenne d'environ 23 repas par rapport à la réalité. Un R² de 0,880 indique qu'il explique une bonne partie des fluctuations du nombre de repas servis.

## Le critère (rappel ≥ 0,75) est-il atteint ?

Je ne peux pas trancher à partir des résultats dont je dispose : le rappel relève de la classification, alors qu'ici on résout un problème de régression (prévoir un nombre de repas). Il reste à savoir si ce seuil s'applique à une autre partie du TP ou si une classification est également demandée.

## Ce qui reste flou

Je dois encore vérifier qu'un écart moyen d'environ 23 repas est tolérable pour la cantine, vu ce que coûtent le gaspillage et les repas manquants. Il faudra aussi regarder de près les plus grosses erreurs et s'assurer que le modèle reste fiable sur des dates à venir.