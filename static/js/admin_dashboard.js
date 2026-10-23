"use strict";

document.addEventListener("DOMContentLoaded", initialiserDashboard);

async function initialiserDashboard() {
    const message = document.getElementById("dashboard-message");
    const kpiTaux = document.getElementById("kpi-taux-occupation");

    if (!message) {
        return;
    }

    if (typeof Chart === "undefined") {
        message.textContent =
            "Les graphiques ne peuvent pas être chargés. Vérifiez votre connexion Internet.";
        return;
    }

    try {
        const reponse = await fetch("/api/statistiques");

        if (!reponse.ok) {
            throw new Error("La récupération des statistiques a échoué.");
        }

        const donnees = await reponse.json();

        if (kpiTaux) {
            kpiTaux.textContent =
                `${donnees.taux_occupation_pourcent} %`;
        }

        const nombreLogements =
            donnees.disponibilite.disponibles +
            donnees.disponibilite.loues;

        if (nombreLogements === 0) {
            message.textContent =
                "Ajoutez des logements pour commencer à visualiser les statistiques.";
        } else {
            message.remove();
        }

        const formatNombre = (valeur) =>
            Number(valeur || 0).toLocaleString("fr-FR");

        const couleurs = {
            vert: "#28543d",
            vertClair: "#789b7b",
            or: "#b59b58",
            beige: "#d9c9a5",
            ivoire: "#f3eee2",
            gris: "#a9b2a8"
        };

        const couleursGraphiques = [
            couleurs.vert,
            couleurs.or,
            couleurs.vertClair,
            couleurs.beige,
            couleurs.gris,
            "#526e60",
            "#d6b66d"
        ];

        Chart.defaults.font.family = "Arial, sans-serif";
        Chart.defaults.color = "#526257";

        // 1. Disponibilité des logements
        new Chart(
            document.getElementById("graphique-disponibilite"),
            {
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
                        borderWidth: 4,
                        hoverOffset: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "62%",
                    plugins: {
                        legend: {
                            position: "bottom"
                        },
                        tooltip: {
                            callbacks: {
                                label: (contexte) =>
                                    `${contexte.label} : ${formatNombre(contexte.raw)}`
                            }
                        }
                    }
                }
            }
        );

        // 2. Nombre de logements par type
        new Chart(
            document.getElementById("graphique-types"),
            {
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
                        borderRadius: 7,
                        maxBarThickness: 52
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
        );

        // 3. Demandes de visite par statut
        const libellesStatuts = {
            "nouvelle": "Nouvelle",
            "confirmée": "Confirmée",
            "effectuée": "Effectuée"
        };

        new Chart(
            document.getElementById("graphique-demandes"),
            {
                type: "doughnut",
                data: {
                    labels: donnees.demandes_par_statut.map(
                        ligne => libellesStatuts[ligne.statut] || ligne.statut
                    ),
                    datasets: [{
                        data: donnees.demandes_par_statut.map(
                            ligne => ligne.nombre
                        ),
                        backgroundColor: couleursGraphiques,
                        borderColor: "#fffdf8",
                        borderWidth: 4,
                        hoverOffset: 8
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
        );

        // 4. Revenus mensuels sur six mois
        new Chart(
            document.getElementById("graphique-revenus"),
            {
                type: "line",
                data: {
                    labels: donnees.revenus_par_mois.mois,
                    datasets: [{
                        label: "Revenus en FCFA",
                        data: donnees.revenus_par_mois.revenus,
                        borderColor: couleurs.vert,
                        backgroundColor: "rgba(40, 84, 61, 0.12)",
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointHoverRadius: 7
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
        );

        // 5. Loyer moyen par quartier
        new Chart(
            document.getElementById("graphique-quartiers"),
            {
                type: "bar",
                data: {
                    labels: donnees.loyers_moyens_par_quartier.map(
                        ligne => ligne.quartier
                    ),
                    datasets: [{
                        label: "Loyer moyen (FCFA)",
                        data: donnees.loyers_moyens_par_quartier.map(
                            ligne => ligne.loyer_moyen
                        ),
                        backgroundColor: couleurs.vertClair,
                        borderRadius: 7,
                        maxBarThickness: 42
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
        );

    } catch (erreur) {
        message.textContent =
            "Impossible de charger les graphiques. Vérifiez que le serveur Flask fonctionne.";
        console.error(erreur);
    }
}