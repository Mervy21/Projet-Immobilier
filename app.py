import os
import sqlite3
from pathlib import Path
from functools import wraps
from datetime import date
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    abort,
)
from werkzeug.security import check_password_hash
DOSSIER_PROJET = Path(__file__).resolve().parent
FICHIER_BASE = DOSSIER_PROJET / "projet.db"
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "NESTY_SECRET_KEY",
    "cle-secrete-de-developpement-a-remplacer"
)
def obtenir_connexion():
    connexion = sqlite3.connect(FICHIER_BASE)
    connexion.row_factory = sqlite3.Row
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion
def administrateur_requis(fonction):
    @wraps(fonction)
    def fonction_protegee(*args, **kwargs):
        if "administrateur_id" not in session:
            flash("Veuillez vous connecter pour accéder à cette page.", "erreur")
            return redirect(url_for("connexion_admin"))
        return fonction(*args, **kwargs)
    return fonction_protegee
@app.route("/")
def accueil():
    connexion = obtenir_connexion()
    biens = connexion.execute("""
        SELECT biens.*, quartiers.nom AS quartier
        FROM biens
        JOIN quartiers ON biens.quartier_id = quartiers.id
        WHERE biens.disponible = 1
        ORDER BY biens.id DESC
    """).fetchall()
    quartiers = connexion.execute("""
        SELECT id, nom
        FROM quartiers
        ORDER BY nom
    """).fetchall()
    connexion.close()
    return render_template(
        "accueil.html",
        biens=biens,
        quartiers=quartiers
    )
@app.route("/bien/<int:bien_id>")
def detail_bien(bien_id):
    connexion = obtenir_connexion()
    bien = connexion.execute("""
        SELECT biens.*, quartiers.nom AS quartier
        FROM biens
        JOIN quartiers ON biens.quartier_id = quartiers.id
        WHERE biens.id = ? AND biens.disponible = 1
    """, (bien_id,)).fetchone()
    connexion.close()
    if bien is None:
        abort(404)
    return render_template(
        "detail_bien.html",
        bien=bien,
        aujourd_hui=date.today().isoformat()
    )
@app.route("/demande-visite/<int:bien_id>", methods=["POST"])
def demander_visite(bien_id):
    nom_client = request.form.get("nom_client", "").strip()
    telephone = request.form.get("telephone", "").strip()
    date_souhaitee = request.form.get("date_souhaitee", "").strip()
    message = request.form.get("message", "").strip()
    if not nom_client or not telephone or not date_souhaitee:
        flash("Veuillez remplir tous les champs obligatoires.", "erreur")
        return redirect(url_for("detail_bien", bien_id=bien_id))
    try:
        date_visite = date.fromisoformat(date_souhaitee)
        if date_visite < date.today():
            flash("La date de visite ne peut pas être dans le passé.", "erreur")
            return redirect(url_for("detail_bien", bien_id=bien_id))
    except ValueError:
        flash("La date de visite est invalide.", "erreur")
        return redirect(url_for("detail_bien", bien_id=bien_id))
    connexion = obtenir_connexion()
    bien = connexion.execute("""
        SELECT id
        FROM biens
        WHERE id = ? AND disponible = 1
    """, (bien_id,)).fetchone()
    if bien is None:
        connexion.close()
        abort(404)
    connexion.execute("""
        INSERT INTO demandes_visite
            (bien_id, nom_client, telephone, date_souhaitee, message)
        VALUES (?, ?, ?, ?, ?)
    """, (bien_id, nom_client, telephone, date_souhaitee, message))
    connexion.commit()
    connexion.close()
    flash("Votre demande de visite a été envoyée avec succès.", "succes")
    return redirect(url_for("detail_bien", bien_id=bien_id))
