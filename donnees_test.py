"""
Script de création des données de test de l'agence immobilière.

Les quartiers sont situés à Yaoundé, au Cameroun.
Les biens, les clients, les locataires et les paiements
sont des données fictives destinées aux tests.
"""

import sqlite3
import random

from datetime import date, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash

# 1. CONFIGURATION

DOSSIER_PROJET = Path(__file__).resolve().parent

FICHIER_BASE = DOSSIER_PROJET / "projet.db"
FICHIER_SCHEMA = DOSSIER_PROJET / "schema.sql"

random.seed(42)


# 2. QUARTIERS DE YAOUNDÉ

QUARTIERS = [
    "Bastos",
    "Nlongkak",
    "Mokolo",
    "Tsinga",
    "Biyem-Assi",
    "Mendong",
    "Mvan",
    "Essos",
    "Mimboman",
    "Ngousso",
]

# 3. NOMS POUR LES DONNÉES DE TEST

PRENOMS = [
    "Merveille",
    "Clarisse",
    "Sandrine",
    "Esther",
    "Grâce",
    "Patricia",
    "Brenda",
    "Carine",
    "Diane",
    "Joëlle",
    "Fabrice",
    "Junior",
    "Arnaud",
    "Emmanuel",
    "Christian",
    "Landry",
    "Yvan",
    "Samuel",
    "Serge",
    "Patrick",
]

NOMS = [
    "Nkom",
    "Mballa",
    "Atangana",
    "Ngono",
    "Mvondo",
    "Etoa",
    "Essomba",
    "Ondoa",
    "Abena",
    "Fouda",
    "Owona",
    "Mbarga",
    "Ndongo",
    "Nana",
    "Tsala",
    "Mekongo",
    "Kamga",
    "Fomo",
    "Tchoumi",
    "Njoya",
]

# 4. TYPES DE LOGEMENTS

TYPES_BIENS = [
    "Studio",
    "Chambre moderne",
    "Appartement",
    "Villa",
]

EQUIPEMENTS = [
    "Eau courante, électricité",
    "Douche interne, cuisine",
    "Parking, eau courante",
    "Cuisine, douche interne, balcon",
    "Compteur ENEO, forage",
    "Cuisine, parking, balcon",
    "Forage, gardiennage",
    "Eau courante, carrelage",
    "Douche interne, compteur ENEO",
    "Cuisine équipée, parking",
]

# 5. CHEMINS DES PHOTOS

PHOTOS_PAR_TYPE = {
    "Studio": [
        "images/studio/1.JPG",
        "images/studio/2.JPG",
        "images/studio/3.JPG",
        "images/studio/4.JPG",
    ],
    "Chambre moderne": [
        "images/chambre/1.JPG",
        "images/chambre/2.JPG",
        "images/chambre/3.JPG",
        "images/chambre/4.JPG",
    ],
    "Appartement": [
        "images/appartement/1.JPG",
        "images/appartement/2.JPG",
        "images/appartement/3.JPG",
        "images/appartement/4.JPG",
    ],
    "Villa": [
        "images/villa/1.JPG",
        "images/villa/2.JPG",
        "images/villa/3.JPG",
        "images/villa/4.JPG",
    ],
}

# 6. FONCTIONS UTILITAIRES


def generer_nom():
    """Génère un nom fictif pour les données de test."""
    prenom = random.choice(PRENOMS)
    nom = random.choice(NOMS)

    return f"{prenom} {nom}"


def generer_telephone():
    """Génère un numéro fictif."""
    prefixes = [
        "650",
        "651",
        "652",
        "653",
        "654",
        "655",
        "656",
        "657",
        "658",
        "659",
        "670",
        "671",
        "672",
        "673",
        "674",
        "675",
        "677",
        "678",
        "680",
        "681",
        "690",
        "691",
        "692",
        "693",
        "694",
        "695",
        "696",
        "697",
        "698",
        "699",
    ]

    prefixe = random.choice(prefixes)
    numero = random.randint(100000, 999999)

    return f"+237 {prefixe} {numero}"


def soustraire_mois(date_reference, nombre_mois):
    """Retourne le premier jour d'un mois antérieur."""
    mois_total = date_reference.year * 12 + date_reference.month - 1 - nombre_mois

    annee = mois_total // 12
    mois = mois_total % 12 + 1

    return date(annee, mois, 1)


