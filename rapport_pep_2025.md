# Calcul détaillé des périodes-élèves pondérées (PEP) — année civile 2025

> Établissement 3052 — calcul reproduit par pyetnic (lecture seule, prod) selon la spec
> `specs/21_calcul_encadrement_dotation.md` (décret 16/04/1991 art. 99 + arrêté GCF 22/11/2002 art. 3-4).
> Généré le 2026-06-11 (session 9ter).

## Méthode et intrants

- **Assiette civile 2025** = périodes **réelles An2** des Doc 2 de 2024-2025 + périodes **réelles An1** des Doc 2 de 2025-2026 (207 organisations lues).
- **PE** = périodes réelles × `nbEleveC1` (élèves du Doc 2, comptage 1ᵉʳ dixième).
- **Coefficient pédagogique** par `coCategorie` : `referentiels/coefficients_ponderation_coCategorie.csv`.
- **Coefficient de niveau** dérivé du `codeFormation` (segment `Uxx`) : U1x → B (1,0), U2x → A (1,25), U3x → C (1,5).
- **Part d'autonomie** (`Auto`) : répartie au prorata des périodes des cas généraux **du dossier pédagogique** (`nbPeriodeBranche`, hérite leurs coefficients) — base indispensable pour les organisations sur deux années scolaires, où l'autonomie peut tomber dans une année civile sans cours généraux (ex. 510/org1 2024-2025 : 58 pér. CTln en 2024, 24 pér. d'autonomie en 2025).
- **Limitation organique** : les périodes réelles du Doc 2 sont supposées ne couvrir que la part dotation (constat session 9ter : `réelles = prévues − IE` sur les UE mixtes) ; les UE 100 % IE ont des réelles nulles et ne contribuent pas.
- **Cas particuliers** (encadrement, EPT, suivi) : périodes × moyenne PEP/période de l'établissement (étape 4 de l'arrêté).

## Synthèse

| Grandeur | Valeur |
|---|---:|
| PE non pondérées (cas généraux + autonomie) | 54,409.5 |
| Périodes organiques (cas généraux + autonomie) | 4,913.5 |
| PEP cas généraux | 73,104.30 |
| PEP part d'autonomie | 17,312.29 |
| **Moyenne PEP/période** | **18.402** |
| PEP cas particuliers (639 pér. × moyenne) | 11,758.67 |
| **PEP TOTAL établissement — année civile 2025** | **102,175.26** |

## Détail par UE — cas généraux + autonomie

