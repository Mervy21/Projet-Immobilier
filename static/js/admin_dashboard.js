"use strict";

document.addEventListener("DOMContentLoaded", initialiserDashboard);

async function initialiserDashboard() {
    const message = document.getElementById("dashboard-message");
    const kpiTaux = document.getElementById("kpi-taux-occupation");
    const blocDetaille = document.getElementById("bloc-statistiques-detaillees");

    if (!message) {
        return;
    }

    const formatNombre = (valeur) =>
        Number(valeur || 0).toLocaleString("fr-FR");

    const couleurs = {
        vert: "#28543d",
        vertClair: "#789b7b",
        or: "#b59b58",
        beige: "#d9c9a5",
        gris: "#a9b2a8"
    };

    try {
        if (typeof Chart === "undefined") {
            throw new Error(
                "Chart.js n'est pas chargé. Vérifiez la connexion Internet."
            );
        }

        const reponse = await fetch("/api/statistiques", {
            headers: {
                "Accept": "application/json"
            }
        });

        if (!reponse.ok) {
            throw new Error(
                `L'API statistiques a répondu avec le statut ${reponse.status}.`
            );
        }

        const donnees = await reponse.json();

        if (!donnees.disponibilite) {
            throw new Error("Les données de disponibilité sont absentes.");
        }

        if (kpiTaux) {
            kpiTaux.textContent =
                `${formatNombre(donnees.taux_occupation_pourcent)} %`;
        }

        message.textContent = "Statistiques chargées.";

        const donneesGraphiques = [
            {
                id: "graphique-disponibilite",
                configuration: {
                    type: "doughnut",
                    data: {
                        labels: ["Disponibles", "Loués"],
                        datasets: [{
                            data: [
                                donnees.disponibilite.disponibles,
                                donnees.disponibilite.loues
                            ],
                            backgroundColor: [
                                couleurs.vert,
                                couleurs.or
                            ],
                            borderColor: "#fffdf8",
                            borderWidth: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: "62%",
                        plugins: {
                            legend: {
                                position: "bottom"
                            }
                        }
                    }
                }
            },
            {
                id: "graphique-types",
                configuration: {
                    type: "bar",
                    data: {
                        labels: donnees.logements_par_type.map(
                            ligne => ligne.type
                        ),
                        datasets: [{
                            label: "Nombre de logements",
                            data: donnees.logements_par_type.map(
                                ligne => ligne.nombre
                            ),
                            backgroundColor: couleurs.vert,
                            borderRadius: 7
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    precision: 0
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                }
            },
            {
                id: "graphique-demandes",
                configuration: {
                    type: "doughnut",
                    data: {
                        labels: donnees.demandes_par_statut.map(
                            ligne => ligne.statut
                        ),
                        datasets: [{
                            data: donnees.demandes_par_statut.map(
                                ligne => ligne.nombre
                            ),
                            backgroundColor: [
                                couleurs.vert,
                                couleurs.or,
                                couleurs.vertClair,
                                couleurs.beige,
                                couleurs.gris
                            ],
                            borderColor: "#fffdf8",
                            borderWidth: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: "bottom"
                            }
                        }
                    }
                }
            },
            {
                id: "graphique-revenus",
                configuration: {
                    type: "line",
                    data: {
                        labels: donnees.revenus_par_mois.mois,
                        datasets: [{
                            label: "Revenus en FCFA",
                            data: donnees.revenus_par_mois.revenus,
                            borderColor: couleurs.vert,
                            backgroundColor: "rgba(40, 84, 61, 0.12)",
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: valeur => formatNombre(valeur)
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: contexte =>
                                        `${formatNombre(contexte.raw)} FCFA`
                                }
                            }
                        }
                    }
                }
            },
            {
                id: "graphique-quartiers",
                configuration: {
                    type: "bar",
                    data: {
                        labels: donnees.loyers_moyens_par_quartier.map(
                            ligne => ligne.quartier
                        ),
                        datasets: [{
                            label: "Loyer moyen en FCFA",
                            data: donnees.loyers_moyens_par_quartier.map(
                                ligne => ligne.loyer_moyen
                            ),
                            backgroundColor: couleurs.vertClair,
                            borderRadius: 7
                        }]
                    },
                    options: {
                        indexAxis: "y",
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                beginAtZero: true,
                                ticks: {
                                    callback: valeur => formatNombre(valeur)
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: contexte =>
                                        `${formatNombre(contexte.raw)} FCFA / mois`
                                }
                            }
                        }
                    }
                }
            }
        ];

        Chart.defaults.font.family = "Arial, sans-serif";
        Chart.defaults.color = "#526257";

        for (const graphique of donneesGraphiques) {
            const canvas = document.getElementById(graphique.id);

            if (!canvas) {
                console.warn(
                    `Le canvas ${graphique.id} est absent du template.`
                );
                continue;
            }

            const graphiqueExistant = Chart.getChart(canvas);

            if (graphiqueExistant) {
                graphiqueExistant.destroy();
            }

            new Chart(canvas, graphique.configuration);
        }

        message.remove();

        if (blocDetaille) {
            afficherStatistiquesDetaillees(blocDetaille, donnees);
        }

    } catch (erreur) {
        message.textContent =
            "Impossible de charger les graphiques. Vérifiez le chargement de Chart.js et l'accès à l'API.";

        if (blocDetaille) {
            blocDetaille.replaceChildren();

            const paragraphe = document.createElement("p");
            paragraphe.textContent =
                "Les statistiques complémentaires sont momentanément indisponibles.";

            blocDetaille.appendChild(paragraphe);
        }

        console.error("Erreur du tableau de bord NESTY :", erreur);
    }
}

function afficherStatistiquesDetaillees(conteneur, donnees) {
    const formatNombre = (valeur) =>
        Number(valeur || 0).toLocaleString("fr-FR");

    conteneur.replaceChildren();

    ajouterTitre(conteneur, "Revenus du mois");
    ajouterParagraphe(
        conteneur,
        `${formatNombre(donnees.revenus_du_mois)} FCFA en ${donnees.mois_actuel}.`
    );

    ajouterTitre(conteneur, "Loyers moyens par type");

    const listeTypes = document.createElement("ul");

    for (const ligne of donnees.loyers_moyens_par_type) {
        const element = document.createElement("li");

        element.textContent =
            `${ligne.type} : ${formatNombre(ligne.loyer_moyen)} FCFA / mois`;

        listeTypes.appendChild(element);
    }

    conteneur.appendChild(listeTypes);

    ajouterTitre(conteneur, "Locations sans paiement du mois");

    const impayes = donnees.locations_impayees_ce_mois || [];

    if (impayes.length === 0) {
        ajouterParagraphe(
            conteneur,
            "Aucune location impayée signalée pour ce mois."
        );
        return;
    }

    const listeImpayes = document.createElement("ul");

    for (const location of impayes) {
        const element = document.createElement("li");

        element.textContent =
            `${location.nom_locataire} — ${location.titre_bien} ` +
            `(${location.quartier}) : ${formatNombre(location.loyer_convenu)} FCFA`;

        listeImpayes.appendChild(element);
    }

    conteneur.appendChild(listeImpayes);
}

function ajouterTitre(conteneur, texte) {
    const titre = document.createElement("h3");
    titre.textContent = texte;
    conteneur.appendChild(titre);
}

function ajouterParagraphe(conteneur, texte) {
    const paragraphe = document.createElement("p");
    paragraphe.textContent = texte;
    conteneur.appendChild(paragraphe);
}