def dernier_jour_du_mois(annee, mois):
    """Calcule le dernier jour du mois demandé."""
    if mois == 12:
        premier_jour_suivant = date(annee + 1, 1, 1)
    else:
        premier_jour_suivant = date(annee, mois + 1, 1)

    return premier_jour_suivant - timedelta(days=1)


# 7. VÉRIFICATION DU SCHÉMA SQL

if not FICHIER_SCHEMA.exists():
    raise FileNotFoundError(
        "Le fichier schema.sql est introuvable. "
        "Il doit se trouver dans le dossier du projet."
    )

# 8. CONNEXION À LA BASE DE DONNÉES

connexion = sqlite3.connect(FICHIER_BASE)

# Active la vérification des clés étrangères.
connexion.execute("PRAGMA foreign_keys = ON")

curseur = connexion.cursor()


try:

    # RÉINITIALISATION DES TABLES
    curseur.executescript("""
        DROP TABLE IF EXISTS paiements;
        DROP TABLE IF EXISTS locations;
        DROP TABLE IF EXISTS demandes_visite;
        DROP TABLE IF EXISTS biens;
        DROP TABLE IF EXISTS administrateurs;
        DROP TABLE IF EXISTS quartiers;
    """)

    # Création des tables à partir de schema.sql.
    with open(FICHIER_SCHEMA, "r", encoding="utf-8") as fichier:
        contenu_schema = fichier.read()

    curseur.executescript(contenu_schema)

    print("Structure de la base créée.")

    # 9. INSERTION DES QUARTIERS
    for nom_quartier in QUARTIERS:
        curseur.execute(
            """
            INSERT INTO quartiers (nom, ville)
            VALUES (?, ?)
            """,
            (nom_quartier, "Yaoundé"),
        )

    curseur.execute("SELECT id, nom FROM quartiers")
    identifiants_quartiers = {
        nom: identifiant for identifiant, nom in curseur.fetchall()
    }
    print("10 quartiers ajoutés.")

    # 10. CRÉATION DES 50 BIENS

    identifiants_biens = []

    for numero in range(1, 51):

        type_bien = TYPES_BIENS[(numero - 1) % len(TYPES_BIENS)]

        quartier = QUARTIERS[(numero - 1) % len(QUARTIERS)]

        # Prix fictifs de démonstration.
        if type_bien == "Chambre moderne":
            loyer = random.randrange(25000, 65001, 5000)

        elif type_bien == "Studio":
            loyer = random.randrange(45000, 100001, 5000)

        elif type_bien == "Appartement":
            loyer = random.randrange(80000, 251001, 10000)

        else:
            loyer = random.randrange(200000, 601001, 25000)

        # Nombre de pièces et superficie.
        if type_bien == "Chambre moderne":
            nombre_pieces = 1
            superficie = random.randint(12, 30)

        elif type_bien == "Studio":
            nombre_pieces = random.randint(1, 2)
            superficie = random.randint(20, 45)

        elif type_bien == "Appartement":
            nombre_pieces = random.randint(2, 5)
            superficie = random.randint(45, 160)

        else:
            nombre_pieces = random.randint(4, 8)
            superficie = random.randint(100, 350)

        equipements = random.choice(EQUIPEMENTS)

        liste_photos = PHOTOS_PAR_TYPE[type_bien]
        photo = liste_photos[(numero - 1) // len(TYPES_BIENS) % len(liste_photos)]

        titre = f"{type_bien} à louer à {quartier} n° {numero}"

        description = (
            f"{type_bien} situé à {quartier}, Yaoundé. "
            f"Superficie : {superficie} m². "
            "Annonce destinée à la démonstration."
        )

        disponible = 0 if numero <= 20 else 1

        curseur.execute(
            """
            INSERT INTO biens (
                titre,
                type,
                quartier_id,
                loyer_mensuel,
                nombre_pieces,
                superficie,
                equipements,
                photos,
                disponible,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                titre,
                type_bien,
                identifiants_quartiers[quartier],
                loyer,
                nombre_pieces,
                superficie,
                equipements,
                photo,
                disponible,
                description,
            ),
        )

        identifiants_biens.append(curseur.lastrowid)

    print("50 biens immobiliers ajoutés.")

    # 11. CRÉATION DES 60 DEMANDES DE VISITE

    statuts_visite = [
        "nouvelle",
        "confirmée",
        "effectuée",
    ]

    for numero in range(60):
        bien_id = random.choice(identifiants_biens)
        nom_client = generer_nom()
        telephone = generer_telephone()

        date_souhaitee = (
            date.today() + timedelta(days=random.randint(1, 30))
        ).isoformat()

        message = random.choice(
            [
                "Je souhaite visiter ce logement.",
                "Le logement est-il toujours disponible ?",
                "Je voudrais connaître les conditions de location.",
                "Est-il possible de visiter en fin de journée ?",
                "Je souhaite obtenir plus d'informations.",
            ]
        )

        statut = random.choice(statuts_visite)

        curseur.execute(
            """
            INSERT INTO demandes_visite (
                bien_id,
                nom_client,
                telephone,
                date_souhaitee,
                message,
                statut
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                bien_id,
                nom_client,
                telephone,
                date_souhaitee,
                message,
                statut,
            ),
        )

    print("60 demandes de visite ajoutées.")

    # 12. CRÉATION DES 20 LOCATIONS

    identifiants_locations = []

    for numero in range(20):

        bien_id = identifiants_biens[numero]

        curseur.execute(
            """
            SELECT loyer_mensuel
            FROM biens
            WHERE id = ?
            """,
            (bien_id,),
        )

        loyer_initial = curseur.fetchone()[0]

        date_entree = (date.today() - timedelta(days=400 + numero)).isoformat()

        caution = loyer_initial
        loyer_convenu = loyer_initial

        curseur.execute(
            """
            INSERT INTO locations (
                bien_id,
                nom_locataire,
                date_entree,
                date_sortie,
                caution,
                loyer_convenu,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bien_id,
                generer_nom(),
                date_entree,
                None,
                caution,
                loyer_convenu,
                1,
            ),
        )

        identifiants_locations.append((curseur.lastrowid, loyer_convenu))

    print("20 locations ajoutées.")

    # 13. CRÉATION DES 150 PAIEMENTS

    aujourd_hui = date.today()

    mois_precedents = [
        soustraire_mois(aujourd_hui, decalage) for decalage in range(7, 0, -1)
    ]

    nombre_paiements = 0

    for identifiant_location, loyer_convenu in identifiants_locations:

        for mois in mois_precedents:

            mois_concerne = mois.strftime("%Y-%m")

            date_paiement = dernier_jour_du_mois(
                mois.year,
                mois.month,
            ).isoformat()

            curseur.execute(
                """
                INSERT INTO paiements (
                    location_id,
                    mois_concerne,
                    montant,
                    date_paiement
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    identifiant_location,
                    mois_concerne,
                    loyer_convenu,
                    date_paiement,
                ),
            )

            nombre_paiements += 1

    mois_actuel = aujourd_hui.strftime("%Y-%m")

    for identifiant_location, loyer_convenu in identifiants_locations[:10]:

        curseur.execute(
            """
            INSERT INTO paiements (
                location_id,
                mois_concerne,
                montant,
                date_paiement
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                identifiant_location,
                mois_actuel,
                loyer_convenu,
                aujourd_hui.isoformat(),
            ),
        )

        nombre_paiements += 1

    print(f"{nombre_paiements} paiements ajoutés.")

    # 14. CRÉATION DU COMPTE ADMINISTRATEUR

    identifiant_admin = "admin"
    mot_de_passe_admin = "Admin@2026"

    empreinte_mot_de_passe = generate_password_hash(mot_de_passe_admin)

    curseur.execute(
        """
        INSERT INTO administrateurs (login, empreinte)
        VALUES (?, ?)
        """,
        (
            identifiant_admin,
            empreinte_mot_de_passe,
        ),
    )

    # 15. VALIDATION ET AFFICHAGE DU RÉSULTAT

    connexion.commit()

    print("\n======================================")
    print("BASE DE DONNÉES CRÉÉE AVEC SUCCÈS")
    print("======================================")
    print(f"Fichier : {FICHIER_BASE}")
    print("Quartiers : 10")
    print("Biens immobiliers : 50")
    print("Demandes de visite : 60")
    print("Locations : 20")
    print(f"Paiements : {nombre_paiements}")
    print("Administrateur : admin")
    print("Mot de passe : Admin@2026")
    print("======================================")

except Exception:
    connexion.rollback()
    raise
finally:
    connexion.close()