| Année scol. | UE/org | Niv. | Pér. 2025 | PE | PEP | IE |
|---|---|---|---:|---:|---:|---|
| 2024-2025 | 312/1 — BASES DE LA SOUDURE T.I.G. | A | 120 | 1560 | 4875.0 |  |
| 2024-2025 | 519/1 — SOUDURE SEMI-AUTOMATIQUE : NIVEAU 2 | A | 150 | 1350 | 4320.0 |  |
| 2024-2025 | 408/1 — INFORMATIQUE:GESTIONNAIRE DE BASE DE DONNEES-NIV | A | 80 | 1600 | 3200.0 |  |
| 2024-2025 | 455/1 — CONNAISSANCES DE GESTION DE BASE | A | 122 | 2074 | 2592.5 |  |
| 2024-2025 | 511/2 — INFORMATIQUE : MAINTENANCE SOFTWARE | A | 76 | 1216 | 2432.0 |  |
| 2024-2025 | 561/1 — APPROCHE CONCEPTUELLE METIERS AIDE & SOINS AUX P | A | 140 | 1260 | 2266.9 |  |
| 2024-2025 | 528/4 — LANGUE : FRANCAIS UF 1 - NIVEAU ELEMENTAIRE | B | 120 | 2160 | 2160.0 |  |
| 2024-2025 | 455/2 — CONNAISSANCES DE GESTION DE BASE | A | 157 | 1570 | 1962.5 |  |
| 2025-2026 | 523/1 — BASES DE SOUDAGE ET DU COUPAGE OXYACETYLENIQUES | B | 80 | 800 | 1880.0 |  |
| 2024-2025 | 565/2 — AIDE-SOIGNANT : APPROCHE CONCEPTUELLE | A | 160 | 1440 | 1800.0 |  |
| 2024-2025 | 564/1 — AIDE-SOIGNANT : METHODOLOGIE APPLIQUEE | A | 178 | 1068 | 1681.5 |  |
| 2024-2025 | 591/1 — UTILISATION D'UN SMARTPHONE | A | 40 | 840 | 1680.0 |  |
| 2025-2026 | 556/1 — DECOUVERTE DES METIERS DE L'AIDE ET DES SOINS AU | A | 24 | 816 | 1632.0 |  |
| 2024-2025 | 405/2 — INFORMATIQUE:EDITION ASSISTEE PAR ORDINATEUR-NIV | A | 40 | 800 | 1600.0 |  |
| 2024-2025 | 406/2 — INFORMATIQUE : TABLEUR -NIVEAU ELEMENTAIRE | A | 40 | 800 | 1600.0 |  |
| 2024-2025 | 407/1 — INFORMATIQUE:PRESENTATION ASSISTEE PAR ORD-NIVEA | A | 40 | 800 | 1600.0 |  |
| 2024-2025 | 522/1 — SOUDURE A L'ARC AVEC ELECTRODE ENROBEE : NIVEAU  | B | 46 | 598 | 1534.0 |  |
| 2024-2025 | 482/1 — LANGUE : ANGLAIS UF 1 - NIVEAU ELEMENTAIRE | B | 84 | 1512 | 1512.0 |  |
| 2025-2026 | 564/1 — AIDE-SOIGNANT : METHODOLOGIE APPLIQUEE | A | 106 | 954 | 1503.0 |  |
| 2024-2025 | 403/3 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'EXPLOITATION | A | 40 | 720 | 1440.0 |  |
| 2024-2025 | 528/2 — LANGUE : FRANCAIS UF 1 - NIVEAU ELEMENTAIRE | B | 120 | 1440 | 1440.0 |  |
| 2024-2025 | 537/1 — PROGRAMMATION : NIVEAU 1 | A | 88 | 704 | 1408.0 |  |
| 2024-2025 | 528/3 — LANGUE : FRANCAIS UF 1 - NIVEAU ELEMENTAIRE | B | 120 | 1320 | 1320.0 |  |
| 2025-2026 | 511/2 — INFORMATIQUE : MAINTENANCE SOFTWARE | A | 72 | 648 | 1296.0 |  |
| 2025-2026 | 549/1 — AIDE-SOIGNANT:ACTUAL DES ACT INFIRM DELEG:ASP TH | A | 48 | 768 | 1248.0 |  |
| 2024-2025 | 492/2 — LANGUE FRANCAIS - UF 3 - NIVEAU INTERMEDIAIRE | A | 120 | 960 | 1200.0 |  |
| 2024-2025 | 588/1 — INITIATION A L'ANGLAIS INFORMATIQUE - UE1 | B | 60 | 1140 | 1140.0 |  |
| 2025-2026 | 528/3 — LANGUE : FRANCAIS UF 1 - NIVEAU ELEMENTAIRE | B | 76 | 1140 | 1140.0 |  |
| 2024-2025 | 405/4 — INFORMATIQUE:EDITION ASSISTEE PAR ORDINATEUR-NIV | A | 40 | 560 | 1120.0 |  |
| 2024-2025 | 523/1 — BASES DE SOUDAGE ET DU COUPAGE OXYACETYLENIQUES | B | 48 | 528 | 1102.2 |  |
| 2024-2025 | 483/1 — LANGUE : ANGLAIS UF 2 - NIVEAU ELEMENTAIRE | B | 84 | 1092 | 1092.0 |  |
| 2025-2026 | 326/1 — COMMUNICAT°:EXPRESS° OR & ECRITE APPLIQUEE AU SE | A | 68 | 544 | 1088.0 |  |
| 2024-2025 | 557/1 — COMMUNICATION:EXPR OR & EXRITE APP AU SECT DU SE | A | 60 | 540 | 1080.0 |  |
| 2024-2025 | 406/1 — INFORMATIQUE : TABLEUR -NIVEAU ELEMENTAIRE | A | 40 | 520 | 1040.0 |  |
| 2024-2025 | 497/1 — INFORMATIQUE : RESEAUX - INTERNET/INTRANET | A | 40 | 520 | 1040.0 |  |
| 2025-2026 | 524/1 — SOUDURE SEMI-AUTOMATIQUE : NIVEAU 1 | B | 46 | 552 | 1027.2 |  |
| 2025-2026 | 510/1 — INFORMATIQUE : MAINTENANCE HARDWARE | A | 64 | 512 | 1024.0 |  |
| 2025-2026 | 511/1 — INFORMATIQUE : MAINTENANCE SOFTWARE | A | 30 | 510 | 1020.0 |  |
| 2024-2025 | 403/1 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'EXPLOITATION | A | 24 | 504 | 1008.0 |  |
| 2024-2025 | 549/1 — AIDE-SOIGNANT:ACTUAL DES ACT INFIRM DELEG:ASP TH | A | 34 | 544 | 992.0 |  |
| 2024-2025 | 500/1 — INFORMATIQUE : TECHNOLOGIE DES RESEAUX | A | 40 | 480 | 960.0 |  |
| 2024-2025 | 403/2 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'EXPLOITATION | A | 24 | 480 | 960.0 |  |
| 2024-2025 | 596/1 — POSE DE SYSTEMES D'EGOUTTAGE ET DE DRAINAGE PERI | B | 50 | 450 | 936.0 |  |
| 2025-2026 | 528/2 — LANGUE : FRANCAIS UF 1 - NIVEAU ELEMENTAIRE | B | 116 | 928 | 928.0 |  |
| 2025-2026 | 537/1 — PROGRAMMATION : NIVEAU 1 | A | 34 | 442 | 884.0 | K |
| 2024-2025 | 328/5 — INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE | A | 20 | 400 | 800.0 |  |
| 2024-2025 | 405/3 — INFORMATIQUE:EDITION ASSISTEE PAR ORDINATEUR-NIV | A | 40 | 400 | 800.0 |  |
| 2024-2025 | 492/1 — LANGUE FRANCAIS - UF 3 - NIVEAU INTERMEDIAIRE | A | 120 | 600 | 750.0 |  |
| 2025-2026 | 522/1 — SOUDURE A L'ARC AVEC ELECTRODE ENROBEE : NIVEAU  | B | 42 | 420 | 744.0 |  |
| 2024-2025 | 326/2 — COMMUNICAT°:EXPRESS° OR & ECRITE APPLIQUEE AU SE | A | 44 | 352 | 704.0 |  |
| 2024-2025 | 510/2 — INFORMATIQUE : MAINTENANCE HARDWARE | A | 44 | 352 | 704.0 |  |
| 2024-2025 | 510/1 — INFORMATIQUE : MAINTENANCE HARDWARE | A | 24 | 336 | 672.0 |  |
| 2025-2026 | 492/1 — LANGUE FRANCAIS - UF 3 - NIVEAU INTERMEDIAIRE | A | 76 | 532 | 665.0 |  |
| 2024-2025 | 157/2 — ESS - METHODES DE TRAVAIL | A | 40 | 320 | 640.0 |  |
| 2025-2026 | 328/3 — INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE | A | 20 | 320 | 640.0 |  |
| 2024-2025 | 524/1 — SOUDURE SEMI-AUTOMATIQUE : NIVEAU 1 | B | 34 | 306 | 617.0 |  |
| 2025-2026 | 483/1 — LANGUE : ANGLAIS UF 2 - NIVEAU ELEMENTAIRE | B | 44 | 616 | 616.0 |  |
| 2024-2025 | 498/1 — INFORMATIQUE : INTRODUCTION A LA TECHNOLOGIE DES | A | 40 | 480 | 600.0 |  |
| 2025-2026 | 328/4 — INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE | A | 20 | 300 | 600.0 |  |
| 2024-2025 | 511/4 — INFORMATIQUE : MAINTENANCE SOFTWARE | A | 32 | 288 | 576.0 |  |
| 2024-2025 | 499/1 — INFORMATIQUE : SYSTEME D'EXPLOITATION | A | 40 | 280 | 560.0 |  |
| 2025-2026 | 455/1 — CONNAISSANCES DE GESTION DE BASE | A | 80 | 400 | 500.0 |  |
| 2024-2025 | 501/1 — INFORMATIQUE : UTILITAIRES COMPLEMENTAIRES AU SY | A | 40 | 240 | 480.0 |  |
| 2024-2025 | 490/2 — LANGUE : FRANCAIS UF 2 - NIVEAU ELEMENTAIRE | B | 120 | 480 | 480.0 |  |
| 2024-2025 | 395/1 — REV GEN BAR:FORM COMPL ACCES ECHEL D4 OUV QUAL D | B | 15 | 450 | 450.0 | C |
| 2024-2025 | 511/1 — INFORMATIQUE : MAINTENANCE SOFTWARE | A | 16 | 224 | 448.0 |  |
| 2025-2026 | 523/2 — BASES DE SOUDAGE ET DU COUPAGE OXYACETYLENIQUES | B | 28 | 252 | 446.4 |  |
| 2024-2025 | 565/1 — AIDE-SOIGNANT : APPROCHE CONCEPTUELLE | A | 84 | 336 | 420.0 |  |
| 2025-2026 | 328/2 — INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE | A | 20 | 200 | 400.0 |  |
| 2024-2025 | 327/2 — MATHEMATIQUES APPLIQUEES | A | 44 | 308 | 385.0 |  |
| 2025-2026 | 403/3 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'EXPLOITATION | A | 12 | 192 | 384.0 |  |
| 2024-2025 | 328/4 — INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE | A | 20 | 180 | 360.0 |  |
| 2025-2026 | 403/2 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'EXPLOITATION | A | 12 | 180 | 360.0 |  |
| 2024-2025 | 593/1 — CESS : FRANCAIS - NIVEAU 1 | A | 40 | 280 | 350.0 |  |
| 2025-2026 | 328/1 — INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE | A | 20 | 160 | 320.0 |  |
| 2025-2026 | 402/2 — MATHEMATIQUES APPLIQUEES A L'INFORMATIQUE | A | 36 | 252 | 315.0 |  |
| 2025-2026 | 589/1 — INITIATION A L'ANGLAIS INFORMATIQUE - UE2 | B | 32 | 288 | 288.0 |  |
| 2025-2026 | 482/1 — LANGUE : ANGLAIS UF 1 - NIVEAU ELEMENTAIRE | B | 40 | 280 | 280.0 |  |
| 2025-2026 | 157/1 — ESS - METHODES DE TRAVAIL | A | 16 | 128 | 256.0 |  |
| 2025-2026 | 406/1 — INFORMATIQUE : TABLEUR -NIVEAU ELEMENTAIRE | A | 16 | 128 | 256.0 |  |
| 2024-2025 | 396/1 — REV GEN BAR:FORM COMPL ACCES ECHEL D4 OUV QUAL D | B | 8 | 248 | 248.0 | C |
| 2025-2026 | 405/1 — INFORMATIQUE:EDITION ASSISTEE PAR ORDINATEUR-NIV | A | 16 | 112 | 224.0 |  |
| 2024-2025 | 589/2 — INITIATION A L'ANGLAIS INFORMATIQUE - UE2 | B | 24 | 216 | 216.0 |  |
| 2024-2025 | 563/1 — INITIATION AUX PREMIERS SECOURS | A | 20 | 100 | 200.0 |  |
| 2025-2026 | 563/1 — INITIATION AUX PREMIERS SECOURS | A | 20 | 100 | 200.0 |  |
| 2024-2025 | 402/1 — MATHEMATIQUES APPLIQUEES A L'INFORMATIQUE | A | 16 | 144 | 180.0 |  |
| 2025-2026 | 396/1 — REV GEN BAR:FORM COMPL ACCES ECHEL D4 OUV QUAL D | B | 10 | 150 | 150.0 | C |
| 2024-2025 | 570/1 — INTRO A LA SECU & A L'HYGIENE METIERS PARACHEV D | B | 12 | 108 | 108.0 |  |
| 2025-2026 | 327/1 — MATHEMATIQUES APPLIQUEES | A | 12 | 84 | 105.0 |  |
| 2024-2025 | 568/1 — FORM CONT AG TECH DES ADM LOC & REG-SEC SPEC A L | A | 10.5 | 73.5 | 91.9 | C |
| 2025-2026 | 568/1 — FORM CONT AG TECH DES ADM LOC & REG-SEC SPEC A L | A | 5 | 50 | 62.5 | C |