@app.route("/api/biens")
def api_biens():
    type_bien = request.args.get("type", "").strip()
    quartier_id = request.args.get("quartier", "").strip()
    loyer_maximum = request.args.get("loyer_maximum", "").strip()
    pieces_minimum = request.args.get("pieces_minimum", "").strip()
    requete = """
        SELECT biens.id, biens.titre, biens.type,
               biens.loyer_mensuel, biens.nombre_pieces,
               biens.superficie, biens.photos,
               quartiers.nom AS quartier
        FROM biens
        JOIN quartiers ON biens.quartier_id = quartiers.id
        WHERE biens.disponible = 1
    """
    parametres = []
    if type_bien:
        types_autorises = [
            "Studio",
            "Chambre moderne",
            "Appartement",
            "Villa"
        ]
        if type_bien not in types_autorises:
            return jsonify({"erreur": "Type de logement invalide."}), 400
        requete += " AND biens.type = ?"
        parametres.append(type_bien)
    if quartier_id:
        try:
            quartier_id = int(quartier_id)
            if quartier_id < 1:
                raise ValueError
        except ValueError:
            return jsonify({"erreur": "Quartier invalide."}), 400
        requete += " AND biens.quartier_id = ?"
        parametres.append(quartier_id)
    if loyer_maximum:
        try:
            loyer_maximum = int(loyer_maximum)
            if loyer_maximum < 1:
                raise ValueError
        except ValueError:
            return jsonify({"erreur": "Loyer maximum invalide."}), 400
        requete += " AND biens.loyer_mensuel <= ?"
        parametres.append(loyer_maximum)
    if pieces_minimum:
        try:
            pieces_minimum = int(pieces_minimum)
            if pieces_minimum < 1:
                raise ValueError
        except ValueError:
            return jsonify({"erreur": "Nombre de pièces invalide."}), 400
        requete += " AND biens.nombre_pieces >= ?"
        parametres.append(pieces_minimum)
    requete += " ORDER BY biens.id DESC"
    connexion = obtenir_connexion()
    biens = connexion.execute(requete, parametres).fetchall()
    connexion.close()
    return jsonify([dict(bien) for bien in biens])
@app.route("/admin/connexion", methods=["GET", "POST"])
def connexion_admin():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "")
        if not login or not mot_de_passe:
            flash("Veuillez saisir votre identifiant et votre mot de passe.", "erreur")
            return render_template("admin_connexion.html")
        connexion = obtenir_connexion()
        administrateur = connexion.execute("""
            SELECT id, login, empreinte
            FROM administrateurs
            WHERE login = ?
        """, (login,)).fetchone()
        connexion.close()
        if administrateur and check_password_hash(
            administrateur["empreinte"],
            mot_de_passe
        ):
            session.clear()
            session["administrateur_id"] = administrateur["id"]
            session["administrateur_login"] = administrateur["login"]
            flash("Connexion réussie.", "succes")
            return redirect(url_for("tableau_bord_admin"))
        flash("Identifiant ou mot de passe incorrect.", "erreur")
    return render_template("admin_connexion.html")
@app.route("/admin/deconnexion", methods=["POST"])
@administrateur_requis
def deconnexion_admin():
    session.clear()
    flash("Vous êtes déconnecté.", "succes")
    return redirect(url_for("connexion_admin"))
@app.route("/admin")
@administrateur_requis
def tableau_bord_admin():
    connexion = obtenir_connexion()
    statistiques = connexion.execute("""
        SELECT
            COUNT(*) AS total_biens,
            COALESCE(SUM(CASE WHEN disponible = 1 THEN 1 ELSE 0 END), 0)
                AS biens_disponibles,
            COALESCE(SUM(CASE WHEN disponible = 0 THEN 1 ELSE 0 END), 0)
                AS biens_loues
        FROM biens
    """).fetchone()
    demandes = connexion.execute("""
        SELECT demandes_visite.*, biens.titre AS titre_bien
        FROM demandes_visite
        JOIN biens ON demandes_visite.bien_id = biens.id
        WHERE demandes_visite.statut = 'nouvelle'
        ORDER BY demandes_visite.date_creation DESC
    """).fetchall()
    connexion.close()
    return render_template(
        "admin_tableau_bord.html",
        statistiques=statistiques,
        demandes=demandes
    )
