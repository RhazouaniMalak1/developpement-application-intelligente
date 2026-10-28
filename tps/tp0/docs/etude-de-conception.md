# Étude de conception — Prédiction des pannes de machines

Groupe : Najim Aya       · Version : complétée · Date : 27/10/2026
       : Rhazouani Malak
       : Mekkaoui Imane
       : Hamdaoui Hiba 

## 1. Contexte et utilisateurs
- Utilisateur principal : technicien de maintenance industrielle.

## 2. Problème et décision
- Décision : déterminer si une machine présente un risque de panne afin de planifier une vérification.
- Fréquence : à chaque nouvelle série de mesures de la machine.
- Coût d'une erreur : une panne non détectée peut causer un arrêt ; une fausse alerte demande une vérification inutile.

## 3. Approche par sous-problème
| Sous-problème | Approche | Pourquoi pas une approche plus simple |
|---|---|---|
| Prédire la panne ("failure") | Classification supervisée avec plusieurs modèles de machine learning et une baseline. | Des règles fixes pourraient mal représenter les liens entre les mesures et les pannes. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| "data/exemple_pannes.csv" | Fichier d'exemple fourni dans le projet ; source externe et licence non précisées. | 5 000 lignes, 5 colonnes ; 4 variables d'entrée et la cible "failure". | Aucune donnée personnelle n'est indiquée, les colonnes décrivent des mesures de machines. |

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : classificateur qui prédit la classe la plus fréquente ; rappel de 0,000 sur le jeu de test.
- Métrique principale : rappel, car le projet cherche à détecter les pannes et à limiter les pannes manquées.
- Critère d'acceptation : obtenir un rappel supérieur à 0,000 sur le jeu de test de 1 000 lignes ; l'arbre de décision atteint 0,597. Aucun seuil chiffré supplémentaire n'est défini.

## 6. Architecture prévue
Le programme charge le CSV, sépare les données en entraînement et en test, puis prépare les variables numériques et entraîne les modèles. Il compare leurs résultats, sauvegarde le meilleur modèle dans "models/model.joblib" et les scores dans "models/metrics.json".

## 7. Choix technologiques
Le projet utilise Python, pandas et scikit-learn pour lire les données, préparer les variables, entraîner les modèles et calculer les métriques. La graine 42 rend le découpage aléatoire reproductible.

## 8. Risques, éthique, confidentialité
Une panne mal détectée peut provoquer un arrêt, tandis qu'une fausse alerte peut entraîner une inspection inutile. Les données fournies ne contiennent pas de colonne personnelle, mais leur origine n'est pas précisée et le modèle doit être vérifié avant une utilisation réelle.

## 9. Limites et hors périmètre
L'évaluation utilise un seul découpage aléatoire et un fichier d'exemple, les scores peuvent changer avec d'autres données. Le projet ne décrit ni le déploiement en usine, ni le suivi du modèle, ni une décision automatique de réparation.