## Cas particuliers — valorisés à la moyenne PEP/période

Moyenne PEP/période = 18.402

| Année scol. | UE/org | Cat. | Pér. 2025 | PEP | Activité |
|---|---|---|---:|---:|---|
| 2025-2026 | 402/1 — MATHEMATIQUES APPLIQUEES A L'INFORM | ExPT | 40 | 736.1 | EXPERTISE PEDAGOGIQUE ET TECHNIQUE |
| 2025-2026 | 403/1 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'E | ExPT | 1 | 18.4 | EXPERTISE PEDAGOGIQUE ET TECHNIQUE |
| 2024-2025 | 403/5 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'E | ExPT | 179 | 3293.9 | EXPERTISE PEDAGOGIQUE ET TECHNIQUE |
| 2024-2025 | 403/6 — INFORMATIQUE:LOGICIEL GRAPHIQUE D'E | ExPT | 99 | 1821.8 | EXPERTISE PEDAGOGIQUE ET TECHNIQUE |
| 2024-2025 | 512/1 — STAGE : TECHNICIEN EN INFORMATIQUE | CTen | 39 | 717.7 | ENCADREMENT DU STAGE DU TECHNICIEN EN IN |
| 2025-2026 | 512/1 — STAGE : TECHNICIEN EN INFORMATIQUE | CTen | 4 | 73.6 | ENCADREMENT DU STAGE DU TECHNICIEN EN IN |
| 2024-2025 | 513/1 — EPREUVE INTEGREE DE LA SECTION: "TE | CTen | 15 | 276.0 | PREPA EI SECTION "TECHNICIEN EN INFORMAT |
| 2024-2025 | 513/1 — EPREUVE INTEGREE DE LA SECTION: "TE | CTen | 4 | 73.6 | EI SECTION "TECHNICIEN EN INFORMATIQUE" |
| 2024-2025 | 550/1 — AIDE-SOIGNANT:ACTUAL DES ACT INFIRM | PPen | 20 | 368.0 | A-I:ACTU ACT INFIR DEL:ENCADREMENT DU ST |
| 2024-2025 | 550/1 — AIDE-SOIGNANT:ACTUAL DES ACT INFIRM | PPen | 12 | 220.8 | A-I:ACTU ACT INFIR DEL:ENCADREMENT DE LA |
| 2024-2025 | 560/1 — STAGE D'OBSERVATION METIERS DE L'AI | PPen | 59 | 1085.7 | ENCADREMENT STAGE D'OBSERVATION METIERS  |
| 2025-2026 | 560/1 — STAGE D'OBSERVATION METIERS DE L'AI | PPen | 4 | 73.6 | ENCADREMENT STAGE D'OBSERVATION METIERS  |
| 2024-2025 | 562/1 — STAGE D'INSERTION METIERS DE L'AIDE | PPen | 60 | 1104.1 | ENCADREMENT STAGE D'INSERTION |
| 2025-2026 | 566/1 — AIDE-SOIGNANT : STAGE D'INTEGRATION | PPen | 12 | 220.8 | AIDE-SOIGNANT : ATELIER DE PRATIQUE REFL |
| 2024-2025 | 566/2 — AIDE-SOIGNANT : STAGE D'INTEGRATION | PPen | 40 | 736.1 | AIDE-SOIGNANT : STAGE D'INTEGRATION:ENCA |
| 2025-2026 | 566/2 — AIDE-SOIGNANT : STAGE D'INTEGRATION | PPen | 4 | 73.6 | AIDE-SOIGNANT : STAGE D'INTEGRATION:ENCA |
| 2024-2025 | 567/1 — EPREUVE INTEGREE DE LA SECTION : "A | CTen | 19 | 349.6 | PREPARATION EI |
| 2024-2025 | 567/1 — EPREUVE INTEGREE DE LA SECTION : "A | CTen | 4 | 73.6 | EI DE LA SECTION:"AIDE-SOIGNANT" |
| 2024-2025 | 608/1 — AIDE FAMILIAL : STAGE D'INTEGRATION | PPen | 4 | 73.6 | ENCADREMENT DE STAGE |
| 2025-2026 | 608/1 — AIDE FAMILIAL : STAGE D'INTEGRATION | PPen | 16 | 294.4 | ENCADREMENT DE STAGE |
| 2025-2026 | 608/1 — AIDE FAMILIAL : STAGE D'INTEGRATION | SEtu | 4 | 73.6 | ADMISSION, SUIVI PEDAGOGIQUE ET SANCTION |

