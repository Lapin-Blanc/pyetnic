# Circulaire 9589 — Rentrée scolaire 2025-2026 (Enseignement pour Adultes) — Contexte métier « personnel »

> Analyse fonctionnelle de la circulaire de rentrée des membres du personnel (MDP),
> en complément des spécifications des services SOAP ETNIC EPROM.
> Source : `circulaires/53089_0000.pdf` (356 pages PDF = 293 pages numérotées + annexes A1-A36).
> Date d'analyse : 2026-06-05 — Fichier 1/2 (contexte). Voir `08_circulaire_9589_ea12_attributions.md` pour le modèle EA12/attributions.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Circulaire | n° 9589 du 19/09/2025 |
| Type | Circulaire de rentrée (bleue) |
| Validité | à partir du 25/08/2025 |
| Abroge et remplace | circulaire n° 9343 du 24/08/2024 |
| Objet | Gestion administrative et pécuniaire des MDP de l'enseignement pour adultes (ex promotion sociale) |
| Émetteur | AGE — DGPE (Direction générale des personnels de l'enseignement), Direction de l'enseignement non obligatoire (DENO) |
| Réseaux | WBE, officiel subventionné (OS), libre subventionné (LS) |
| Niveaux | EA secondaire, EA secondaire en alternance, EA supérieur |
| Contact | Yolande PIERRARD, SGGPE/DENO — 02/413 29 14 — yolande.pierrard@cfwb.be |
| Mots-clés officiels | Liquidation ; Traitements ; Pouvoir Régulateur ; Pouvoir Organisateur ; Direction de Gestion ; EA12 |

### Structure du document (renvois)

| Partie | Pages (numérotation circulaire) |
|---|---|
| Nouveautés et modifications | 15-16 |
| Fiche I — Informations pratiques (sigles, rythmes scolaires, organigrammes, EU) | 17-65 |
| Fiche II — Acteurs-clés (PR, PO, MDP) | 66-108 |
| Fiche III — Documents à transmettre au PR (GEDI, échéances, EA12/EA12bis/EA12ter, codes DI, codes RTF/RL10/FADI, annexes 2-36) | 109-290 |
| Récapitulatif des annexes | 291-293 |
| Formulaires vierges (annexes) | PDF pages 294-356 |

> Correspondance pages : page numérotée N = page PDF N+2.

---

## 1. Positionnement par rapport aux services EPROM

La circulaire couvre la **face « personnel/paie »** du domaine promotion sociale, complémentaire
de la face « offre de formation » couverte par les services SOAP EPROM déjà spécifiés :

| Face « offre de formation » (EPROM, specs 01-06) | Face « personnel/paie » (circulaire 9589) |
|---|---|
| Formations/UE organisables et organisées | Attributions des MDP dans les UE (EA12) |
| Document 1 (population), Document 2 (périodes), Document 3 (attributions) | Doc12 = EA12 : demande de mise en liquidation des traitements |
| Approbation école → PO → Administration | Transmission PO → Direction de gestion via GEDI |
| Identifiants FASE (etabId, implId) | Identifiants ECOT + FASE + matricule enseignant |

**Points de jonction concrets avec les specs EPROM** (détaillés dans le fichier 08) :

- Le code **U.E.** demandé sur l'EA12 (« 9 chiffres et 2 lettres ») correspond au
  `codeFormation` d'EPROM (ex. `761001U31C1` — spec 01, registre `FormationCT`).
- Le **matricule enseignant** (11 positions) = `noMatEns` du Document 3 EPROM (spec 05).
- Les **codes DI** (disponibilité/congé) de la circulaire ≈ table `coDispo` du Document 3.
- L'EA12 exige de reporter l'intitulé des cours « tel que repris au **document 8 ou 8bis** »
  et la classification du **document 2** — ces documents amont sont ceux référencés par
  `nbPeriodesDoc8`, `nbPeriodesPrevuesDoc2`, `nbPeriodesReellesDoc2` du Document 3 EPROM.
- ⚠️ La **situation administrative** EA12 (D, Z, V, S, I, St, P, R, A, T, M) n'est **pas** la même
  table que `teStatut` du Document 3 (C, P, A, D, E, X, T) — faux ami, voir fichier 08, §5.

---

## 2. Terminologie — changement de dénomination officiel

> **« Enseignement pour adultes » (EA) remplace « Enseignement de promotion sociale » (EPS)**
> depuis le décret du 27/03/2025 (parution MB 08/04/2025). La circulaire 9589 applique
> systématiquement la nouvelle appellation (« ex promotion sociale »).

Conséquences pour l'implémentation :

- Les textes réglementaires et les noms techniques historiques conservent « promotion sociale »
  (décret organique du 16/04/1991, codes unité 212/215/219/222 du registre, namespaces EPROM…).
- Les documents récents et formulaires utilisent « EA » (EA12 = ex PS12 ; la rubrique
  « Date du PS12 précédent » subsiste d'ailleurs telle quelle dans le mode d'emploi p.138).
- Recommandation pyetnic : conserver les identifiants techniques EPROM/PS existants,
  mais utiliser « enseignement pour adultes (EA) » dans la documentation utilisateur.

Autre terme générique : **Doc12** = terme couvrant EA12, FOND12, SEC12, A12… selon le niveau
d'enseignement. Dans l'EA : EA12 (secondaire), EA12 bis (supérieur), EA12 ter (experts).

---

## 3. Acteurs et responsabilités

### Pouvoir régulateur (PR) — la FWB (p.66-67)

- **Liquide mensuellement** les (subventions-)traitements des MDP sur la base des documents
  transmis (Doc12, CAD…) — débiteur de revenus des MDP.
- Transmet trimestriellement à l'ONSS la déclaration multifonctionnelle (**DMFA**).
- Met à disposition des MDP fiches de paie, fiches fiscales et documents via **Mon Espace**.

### Pouvoir organisateur (PO) (p.67-88)

- Employeur du MDP (l'engagement lie le MDP au PO, pas à la FWB).
- Obligations clés : déclarations **DIMONA** (entrée/sortie) et **DDRS**, transmission des
  documents exacts et dans les délais, contrôle mensuel des traitements versés (application
  **GESP**), avance sur rémunération obligatoire en cas de retard qui lui est imputable.
- Interlocuteur de l'Administration via une **Direction de gestion** territorialement compétente
  (Brabant wallon, Bruxelles, Hainaut I Mons, Hainaut II Charleroi, Liège, Namur/Luxembourg) ;
  pour l'EA, direction spécifique : **DENO**.

### Membre du personnel (MDP) (p.88-108)

- Consulte ses documents (Doc12, fiches de paie, fiches fiscales) sur **Mon Espace**
  (https://monespace.fw-b.be/).
- Catégories de statut : **T** (temporaire), **TPr** (temporaire prioritaire — « protégé » en EA WBE),
  **St** (stagiaire directeur), **D** (définitif), **ACS/APE/PTP** (statuts spécifiques d'aide à l'emploi).

---

## 4. Identifiants — référentiel

### N° ECOT (10 chiffres) — identifiant « paie » de l'établissement

Structure différente selon le réseau (mode d'emploi EA12, p.123-124 ; EA12bis p.159-160) :

**Enseignement organisé (WBE)** :

| Cases | Valeur |
|---|---|
| 1-2 | `80` |
| 3-4 | `11` |
| 5-6 | `24` |
| 7-10 | N° d'établissement Communauté française |

**Enseignement subventionné** :

| Case | Signification | Valeurs |
|---|---|---|
| 1 | PO | 1 = communal, 2 = libre, 4 = provincial |
| 2 | Type d'enseignement | 5 = technique et professionnel |
| 3 | — | 2 = enseignement de promotion sociale |
| 4 | Province et assimilée | 1 = COCOF, 2 = Bruxelles ou Brabant wallon, 5 = Hainaut, 6 = Liège, 8 = Luxembourg, 9 = Namur |
| 5-7 | Commune | — |
| 8-10 | Établissement dans la commune | — |

### N° FASE — identifiant « pédagogique » de l'établissement

Demandé sur l'EA12 **en plus** du n° ECOT. C'est l'identifiant utilisé par les services EPROM
(`etabId`/`EtabIdST`, `implId`/`ImplIdST` du registre). Un établissement a donc **deux identifiants
parallèles** : ECOT (côté paie/DGPE) et FASE (côté offre/AGE) — toute application qui fait le pont
entre les deux faces doit maintenir cette correspondance.

### Matricule enseignant (11 positions) — format

| Cases | Contenu |
|---|---|
| 1 | Sexe : `1` = homme, `2` = femme |
| 2-7 | Date de naissance inversée `AAMMJJ` |
| 8-11 | 4 chiffres attribués par l'Administration à l'immatriculation |

- Si immatriculation en cours : laisser les 4 dernières cases vides.
- Correspond au `noMatEns` du Document 3 EPROM (ex. `28208171112` = femme, née 17/08/1982, n° 1112).
- L'immatriculation s'obtient via la **Fiche signalétique (A3)** (p.229-236) : 1ʳᵉ entrée en fonction,
  entrée en fonction d'un MDP déjà immatriculé, ou modification signalétique.

### NISS / NISS bis

- **NISS** : n° d'identification unique à la sécurité sociale = n° de Registre national.
- **NISS bis** : pour les personnes hors Registre national ; reconnaissable au 3ᵉ chiffre
  (obligatoirement 2, 3, 4 ou 5, ex. `904122xxxxx`). Données RN non fiables pour ces MDP →
  signalétique complète requise.
- Depuis octobre 2020, l'Administration récupère la signalétique des MDP à NISS belge
  directement du Registre national (envoi allégé : RN, nom, prénom, sexe).

---

## 5. Calendrier 2025-2026 (rythmes scolaires)

### Règles structurelles (p.23-28)

- Calendrier réformé depuis 2022-2023 : alternance 7 semaines de cours / 2 semaines de congé,
  180 à 184 jours de scolarité.
- **Année académique EA** : commence le **dernier lundi d'août** et se termine la veille de la
  rentrée suivante. Exception : si le dernier lundi est un 30 ou 31 août, l'année commence
  l'avant-dernier lundi (alignement sur l'obligatoire) — art. 46 D.-31/03/2022 modifiant
  l'art. 5bis, 21° du décret du 16/04/1991.
- L'année scolaire des MDP s'étend du dernier lundi d'août au premier vendredi de juillet :
  **313 jours** entre début et fin (au lieu de 300-303 avant la réforme).
- Dans l'EA, seuls les **congés d'hiver et jours fériés légaux sont obligatoires** ; les PO
  des cours < 32 semaines peuvent s'adapter en respectant le nombre de jours de scolarité.
- Des activités d'enseignement peuvent être organisées **pendant les vacances d'été** dès le
  1ᵉʳ samedi de juillet → EA12 distinct (voir fichier 08, §4.5).

### Dates 2025-2026 (circulaire 9487 du 16/04/2025)

| Élément | Date |
|---|---|
| Rentrée académique | lundi 25/08/2025 |
| Fin de l'année académique | dimanche 23/08/2026 |
| Vacances d'hiver (suspension obligatoire) | lundi 22/12/2025 → vendredi 02/01/2026 |
| Fin d'année scolaire MDP (1ᵉʳ vendredi de juillet) | 03/07/2026 (vacances d'été dès le samedi 04/07/2026) |

Jours fériés sans activités d'apprentissage/évaluation : 27/09/2025 (Fête FWB), 01-02/11/2025,
11/11/2025, 25/12/2025, 01/01/2026, 05-06/04/2026 (Pâques), 01/05/2026, 14/05/2026 (Ascension),
24-25/05/2026 (Pentecôte), 21/07/2026, 15/08/2026.

> Utile pour pyetnic : validation des périodes d'occupation et des dates d'événement des
> documents ; l'année scolaire EPROM (`AnneeScolaireST`, pattern `\d{4}-\d{4}`) couvre
> désormais réellement du 25/08 au 23/08.

---

## 6. Échéancier de paie 2025-2026 (p.113-114)

Paiement le **dernier jour ouvrable du mois**. Les documents doivent parvenir à l'Administration
au plus tard à la **date-limite de réception** pour garantir le paiement du mois :

| Mois | Paiement | Période couverte | Date-limite réception |
|---|---|---|---|
| Septembre 2025 | 30/09/25 | 01/09 – 30/09 (+ 25/08 – 31/08 pour les temporaires) | **12/09/25** |
| Octobre 2025 | 31/10/25 | 01/10 – 31/10 | 15/10/25 |
| Novembre 2025 | 28/11/25 | 01/11 – 30/11 | 12/11/25 |
| Décembre 2025 | 31/12/25 | 01/12 – 31/12 | 09/12/25 |
| Janvier 2026 | 30/01/26 | 01/01 – 31/01 | 14/01/26 |
| Février 2026 | 27/02/26 | 01/02 – 28/02 | 11/02/26 |
| Mars 2026 | 31/03/26 | 01/03 – 31/03 | 13/03/26 |
| Avril 2026 | 30/04/26 | 01/04 – 30/04 | 14/04/26 |
| Mai 2026 | 29/05/26 | 01/05 – 31/05 | 08/05/26 |
| Juin 2026 | 30/06/26 | 01/06 – 30/06 | 12/06/26 |
| Juillet 2026 | 31/07/26 | 01/07 – 31/07 (+ différé temporaires) | 14/07/26 |
| Août 2026 | 31/08/26 | 01/08 – 31/08 (+ différé temporaires) | 13/08/26 |

- Les MDP **temporaires** sont payés avec **traitement différé** l'été ; le personnel de sélection
  et de promotion temporaire de l'EA est payé **en dixièmes** (et non en douzièmes).
- Consigne récurrente : envoi « au fil de l'eau », ne pas attendre la date ultime.

---

## 7. Écosystème applicatif (perspective intégration)

| Application | Rôle | Notes intégration |
|---|---|---|
| **GEDI** | Canal unique et obligatoire (depuis 22/04/2024) de transmission numérique des documents carrière/paie vers les Directions de gestion | Deux canaux : voir ci-dessous |
| **GEDI-PRO** | Application métier web fournie par l'Administration | Accès : formulaire + engagement de confidentialité → acces-gesper@cfwb.be |
| **GEDI-WS** | **Web service** pour applications locales des écoles/PO | Applications déjà connectées : **ProEco, CREOS, EPHEC**. La formation/l'accompagnement relèvent du prestataire de l'application locale |
| **GESP** | Téléchargement PDF par le PO des données pécuniaires (listings mensuels/annuels par n° ECOT, fiches de paie) | Données disponibles vers le 25 du mois, conservées 5 ans. Support DDRS : 02/413 35 00 |
| **Mon Espace** | Guichet électronique des MDP (Doc12, fiches de paie, fiches fiscales, n° de compte) | https://monespace.fw-b.be/ |
| **DIMONA/DDRS** | Déclarations ONSS immédiates (entrée/sortie) et risques sociaux | Les dates DIMONA doivent concorder **strictement** avec les périodes d'occupation des EA12 |
| **CAMMAT** | Communication d'Absence Maladie-Maternité-Accident du Travail — pilote depuis 19/05/2025 | Période transitoire : les relevés RIM (A35/36) sont maintenus |
| **VALEXU** | Demandes de valorisation d'expérience utile (circulaire 9528 du 12/06/2025) | Les dépêches d'EU métier proviennent de VALEXU |
| **PRIMOWEB** | Référentiel public titres/fonctions (RTF) + offres d'emploi | Liste des codes RTF par fonction ; tableau de correspondance des fonctions (AGCF-05/06/2014) |

> **GEDI-WS** est le seul canal « machine » documenté côté personnel. Si une application locale
> devait à terme transmettre des Doc12, c'est par ce canal (accès via la cellule GEDI), pas par
> les services EPROM. Les services EPROM (formations/documents 1-3) et GEDI (documents
> personnel/paie) sont des mondes distincts.

### Exceptions au canal GEDI (p.111)

- DNTA/DNTA religion (disponibilités par défaut d'emploi, réaffectations) : hors GEDI.
- Déclarations d'accident du travail : par e-mail à accidents.travail.enseignement@cfwb.be
  (circulaire 9211).

### Signatures (p.112)

La transmission par GEDI dispense des signatures, **sauf** : prestation de serment (A4),
relevé de grève, relevé ANRJ, CAD pour IC irréversible à temps partiel 55+, demandes de DPPR,
contrat ACS/APE, déclaration de double nationalité belgo-française, DNTA.

---

## 8. Sigles essentiels (sélection orientée implémentation, p.18-22)

| Sigle | Signification |
|---|---|
| ANRJ | Absence non réglementairement justifiée |
| CAD | Congés, absences, disponibilités |
| DI | Codes CAD de congés, absences et disponibilités |
| DMFA | Déclaration multifonctionnelle à l'ONSS |
| Doc12 | Terme générique pour EA12, FOND12, SEC12, A12, etc. |
| DPPR | Disponibilité pour convenances personnelles précédant la pension de retraite |
| EA | Enseignement pour adultes (anciennement promotion sociale) |
| EHR | Enseignement à horaire réduit |
| EUM | Expérience utile métier |
| FADI | Référentiel des fonctions, absences et disponibilités |
| FLT | Fixation liquidation traitement (service) |
| GEDI | Gestion des échanges de données et interconnexions |
| MDP | Membre du personnel |
| MFI | Module de formation individualisée |
| NCC | Non chargé de cours |
| PO / PR | Pouvoir organisateur / Pouvoir régulateur |
| PVC / PVD | Procès-verbal de carence / de dérogation |
| RL10 | Application/moteur de calcul de la paie des MDP |
| RTF | Régime des titres et fonctions (réforme 2016) |
| TR / TS / TP / TPNL | Titre requis / suffisant / de pénurie (listée) / de pénurie non listée |
| UE | Unité d'enseignement |

Lettres de situation administrative (utilisées sur les Doc12 — table complète au fichier 08, §5) :
D, Z, V, S, I, St, P, R, A, T, M.

---

## 9. Nouveautés 2025-2026 (p.15-16)

- Appellation « Enseignement pour adultes » (décret 27/03/2025, MB 08/04/2025).
- Annexes inter-réseaux renumérotées : un même document transversal porte le même intitulé
  et le même numéro tous niveaux confondus.
- Tableaux récapitulatifs codes **RTF/RL10/FADI** (voir fichier 08, §9).
- Dérogation de titre requis au supérieur : remplacée par une **case à cocher sur l'EA12 1bis**
  (l'ancienne annexe 26 disparaît).
- Fin de l'envoi postal des listings de paie (circulaire 9415 du 22/01/2025 — dématérialisation).
- VALEXU : informatisation de la valorisation d'expérience utile (circulaire 9528 du 12/06/2025).
- **CAMMAT** : pilote depuis le 19/05/2025 (RIM maintenus pendant la transition).
- A5bis : valorisation d'ancienneté acquise dans le **secteur privé**.
- A27 (prestations mensuelles d'expert) : plusieurs UE possibles sur la même annexe.

---

## 10. Récapitulatif des annexes (p.291-293)

Annexes les plus pertinentes pour le périmètre pyetnic/EA (liste complète dans la circulaire) :

| N° | Document | Détail |
|---|---|---|
| **1** | **EA12** secondaire — demande de mise en liquidation | fichier 08, §3-5 |
| **1bis** | **EA12 bis** supérieur — demande de mise en liquidation | fichier 08, §7 |
| **1ter** | **EA12 ter** experts — demande de mise en liquidation | fichier 08, §8 |
| 2 | Déclaration de cumul interne | fichier 08, §10 |
| 3 | Fiche signalétique (immatriculation/signalétique MDP) | §4 ci-dessus |
| 4 | Prestation de serment | — |
| 5/5bis | Services antérieurs (EUM/enseignement/public ; secteur privé) | — |
| 27 | Prestations mensuelles d'un expert | fichier 08, §8 |
| 28 | Demande de dérogation au profit d'un expert (> 260 périodes) | fichier 08, §8 |
| 34 | Dépassement du tiers (article 77) | fichier 08, §8/§10 |
| 35/36 | Relevé individuel mensuel des absences (RIM) — transition CAMMAT | — |

Autres annexes (6-26, 29-33) : attestations, dérogations linguistiques, accidents du travail,
pécule jeune diplômé, nominations… — hors périmètre direct, voir circulaire p.291-293.

---

## 11. Références citées utiles

| Référence | Objet |
|---|---|
| D.-16/04/1991 | Décret organique de l'enseignement de promotion sociale |
| D.-11/04/2014 | Décret « titres et fonctions » (RTF) |
| AGCF-05/06/2014 | Fonctions, titres de capacité et barèmes (tableau de correspondance, bascule) |
| D.-20/06/2013 | EPT, coordinateur qualité, conseiller à la formation, e-learning |
| D.-31/03/2022 | Réforme des rythmes scolaires annuels |
| D.-27/03/2025 (MB 08/04/2025) | Renommage « Enseignement pour adultes » |
| Circulaire 9487 du 16/04/2025 | Calendrier général de fonctionnement EA 2025-2026 |
| Circulaire 8536 du 30/03/2022 | EPS : rythmes scolaires |
| Circulaire 9316 du 12/07/2024 | Vade-mecum CAD (congés/disponibilités/absences) |
| Circulaire 7716 du 31/08/2020 | Priorisation des titres au primo-recrutement (EPS) |
| Circulaire 9391 du 10/12/2024 | Contrôle local du respect de la priorité des titres |
| Circulaire 9415 du 22/01/2025 | Dématérialisation complète des listings de paie |
| Circulaire 9528 du 12/06/2025 | Application VALEXU |
| Circulaire 8869 du 21/03/2023 | Travail après la retraite / au-delà de 65 ans (experts ≤ 70 ans) |
| AECF-26/01/1993 | Statut des experts (EA) |
| Loi 24/12/1976, art. 76-77 | Plafonds experts et fonction accessoire (dépassement du tiers) |