@app.route("/admin/biens")
@administrateur_requis
def gestion_biens():
    connexion = obtenir_connexion()
    biens = connexion.execute("""
        SELECT biens.*, quartiers.nom AS quartier
        FROM biens
        JOIN quartiers ON biens.quartier_id = quartiers.id
        ORDER BY biens.id DESC
    """).fetchall()
    quartiers = connexion.execute("""
        SELECT id, nom
        FROM quartiers
        ORDER BY nom
    """).fetchall()
    connexion.close()
    return render_template(
        "admin_biens.html",
        biens=biens,
        quartiers=quartiers
    )
@app.route("/admin/biens/ajouter", methods=["POST"])
@administrateur_requis
def ajouter_bien():
    titre = request.form.get("titre", "").strip()
    type_bien = request.form.get("type", "").strip()
    quartier_id = request.form.get("quartier_id", "").strip()
    loyer = request.form.get("loyer_mensuel", "").strip()
    pieces = request.form.get("nombre_pieces", "").strip()
    superficie = request.form.get("superficie", "").strip()
    equipements = request.form.get("equipements", "").strip()
    photos = request.form.get("photos", "").strip()
    description = request.form.get("description", "").strip()
    types_autorises = [
        "Studio",
        "Chambre moderne",
        "Appartement",
        "Villa"
    ]
    try:
        quartier_id = int(quartier_id)
        loyer = int(loyer)
        pieces = int(pieces)
        superficie = float(superficie)
        if (
            not titre
            or type_bien not in types_autorises
            or quartier_id < 1
            or loyer <= 0
            or pieces < 1
            or superficie <= 0
            or not description
        ):
            raise ValueError
    except ValueError:
        flash("Vérifiez les informations du logement.", "erreur")
        return redirect(url_for("gestion_biens"))
    connexion = obtenir_connexion()
    try:
        connexion.execute("""
            INSERT INTO biens (
                titre, type, quartier_id, loyer_mensuel,
                nombre_pieces, superficie, equipements,
                photos, disponible, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            titre,
            type_bien,
            quartier_id,
            loyer,
            pieces,
            superficie,
            equipements,
            photos,
            description
        ))
        connexion.commit()
        flash("Logement ajouté avec succès.", "succes")
    except sqlite3.IntegrityError:
        connexion.rollback()
        flash("Impossible d'ajouter ce logement. Vérifiez le quartier.", "erreur")
    finally:
        connexion.close()
    return redirect(url_for("gestion_biens"))
@app.route("/admin/biens/<int:bien_id>/disponibilite", methods=["POST"])
@administrateur_requis
def changer_disponibilite_bien(bien_id):
    connexion = obtenir_connexion()
    bien = connexion.execute("""
        SELECT id, disponible
        FROM biens
        WHERE id = ?
    """, (bien_id,)).fetchone()
    if bien is None:
        connexion.close()
        abort(404)
    nouvelle_disponibilite = 0 if bien["disponible"] else 1
    if nouvelle_disponibilite == 1:
        location_active = connexion.execute("""
            SELECT id
            FROM locations
            WHERE bien_id = ? AND active = 1
        """, (bien_id,)).fetchone()
        if location_active:
            connexion.close()
            flash("Ce logement possède une location active.", "erreur")
            return redirect(url_for("gestion_biens"))
    connexion.execute("""
        UPDATE biens
        SET disponible = ?
        WHERE id = ?
    """, (nouvelle_disponibilite, bien_id))
    connexion.commit()
    connexion.close()
    flash("Disponibilité du logement mise à jour.", "succes")
    return redirect(url_for("gestion_biens"))
@app.route("/admin/demandes")
@administrateur_requis
def gestion_demandes():
    connexion = obtenir_connexion()

    try:
        demandes = connexion.execute("""
            SELECT demandes_visite.*, biens.titre AS titre_bien
            FROM demandes_visite
            JOIN biens ON demandes_visite.bien_id = biens.id
            ORDER BY demandes_visite.date_creation DESC
        """).fetchall()

        return render_template(
            "admin_demandes.html",
            demandes=demandes
        )
    finally:
        connexion.close()
@app.route("/admin/demandes/<int:demande_id>/statut", methods=["POST"])
@administrateur_requis
def changer_statut_demande(demande_id):
    statut = request.form.get("statut", "").strip()
    statuts_autorises = ["nouvelle", "confirmée", "effectuée"]
    if statut not in statuts_autorises:
        flash("Statut invalide.", "erreur")
        return redirect(url_for("gestion_demandes"))
    connexion = obtenir_connexion()
    curseur = connexion.execute("""
        UPDATE demandes_visite
        SET statut = ?
        WHERE id = ?
    """, (statut, demande_id))
    connexion.commit()
    connexion.close()
    if curseur.rowcount == 0:
        abort(404)
    flash("Statut de la demande mis à jour.", "succes")
    return redirect(url_for("gestion_demandes"))
@app.route("/admin/locations")
@administrateur_requis
def gestion_locations():
    connexion = obtenir_connexion()
    locations = connexion.execute("""
        SELECT locations.*, biens.titre AS titre_bien
        FROM locations
        JOIN biens ON locations.bien_id = biens.id
        ORDER BY locations.active DESC, locations.id DESC
    """).fetchall()
    biens_disponibles = connexion.execute("""
        SELECT id, titre
        FROM biens
        WHERE disponible = 1
        ORDER BY titre
    """).fetchall()
    connexion.close()
    return render_template(
        "admin_locations.html",
        locations=locations,
        biens=biens_disponibles
    )
@app.route("/admin/locations/ajouter", methods=["POST"])
@administrateur_requis
def ajouter_location():
    bien_id = request.form.get("bien_id", "").strip()
    nom_locataire = request.form.get("nom_locataire", "").strip()
    date_entree = request.form.get("date_entree", "").strip()
    caution = request.form.get("caution", "").strip()
    loyer_convenu = request.form.get("loyer_convenu", "").strip()
    try:
        bien_id = int(bien_id)
        caution = int(caution)
        loyer_convenu = int(loyer_convenu)
        date_valide = date.fromisoformat(date_entree)
        if (
            not nom_locataire
            or caution < 0
            or loyer_convenu <= 0
            or date_valide > date.today()
        ):
            raise ValueError
    except (ValueError, TypeError):
        flash("Vérifiez les informations de la location.", "erreur")
        return redirect(url_for("gestion_locations"))
    connexion = obtenir_connexion()
    bien = connexion.execute("""
        SELECT id
        FROM biens
        WHERE id = ? AND disponible = 1
    """, (bien_id,)).fetchone()
    if bien is None:
        connexion.close()
        flash("Ce logement n'est pas disponible.", "erreur")
        return redirect(url_for("gestion_locations"))
    try:
        connexion.execute("""
            INSERT INTO locations (
                bien_id, nom_locataire, date_entree,
                date_sortie, caution, loyer_convenu, active
            )
            VALUES (?, ?, ?, NULL, ?, ?, 1)
        """, (
            bien_id,
            nom_locataire,
            date_entree,
            caution,
            loyer_convenu
        ))
        connexion.execute("""
            UPDATE biens
            SET disponible = 0
            WHERE id = ?
        """, (bien_id,))
        connexion.commit()
        flash("Location enregistrée.", "succes")
    except sqlite3.IntegrityError:
        connexion.rollback()
        flash("Impossible d'enregistrer la location.", "erreur")
    finally:
        connexion.close()
    return redirect(url_for("gestion_locations"))
@app.route("/admin/locations/<int:location_id>/terminer", methods=["POST"])
@administrateur_requis
def terminer_location(location_id):
    connexion = obtenir_connexion()
    location = connexion.execute("""
        SELECT bien_id
        FROM locations
        WHERE id = ? AND active = 1
    """, (location_id,)).fetchone()
    if location is None:
        connexion.close()
        abort(404)
    connexion.execute("""
        UPDATE locations
        SET active = 0, date_sortie = ?
        WHERE id = ?
    """, (date.today().isoformat(), location_id))
    connexion.execute("""
        UPDATE biens
        SET disponible = 1
        WHERE id = ?
    """, (location["bien_id"],))
    connexion.commit()
    connexion.close()
    flash("Location terminée.", "succes")
    return redirect(url_for("gestion_locations"))
@app.route("/admin/paiements")
@administrateur_requis
def gestion_paiements():
    connexion = obtenir_connexion()
    paiements = connexion.execute("""
        SELECT paiements.*, locations.nom_locataire,
               biens.titre AS titre_bien
        FROM paiements
        JOIN locations ON paiements.location_id = locations.id
        JOIN biens ON locations.bien_id = biens.id
        ORDER BY paiements.mois_concerne DESC, paiements.id DESC
    """).fetchall()
    locations = connexion.execute("""
        SELECT locations.id, locations.nom_locataire,
               locations.loyer_convenu, biens.titre AS titre_bien
        FROM locations
        JOIN biens ON locations.bien_id = biens.id
        WHERE locations.active = 1
        ORDER BY locations.nom_locataire
    """).fetchall()
    connexion.close()
    return render_template(
        "admin_paiements.html",
        paiements=paiements,
        locations=locations,
        mois_actuel=date.today().strftime("%Y-%m")
    )
@app.route("/admin/paiements/ajouter", methods=["POST"])
@administrateur_requis
def ajouter_paiement():
    location_id = request.form.get("location_id", "").strip()
    mois_concerne = request.form.get("mois_concerne", "").strip()
    montant = request.form.get("montant", "").strip()
    date_paiement = request.form.get("date_paiement", "").strip()
    try:
        location_id = int(location_id)
        montant = int(montant)
        mois_date = date.fromisoformat(mois_concerne + "-01")
        paiement_date = date.fromisoformat(date_paiement)
        if montant <= 0 or paiement_date > date.today():
            raise ValueError
    except (ValueError, TypeError):
        flash("Vérifiez les informations du paiement.", "erreur")
        return redirect(url_for("gestion_paiements"))
    connexion = obtenir_connexion()
    location = connexion.execute("""
        SELECT id
        FROM locations
        WHERE id = ? AND active = 1
    """, (location_id,)).fetchone()
    if location is None:
        connexion.close()
        flash("La location sélectionnée n'est pas active.", "erreur")
        return redirect(url_for("gestion_paiements"))
    try:
        connexion.execute("""
            INSERT INTO paiements (
                location_id, mois_concerne, montant, date_paiement
            )
            VALUES (?, ?, ?, ?)
        """, (
            location_id,
            mois_date.strftime("%Y-%m"),
            montant,
            paiement_date.isoformat()
        ))
        connexion.commit()
        flash("Paiement enregistré.", "succes")
    except sqlite3.IntegrityError:
        connexion.rollback()
        flash("Un paiement existe déjà pour cette location et ce mois.", "erreur")
    finally:
        connexion.close()
    return redirect(url_for("gestion_paiements"))
def _mois_decalage(date_reference, decalage):
    """Retourne un mois au format AAAA-MM, relatif à une date."""
    annee = date_reference.year
    mois = date_reference.month + decalage

    while mois < 1:
        mois += 12
        annee -= 1

    while mois > 12:
        mois -= 12
        annee += 1

    return f"{annee:04d}-{mois:02d}"


@app.route("/api/statistiques")
@administrateur_requis
def api_statistiques():
    connexion = obtenir_connexion()
    mois_actuel = date.today().strftime("%Y-%m")
    premier_mois = _mois_decalage(date.today(), -5)

    # 1. Logements disponibles et logements loues
    disponibilite = connexion.execute("""
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN disponible = 1 THEN 1 ELSE 0 END), 0)
                AS disponibles,
            COALESCE(SUM(CASE WHEN disponible = 0 THEN 1 ELSE 0 END), 0)
                AS loues
        FROM biens
    """).fetchone()

    # 2. Nombre de logements par type
    logements_par_type = connexion.execute("""
        SELECT type, COUNT(*) AS nombre
        FROM biens
        GROUP BY type
        ORDER BY nombre DESC, type
    """).fetchall()

    # 3. Demandes de visite par statut
    demandes_par_statut = connexion.execute("""
        SELECT statut, COUNT(*) AS nombre
        FROM demandes_visite
        GROUP BY statut
        ORDER BY statut
    """).fetchall()

    # 4. Revenus mensuels enregistres sur les six derniers mois
    revenus_par_mois = connexion.execute("""
        SELECT mois_concerne AS mois,
               COALESCE(SUM(montant), 0) AS revenu
        FROM paiements
        WHERE mois_concerne >= ? AND mois_concerne <= ?
        GROUP BY mois_concerne
        ORDER BY mois_concerne
    """, (premier_mois, mois_actuel)).fetchall()

    # 5. Loyer moyen par quartier
    loyers_quartiers = connexion.execute("""
        SELECT quartiers.nom AS quartier,
               ROUND(AVG(biens.loyer_mensuel), 0) AS loyer_moyen
        FROM biens
        JOIN quartiers ON biens.quartier_id = quartiers.id
        GROUP BY quartiers.id, quartiers.nom
        ORDER BY loyer_moyen DESC
    """).fetchall()

    # Statistiques complementaires conservees pour le tableau de bord existant
    loyers_types = connexion.execute("""
        SELECT type,
               ROUND(AVG(loyer_mensuel), 0) AS loyer_moyen
        FROM biens
        GROUP BY type
        ORDER BY type
    """).fetchall()

    taux_occupation = 0
    if disponibilite["total"] > 0:
        taux_occupation = round(
            disponibilite["loues"] / disponibilite["total"] * 100,
            2
        )

    # Locations actives sans paiement enregistre pour le mois actuel
    loyers_impayes = connexion.execute("""
        SELECT locations.id AS location_id,
               locations.nom_locataire,
               locations.loyer_convenu,
               biens.titre AS titre_bien,
               quartiers.nom AS quartier
        FROM locations
        JOIN biens ON locations.bien_id = biens.id
        JOIN quartiers ON biens.quartier_id = quartiers.id
        WHERE locations.active = 1
          AND NOT EXISTS (
              SELECT 1
              FROM paiements
              WHERE paiements.location_id = locations.id
                AND paiements.mois_concerne = ?
          )
        ORDER BY locations.nom_locataire
    """, (mois_actuel,)).fetchall()

    revenus_du_mois = connexion.execute("""
        SELECT COALESCE(SUM(montant), 0) AS total
        FROM paiements
        WHERE mois_concerne = ?
    """, (mois_actuel,)).fetchone()

    connexion.close()

    # Inclure les mois sans paiement afin que la courbe affiche bien six mois
    revenus_index = {
        ligne["mois"]: ligne["revenu"]
        for ligne in revenus_par_mois
    }
    mois_labels = []
    revenus_labels = []

    for decalage in range(-5, 1):
        mois = _mois_decalage(date.today(), decalage)
        mois_labels.append(mois)
        revenus_labels.append(revenus_index.get(mois, 0))

    return jsonify({
        "disponibilite": {
            "disponibles": disponibilite["disponibles"],
            "loues": disponibilite["loues"],
            "total": disponibilite["total"]
        },
        "logements_par_type": [dict(ligne) for ligne in logements_par_type],
        "demandes_par_statut": [dict(ligne) for ligne in demandes_par_statut],
        "revenus_par_mois": {
            "mois": mois_labels,
            "revenus": revenus_labels
        },
        "loyers_moyens_par_quartier": [dict(ligne) for ligne in loyers_quartiers],
        "loyers_moyens_par_type": [dict(ligne) for ligne in loyers_types],
        "taux_occupation_pourcent": taux_occupation,
        "locations_impayees_ce_mois": [dict(ligne) for ligne in loyers_impayes],
        "revenus_du_mois": revenus_du_mois["total"],
        "mois_actuel": mois_actuel
    })
@app.errorhandler(404)
def page_introuvable(erreur):
    return render_template("404.html"), 404
if __name__ == "__main__":
    app.run(debug=False)