## Confrontation aux chiffres officiels (HOD/CICS, écrans 57L/57D — 11/06/2026)

L'utilisateur a extrait du système hôte (transaction `MENP052`, écrans `PMM5DM1` 57L « Liste des
périodes-élèves » et `PMM5EM1` 57D « Détail périodes-élèves par école », établissement **9017001**
EICA Auvelais) les **PE officielles (encadrement)** par année civile :

| An. civ. | PE élèves (officiel) | dont chef d'atelier | Emplois calculés (new) |
|---:|---:|---:|---|
| 2018 | 90 270 | 20 647 | — |
| 2019 | 90 349 | 21 435 | — |
| 2020 | 95 100 | 21 815 | — |
| 2021 | 78 238 | 18 629 | — |
| 2022 | 79 785 | 19 538 | — |
| 2023 | 77 878 | 18 692 | — |
| 2024 | 106 369 | 22 886 | dir. 1,00 · surv. 1,50 |
| **2025** | **99 748** | **18 526** | dir. 1,00 · surv. 1,50 |
| 2026 (partiel) | 28 204 | 7 970 | — |

⚠️ **PE ≠ PEP** : ces 99 748 PE (encadrement) ne sont pas comparables aux 102 175 PEP du présent
rapport (proximité fortuite). La bonne comparaison est avec une **reconstruction des PE encadrement** :
PE organiques toutes catégories (57 772,5) + cas particuliers à la moyenne PE/période (≈ 3 521) +
**interventions extérieures** (≈ 28 895, élèves estimés par le max des lignes d'activité) ≈ **90 189 PE**,
soit 90,4 % du chiffre officiel dans cette première approche. L'écart a été **localisé puis expliqué**
(précision utilisateur) : **11 organisations VC/convention** (455 « Connaissances de gestion » VC ×5,
528/1 FLE, 403/7, 510/2 et 4, 546/1) portent **1 005 périodes IE 2025 sans aucun élève** — ni lignes
d'activité Doc 2, ni population Doc 1, ni inscriptions SEPS (tous vérifiés ; la recherche SEPS
fonctionne par ailleurs : 490/1 → 7 inscriptions ✓). Ce sont des activités de type **EPT (expertise
pédagogique et technique)** prestées sous convention/VC : **l'absence d'élèves y est normale**, et
ces périodes se valorisent comme les cas particuliers, à la **moyenne PE/période** de l'établissement
(même logique que l'étape 4 de l'arrêté côté PEP).

