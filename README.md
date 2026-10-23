# NESTY — Agence immobilière
NESTY est une application web de gestion immobilière développée avec Python, Flask, SQLite, HTML, CSS et JavaScript.
## Fonctionnalités
- Consultation des logements disponibles à Yaoundé.
- Recherche par type, quartier, loyer maximum et nombre de pièces.
- Consultation des détails d'un logement.
- Demande de visite en ligne.
- Connexion administrateur.
- Gestion des logements.
- Gestion des demandes de visite.
- Gestion des locations.
- Enregistrement des paiements mensuels.
- Statistiques immobilières via une API JSON.
## Prérequis
- Python 3.10 ou version ultérieure.
- pip.
## Installation sous Windows
Ouvrir un terminal dans le dossier du projet, puis exécuter :
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Création de la base de données de test

Attention : le script donnees_test.py supprime les tables existantes avant de recréer les données de démonstration.

Exécuter cette commande uniquement si la réinitialisation de la base est souhaitée :

python donnees_test.py

Lancement

python app.py

Ouvrir ensuite :

http://127.0.0.1:5000

Compte administrateur de démonstration

Identifiant : admin

Mot de passe : Admin@2026

Ce compte est réservé aux tests locaux. Changez le mot de passe avant tout déploiement réel.

Images

Les photos doivent se trouver dans le dossier static/images/.

Exemples :

* static/images/studio/1.JPG
* static/images/chambre/1.JPG
* static/images/appartement/1.JPG
* static/images/villa/1.JPG

Les chemins enregistrés dans la base commencent par images/, car Flask les résout dans le dossier static/.

Sécurité

* Les mots de passe administrateur sont stockés sous forme d’empreinte.
* Les requêtes SQL utilisent des paramètres.
* Les routes d’administration sont protégées par une session.
* Le mode debug doit rester désactivé pour la remise finale.

La clé secrète Flask doit être configurée avec une variable d’environnement NESTY_SECRET_KEY avant tout déploiement.

:::
---
## Avant de lancer NESTY
Il reste à fournir le code complet des cinq pages d'administration, de `base.html`, des pages publiques et de `script.js`, puis à harmoniser l'ensemble avec ton `schema.sql`.
Je préfère être transparente : **je ne peux pas certifier que le projet fonctionne intégralement avec seulement les éléments ci-dessus**. Il faut encore vérifier les formulaires HTML, les routes et les colonnes SQLite ensemble, puis exécuter des tests réels.