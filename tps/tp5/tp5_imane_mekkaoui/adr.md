# ADR 004 : Choix du modèle après recherche sur grille

Date : 25/11/2026 · Auteurs : Imane Mekkaoui

## Contexte
MaintAI utilise les mesures des capteurs pour déclencher des alertes de panne. Une panne manquée coûte plus cher qu'une fausse alerte. La grille de 30 essais compare la régression logistique et la forêt aléatoire sur le CSV v2. Le classement donne la priorité au plus petit nombre de pannes manquées, puis au plus petit nombre de fausses alertes.

## Options étudiées
1. Régression logistique, C=0.1, seuil 0.20 : 30 pannes manquées et 152 fausses alertes en validation (rappel 85,3 %, précision 53,4 %).
2. Régression logistique, C=0.01 : autant de pannes manquées (30), et quatre fausses alertes de plus.
3. Forêt aléatoire : comparée dans la même grille. Le classement ne la retient pas.

## Décision
Retenir une régression logistique avec standardisation des mesures (`StandardScaler`), C=0.1, `max_iter=1000` et un seuil d'alerte de 0.20. Une alerte est déclenchée lorsque la probabilité estimée atteint ou dépasse ce seuil.

L'essai retenu a manqué 30 pannes sur la validation, comme l'essai avec C=0.01. Il a produit 152 fausses alertes, soit quatre de moins. Il obtient 85,3 % de rappel et 53,4 % de précision sur la validation. Réentraîné sur les 6 400 lignes de développement, le modèle obtient 82,9 % de rappel, 55,9 % de précision et 89,4 % d'accuracy sur les 1 600 lignes du test réservé.

Expérience MLflow : `maintai-grid-search`  
Run retenu : `1cc1cc0a35cb4621aa1c83f748ee4943`  
Empreinte de la v2 (`data_md5`) : `93fdeef2cac1893c4f720c16457eea75`

## Conséquences
Sur le test réservé, environ 44 % des alertes sont fausses. Ce volume d'alertes est le coût du réglage retenu. Pour réentraîner et enregistrer le pipeline et son seuil via le flux habituel du TP, utiliser la commande suivante avec le CSV v2.

```bash
python -m maintai.train --model logreg --C 0.1 --threshold 0.20
```