**Reconstruction corrigée** : PE lignes avec élèves (57 772,5) + IE avec élèves (28 895,5) +
(319 pér. réservées organiques + 1 005 pér. EPT) × moyenne PE/période :

| Variante de moyenne | Moyenne | Total PE | vs officiel 99 748 |
|---|---:|---:|---:|
| organique (PE org / pér. org) | 11,039 | 101 284 | +1,54 % |
| globale (PE org+IE / pér. org+IE) | 10,634 | **100 748** | **+1,00 %** |

Résidu de ~1 % attribuable aux exclusions DI non payés (majorant connu), aux arrondis officiels et à
la définition exacte de la moyenne (assiette, arrondi 2ᵉ décimale).

## Validation officielle — écran 55L (dotations / PEP, HOD 11/06/2026)

Second extrait utilisateur : transaction `MENP052`, écran **55L** (`PMM5BM1`, « Liste dotations
périodes par an. civile ») — c'est l'écran « pot K » : dotation organique + **PEP officielles** :

| An. civ. | Dot. initiale | Dot. utilisable | Solde | PEP référence | PEP calculée | % |
|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 6 772 | 6 348 | 4 | 128 235 | 126 658 | −1,23 |
| 2019 | 6 772 | 6 338 | −20 | 128 235 | 115 089 | −10,25 |
| 2020 | 6 772 | 6 327 | −10 | 115 084 | 126 821 | +10,20 |
| 2021 | 6 598 | 6 150 | 1 | 117 340 | 98 586 | −15,98 |
| 2022 | 6 598 | 6 169 | — | 98 586 | 92 447 | −6,23 |
| 2023 | 6 598 | 6 440 | −12 | 98 586 | 95 307 | −3,33 |
| 2024 | 6 598 | 7 210 | 3 | 98 586 | 108 214 | +9,77 |
| **2025** | 6 598 | 6 572 | −4 | 98 635 | **101 710** | **+3,12** |
| 2026 | 6 601 | 6 595 | 4 782 | — | 30 111 (partiel) | — |

