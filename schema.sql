PRAGMA foreign_keys = ON;

--  TABLES QUARTIERS

CREATE TABLE IF NOT EXISTS quartiers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    ville TEXT NOT NULL DEFAULT 'Yaounde',
    UNIQUE(nom,ville)
);

-- TABLES DES BIENS IMMOBILIERS

CREATE TABLE IF NOT EXISTS biens(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL, 
    type TEXT NOT NULL CHECK(type IN(
        'Studio',
        'Chambre moderne',
        'Appartement',
        'Villa'
    )),
    quartier_id INTEGER NOT NULL,
    loyer_mensuel INTEGER NOT NULL CHECK(loyer_mensuel > 0),
    nombre_pieces INTEGER NOT NULL CHECK(nombre_pieces >= 1),
    superficie REAL NOT NULL CHECK(superficie > 0),
    equipements TEXT NOT NULL DEFAULT '',
    photos TEXT NOT NULL DEFAULT '',
    disponible INTEGER NOT NULL DEFAULT 1
        CHECK(disponible IN (0, 1)),
    description TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (quartier_id)
        REFERENCES quartiers(id)
);

-- TABLES DEMANDES DE VISIT
CREATE TABLE IF NOT EXISTS demandes_visite(
    id INTEGER  PRIMARY KEY  AUTOINCREMENT,
    bien_id INTEGER NOT NULL,
    nom_client TEXT NOT NULL,
    telephone TEXT NOT NULL,
    date_souhaitee TEXT NOT NULL,
    message TEXT NOT NULL DEFAULT '',
    statut TEXT NOT NULL DEFAULT 'nouvelle'
    CHECK (statut IN(
        'nouvelle',
        'confirmée',
        'effectuée'
    )),
    date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(bien_id)
      REFERENCES biens(id)
);

-- TABLES DES LOCATIONS 

CREATE TABLE IF NOT EXISTS locations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bien_id INTEGER NOT NULL,
    nom_locataire TEXT NOT NULL,
    date_entree TEXT NOT NULL,
    date_sortie TEXT,
    caution INTEGER NOT NULL CHECK(caution>=0),
    loyer_convenu INTEGER NOT NULL CHECK(loyer_convenu>0),
    active INTEGER NOT NULL DEFAULT 1
    CHECK(active IN (0,1)),
    FOREIGN KEY(bien_id)
    REFERENCES biens(id)
);

-- TABLES DES PAIEMENTS

CREATE TABLE IF NOT EXISTS paiements(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    mois_concerne TEXT NOT NULL,
    montant INTEGER NOT NULL CHECK(montant>0),
    date_paiement TEXT NOT NULL,
    FOREIGN KEY (location_id)
    REFERENCES locations(id),
    
    UNIQUE(location_id,mois_concerne)
);

-- TABLES DES ADMINISTRATEURS

CREATE TABLE IF NOT EXISTS administrateurs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL,
    empreinte TEXT NOT NULL
);

-- INDEX POUR LES RECHERCHES

CREATE INDEX IF NOT EXISTS idx_biens_recherche ON biens(
    type,
    quartier_id,
    loyer_mensuel,
    nombre_pieces,
    disponible
);

CREATE INDEX IF NOT EXISTS idx_paiements_mois
ON paiements(mois_concerne);