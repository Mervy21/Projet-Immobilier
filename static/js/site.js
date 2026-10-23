"use strict";

document.addEventListener("DOMContentLoaded", () => {
    initialiserMenu();
    initialiserRecherche();
    initialiserStatistiques();
    initialiserDates();
});


function initialiserMenu() {
    const bouton = document.getElementById("menu-bouton");
    const menu = document.getElementById("menu");

    if (!bouton || !menu) {
        return;
    }

    bouton.addEventListener("click", () => {
        const ouvert = bouton.getAttribute("aria-expanded") === "true";

        bouton.setAttribute("aria-expanded", String(!ouvert));
        menu.classList.toggle("menu-ouvert", !ouvert);
    });
}


function initialiserRecherche() {
    const formulaire = document.getElementById("formulaire-recherche");
    const grille = document.getElementById("grille-biens");
    const compteur = document.getElementById("nombre-resultats");

    if (!formulaire || !grille) {
        return;
    }

    formulaire.addEventListener("submit", async (evenement) => {
        evenement.preventDefault();

        const donnees = new FormData(formulaire);
        const parametres = new URLSearchParams();

        for (const [cle, valeur] of donnees.entries()) {
            if (String(valeur).trim() !== "") {
                parametres.append(cle, String(valeur).trim());
            }
        }

        grille.replaceChildren();

        const chargement = document.createElement("p");
        chargement.className = "message-vide";
        chargement.textContent = "Recherche des logements en cours…";
        grille.appendChild(chargement);

        try {
            const reponse = await fetch(`/api/biens?${parametres.toString()}`);

            if (!reponse.ok) {
                throw new Error("Impossible de récupérer les logements.");
            }

            const biens = await reponse.json();

            grille.replaceChildren();

            if (!Array.isArray(biens) || biens.length === 0) {
                const vide = document.createElement("p");
                vide.className = "message-vide";
                vide.textContent = "Aucun logement ne correspond à vos critères.";
                grille.appendChild(vide);

                if (compteur) {
                    compteur.textContent = "0 logement disponible";
                }

                return;
            }

            biens.forEach((bien) => {
                grille.appendChild(creerCarteBien(bien));
            });

            if (compteur) {
                compteur.textContent =
                    `${biens.length} logement(s) disponible(s)`;
            }

        } catch (erreur) {
            grille.replaceChildren();

            const message = document.createElement("p");
            message.className = "message-vide";
            message.textContent =
                "Une erreur est survenue pendant la recherche. Réessayez.";

            grille.appendChild(message);
            console.error(erreur);
        }
    });

    formulaire.addEventListener("reset", () => {
        window.setTimeout(() => {
            formulaire.requestSubmit();
        }, 0);
    });
}


function creerCarteBien(bien) {
    const carte = document.createElement("article");
    carte.className = "carte-bien";

    const blocImage = document.createElement("div");
    blocImage.className = "image-bien";

    if (bien.photos) {
        const image = document.createElement("img");
        image.src = `/static/${bien.photos}`;
        image.alt = `Photo du logement : ${bien.titre}`;
        image.loading = "lazy";

        image.addEventListener("error", () => {
            image.remove();

            const indisponible = document.createElement("div");
            indisponible.className = "image-indisponible";
            indisponible.textContent = "Photo non disponible";

            blocImage.appendChild(indisponible);
        }, { once: true });

        blocImage.appendChild(image);
    } else {
        const indisponible = document.createElement("div");
        indisponible.className = "image-indisponible";
        indisponible.textContent = "Photo non disponible";

        blocImage.appendChild(indisponible);
    }

    const contenu = document.createElement("div");
    contenu.className = "informations-bien";

    const type = document.createElement("p");
    type.className = "type-bien";
    type.textContent = bien.type || "";

    const titre = document.createElement("h3");
    titre.textContent = bien.titre || "Logement";

    const quartier = document.createElement("p");
    quartier.className = "quartier-bien";
    quartier.textContent = `📍 ${bien.quartier || "Quartier non précisé"}, Yaoundé`;

    const caracteristiques = document.createElement("p");
    caracteristiques.className = "caracteristiques";
    caracteristiques.textContent =
        `${bien.nombre_pieces} pièce(s) · ${bien.superficie} m²`;

    const prix = document.createElement("p");
    prix.className = "prix-bien";

    prix.textContent =
        `${Number(bien.loyer_mensuel).toLocaleString("fr-FR")} FCFA / mois`;

    const lien = document.createElement("a");
    lien.className = "bouton-principal bouton-carte";
    lien.href = `/bien/${encodeURIComponent(bien.id)}`;
    lien.textContent = "Voir le logement";

    contenu.append(type, titre, quartier, caracteristiques, prix, lien);
    carte.append(blocImage, contenu);

    return carte;
}