🎯 **PEP calculée officielle 2025 = 101 710 vs 102 175,26 pyetnic → écart +0,46 %** (+465 PEP).
Candidats pour le résidu : élèves DI non payés non exclus (majorant connu), arrondis officiels
(2ᵉ décimale par étape), valorisation fine des cas particuliers.

**Mécanismes vérifiés sur la série** (calculs exacts) :
- `% = (calculée − référence) / référence` — exact sur les 8 années.
- **Décalage N → N+2** : PEP calculées de l'année N ajustent la dotation de N+2 (« avant-dernière
  année civile », arrêté art. 2) — ex. calc 2019 (−10,25 %) → baisse dotation 2021.
- **Baisse = ¼ × dotation × |%|** : ¼ × 6 772 × 10,25 % = 173,5 ≈ 174 périodes retirées (6 772 → 6 598).
  ⚠️ **Le plafond de 50 périodes (arrêté art. 6) n'a pas été appliqué** — à clarifier (version de
  l'arrêté applicable en 2021 ?).
- **Neutralisation ±8 %** observée : 2022 (−6,23), 2023 (−3,33), 2025 (+3,12) → dotation inchangée.
- **Hausse** : calc 2024 (+9,77 %) → dotation 2026 = 6 601 (+3 seulement — redistribution limitée au
  disponible, enveloppe fermée).
