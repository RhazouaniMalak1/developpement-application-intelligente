#TP0: maintAI 

# Choix du modèle

Date : 27/10/2026 · membre  : Malak Rhazouani
                            
                           
                           

## Contexte
Le projet prédit si une machine tombe en panne à partir de ses mesures. Le rappel est la métrique principale, car il faut repérer le plus de pannes possible.

## Données et découpage
Le fichier utilisé est 'data/exemple_pannes.csv' : il contient 5 000 lignes et 5 colonnes. Les quatre mesures numériques (temperature_c, vibration_mm_s, load_pct, runtime_hours) servent à prédire failure, le découpage est aléatoire, avec 80 % des lignes pour l'entraînement et 20 % pour le test (1 000 lignes).

## Résultats sur le jeu de test

| Modèle | Métrique principale : rappel | Autres métriques |
|---|---:|---|
| Baseline | 0,000 | Exactitude : 0,824 ; précision : 0,000 ; F1 : 0,000 |
| Régression logistique | 0,574 | Exactitude : 0,889 ; précision : 0,737 ; F1 : 0,645 |
| Arbre de décision | 0,597 | Exactitude : 0,839 ; précision : 0,538 ; F1 : 0,566 |
| Forêt aléatoire | 0,545 | Exactitude : 0,873 ; précision : 0,671 ; F1 : 0,602 |
| K plus proches voisins (KNN) | 0,540 | Exactitude : 0,878 ; précision : 0,699 ; F1 : 0,609 |

## Décision
L'arbre de décision est retenu, car il obtient le meilleur rappel : 0,597, soit 0,597 de plus que la baseline. Le critère défini ici, dépasser le rappel de la baseline sur le jeu de test est atteint, aucun seuil chiffré supplémentaire n'est indiqué dans le projet.

## Limites
Le résultat dépend d'un seul découpage aléatoire et le fichier fourni ne décrit pas l'origine des données. Ces scores ne garantissent donc pas les mêmes performances sur d'autres machines ou de nouvelles données.
  
 


# TP0 : CantineAI

**Nom :** RHAZOUANI Malak  
**Groupe :** G

## Le problème

Prédire le nombre de repas à préparer pour une date donnée afin de réduire le gaspillage alimentaire et d’éviter les repas manquants.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Ridge | 22,623 | 28,545 | 0,880 |
| Random Forest | 31,845 | 41,540 | 0,746 |
| KNN | 36,212 | 46,037 | 0,688 |
| Decision Tree | 46,000 | 59,710 | 0,475 |
| Baseline | 70,271 | 88,416 | -0,151 |

## Mon choix, et pourquoi

Je choisis le modèle **Ridge**, car il obtient les meilleures performances. Son MAE est de 22,623 repas, ce qui signifie que ses prédictions s’écartent en moyenne d’environ 23 repas du nombre réel. Son coefficient R² de 0,880 indique qu’il explique une grande partie de la variabilité du nombre de repas servis.

## Le critère (rappel ≥ 0,75) est-il atteint ?

Ce critère ne peut pas être évalué directement avec les résultats actuels, car le rappel est une métrique de classification. Ici, le problème est traité comme une régression, qui prédit un nombre de repas. Il faut donc vérifier si le seuil de rappel concerne une autre partie du TP ou si une classification est également attendue.

## Ce qui reste flou

Il reste à vérifier si l’erreur moyenne d’environ 23 repas est acceptable pour la cantine, notamment en raison du coût du gaspillage et des repas manquants. Il faut aussi examiner les erreurs les plus importantes et vérifier que le modèle fonctionne correctement sur des dates futures.