async function initialiserStatistiques() {
    const conteneur = document.getElementById("bloc-statistiques-detaillees");

    if (!conteneur) {
        return;
    }

    try {
        const reponse = await fetch("/api/statistiques");

        if (!reponse.ok) {
            throw new Error("Impossible de charger les statistiques.");
        }

        const donnees = await reponse.json();

        conteneur.replaceChildren();

        const resume = document.createElement("p");
        resume.textContent =
            `Taux d'occupation : ${donnees.taux_occupation_pourcent} %`;

        const revenus = document.createElement("p");
        revenus.textContent =
            `Paiements enregistrés pour ${donnees.mois_actuel} : ` +
            `${Number(donnees.revenus_du_mois).toLocaleString("fr-FR")} FCFA`;

        const titreQuartiers = document.createElement("h3");
        titreQuartiers.textContent = "Loyers moyens par quartier";

        const listeQuartiers = document.createElement("ul");

        donnees.loyers_moyens_par_quartier.forEach((ligne) => {
            const element = document.createElement("li");

            element.textContent =
                `${ligne.quartier} : ` +
                `${Number(ligne.loyer_moyen).toLocaleString("fr-FR")} FCFA`;

            listeQuartiers.appendChild(element);
        });

        const titreImpayes = document.createElement("h3");
        titreImpayes.textContent = "Locations sans paiement enregistré pour ce mois";

        const listeImpayes = document.createElement("ul");

        if (donnees.locations_impayees_ce_mois.length === 0) {
            const element = document.createElement("li");
            element.textContent = "Aucune location impayée selon les paiements enregistrés.";
            listeImpayes.appendChild(element);
        } else {
            donnees.locations_impayees_ce_mois.forEach((ligne) => {
                const element = document.createElement("li");

                element.textContent =
                    `${ligne.nom_locataire} — ${ligne.titre_bien} — ` +
                    `${Number(ligne.loyer_convenu).toLocaleString("fr-FR")} FCFA`;

                listeImpayes.appendChild(element);
            });
        }

        conteneur.append(
            resume,
            revenus,
            titreQuartiers,
            listeQuartiers,
            titreImpayes,
            listeImpayes
        );

    } catch (erreur) {
        conteneur.textContent =
            "Les statistiques complémentaires ne sont pas disponibles pour le moment.";

        console.error(erreur);
    }
}


function initialiserDates() {
    const aujourdHui = new Date();
    const annee = aujourdHui.getFullYear();
    const mois = String(aujourdHui.getMonth() + 1).padStart(2, "0");
    const jour = String(aujourdHui.getDate()).padStart(2, "0");
    const dateLocale = `${annee}-${mois}-${jour}`;

    const dateVisite = document.getElementById("date_souhaitee");

    if (dateVisite && !dateVisite.min) {
        dateVisite.min = dateLocale;
    }

    const datePaiement = document.getElementById("date_paiement");

    if (datePaiement) {
        datePaiement.max = dateLocale;
    }

    const dateEntree = document.getElementById("date_entree");

    if (dateEntree) {
        dateEntree.max = dateLocale;
    }
}