- **Référence re-proratisée à la dotation** après ajustement : 98 586 × 6 601/6 598 = 98 631 ≈ 98 635.

→ **Prévision dotation 2027** : calc 2025 = +3,12 % (dans ±8 %) → dotation inchangée (≈ 6 601).

## Réconciliation de l'assiette — rapport 4 « Doc2 : périodes organiques » (ppm_1614, éd. 2425 + 2526)

Assiette organique officielle de l'année civile 2025 : **4 126,5** pér. réelles (col. « réel 25 »,
édition 2425) + **1 426,0** (édition 2526) = **5 552,5 périodes organiques**. Décomposition exacte :
**4 913,5** pér. de cas généraux + autonomie et **639** pér. de cas particuliers — soit, **à la période
près**, l'assiette du présent rapport. La couche d'entrée du calcul PEP est donc validée à 100 % ;
le résidu de +0,46 % sur les PEP relève de la pondération/des arrondis officiels, pas de l'assiette.
(Le rapport 4 ne contient pas le bloc des interventions extérieures : « périodes organiques » =
lignes d'activité du Doc 2, ce qui confirme définitivement l'hypothèse « réelles = part dotation ».)

**Assiette IE également réconciliée** (`ppm_2003` B87, éditions 2425 + 2526) : IE civil 2025 =
1 982,5 + 1 939,0 = **3 921,5 périodes = lecture SOAP exacte** (C 2 554,5 · I 598 · F 289 · K 181 ·
V 299). Le `PPM_2002` (« IE de type EPT ») est **vide** : les sessions sans élèves sont des IE
ordinaires, pas des EPT — le résidu PE encadrement (±1 %) relève donc uniquement de leur mode de
valorisation (élèves/moyenne), toutes les assiettes étant désormais validées à 100 %.

## Avertissements et limites

- Les élèves « redevables DI non en ordre de paiement » devraient être exclus (specs 16/19) — non vérifiable via Doc 2 seul (croisement SEPS possible).
- L'arrêté (art. 4, 1°) base l'ajustement sur les périodes **prévues** de l'avant-dernière année civile ; ce rapport utilise les périodes **réelles** (PEP effectivement générées, décret art. 99). Écart possible si prévu ≠ réel.
- Étapes 5-6 de l'arrêté (neutralisation des augmentations, corrections de dépassement) non applicables sans la dotation de référence (hors API, « pot K »).
- Volume EPT 2025 : 319 périodes (plafond 10 % de la dotation organique à vérifier hors API).
