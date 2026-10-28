#TP0: maintAI 

# Choix du modèle

Date : 27/10/2026 · Groupe : Najim Aya 
                           : Rhazouani Malak
                           : Mekkaoui Imane
                           : Hamdaoui Hiba

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
