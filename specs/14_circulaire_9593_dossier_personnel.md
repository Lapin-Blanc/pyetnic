# Circulaire 9593 — Dossier personnel de l'étudiant, registre matricule, droits d'inscription & présences (EA)

> Analyse fonctionnelle « contexte métier SEPS »
> Source : Circulaire **9593** du **23/09/2025**, « Circulaire concernant la constitution du dossier personnel de l'étudiant, la tenue du registre matricule, ainsi que la gestion des droits d'inscription et des présences dans le cadre de l'Enseignement pour Adultes » (34 p., texte natif). **Abroge et remplace la 9350** du 17/09/2024. Validité à partir du 25/08/2025.
> Date d'analyse : 2026-06-09 (session 7)

---

## Portée et intérêt pour pyetnic

Cette circulaire est le **cadre réglementaire** des données manipulées par les **services SEPS** (specs 09-13). Elle explicite la sémantique métier de champs qui, dans les XSD, ne sont que des codes : `motifExemption`, `droitInscription`/`droitInscriptionSpecifique`, `regulier1`/`regulier5`, `statut`, le **registre matricule**, le **NISS / NISS bis**, et les **présences** (comptage 1/10ᵉ & 5/10ᵉ). Elle relie aussi SEPS aux **colonnes du Document 1** EPROM (population, spec 03).

> ⚠️ Ne pas confondre avec la **circulaire 9589** (session 6, specs 07-08) qui traite du **personnel** (paie, EA12). La 9593 traite des **étudiants** (dossier, inscription, DI).

---

## Acteurs & cadre

- **Direction de l'Enseignement pour Adultes (EA)** — Service de la Vérification : contrôle la conformité des dossiers (vérificateurs nommés).
- **EA** = « Enseignement pour Adultes » : nouvelle dénomination de la « promotion sociale » (cf. session 6). Les identifiants techniques SEPS/EPROM restent inchangés.
- Base légale citée : Décret du **16/04/1991** (organisation de l'EA) ; Loi du **29/05/1959** dite « Pacte scolaire » (art. 12 — droits d'inscription et exemptions).

---

## Comptage des étudiants — 1ᵉʳ/10ᵉ et 5ᵉ/10ᵉ (jonction `regulier1`/`regulier5`)

Le comptage conditionne le financement (frais de fonctionnement, charges du personnel). Les **1ᵉʳ et 5ᵉ dixièmes** d'une UE sont calculés sur les dates d'ouverture/fermeture (jours calendaires, **Documents A** EPROM).

**Comptabilisé au 1ᵉʳ/10ᵉ** si : dossier d'inscription complet (fiche/reçu, paiement DI ou justificatif d'exemption, admission validée par titre/test, doc d'identité) **+** inscrit et **présent** au plus tard à la date du 1ᵉʳ/10ᵉ **+** pas de valorisation en dispense complète.
**Comptabilisé au 5ᵉ/10ᵉ** si : dossier complet **+** pas en abandon avant le 5ᵉ/10ᵉ **+** présence effective à cette date et au-delà **+** pas de dispense complète.

➜ **Jonction SEPS** : `specificite.regulier1` / `regulier5` (`O`/`N`) matérialisent ce statut « régulier » aux deux dixièmes. Ces champs sont **gelés après validation** du dixième correspondant (erreurs `30079`/`30080`, spec 11).
➜ **Jonction EPROM Doc 1** (spec 03) : les populations comptées alimentent `nbEleve*` (population au 1/10ᵉ) ; le Doc 1D (spec 06) gère le 5/10ᵉ (`nbEleves5ieme`).

---

## Composition du dossier individuel (jonction signalétique `EtudiantDetailsType`)

Pièces requises par étudiant (classées par ordre alphabétique, conservation au siège) :

1. **Copie du document d'identité** (belge / ressortissant UE / hors UE avec titre de séjour valide — loi 21/06/1985).
2. **Titre d'accès** (capacités préalables requises, diplôme, équivalence des titres étrangers, ou valorisation des acquis par le Conseil des études).
3. **Fiche d'inscription / reçu** (informatisé, signé) — **données d'identité** : nom, prénom, **date et lieu de naissance**, **genre**, **nationalité**, **adresse** ; **données académiques** : intitulé + **codes/numéros administratifs** des UE, dates d'organisation + 1ᵉʳ/10ᵉ, hybride « H », ventilation des périodes, **montant DI par UE** (avec niveau) ou **motif d'exemption**, **DIS** le cas échéant, admission par titre/test, **ECTS**, UE valorisées en dispense, **date d'inscription**, codiplômation « CH », historique, date d'impression.
4. **Décision favorable du Conseil des études** en cas de réinscription dans une UE déjà réussie.
5. **Documents d'exonération du DI** (voir ci-dessous).

➜ **Jonction SEPS** : la fiche d'inscription/reçu est la **contrepartie papier** des données de `EtudiantDetailsType` (specs 09-10 : nom, prénom, naissance{date,codePays,localite}, sexe, codeNationalite, adresse) **+** `InscriptionType`/`UEType`/`SpecificiteDataType` (spec 11-12 : dateInscription, UE codes/n° administratif, DI/DIS, admission, valorisation).

---

## Droits d'inscription (DI), DIS et DIC

| Sigle | Nom | Champ SEPS correspondant |
|---|---|---|
| **DI** | Droit d'inscription | `specificite.droitInscription.indicateurDroitInscription` (+ `exempte`) |
| **DIS** | Droit d'inscription **spécifique** (étudiants **hors UE/CEE**) | `specificite.droitInscriptionSpecifique` |
| **DIC** | Droit d'inscription **complémentaire** (frais admin., art. 12 §4-5) | *hors SEPS* (propre à l'établissement) |

### Cas d'exemption du DI ↔ `MotifExemptionType` (spec 11)
La circulaire détaille les cas du Pacte scolaire (art. 12 §3) ; correspondance avec l'énumération SEPS `MotifExemptionType` :

| `MotifExemption` (SEPS) | Cas circulaire 9593 |
|---|---|
| `C01` Mineur obligation scolaire | §A.1 (attestation établissement ; rappel : pas d'inscription EA pendant l'obligation scolaire **à temps plein**, art. 6 décret 1991) |
| `C02` Chômeur complet indemnisé | §A.2/A.6 (chercheurs d'emploi ; attestations Actiris/Forem/ADG/VDAB) |
| `C03` Handicap reconnu | §A.5 (document probant AVIQ/SPF/INAMI/mutuelle/CAAMI) |
| `C04` Bénéficiaire du RIS | §A.7 (attestation CPAS ; RIS/ERIS ; FEDASIL) |
| `C05` Personnel enseignant — formation continuée/recyclage | §A.8 (attestations ANNEXES 4/5 ; TIC d'office) |
| `C06` Obligation autorité publique | §A.9 (ANNEXES 6/7 ; SAFA/SAD) |
| `C07` Autre | §A.4, §A.10, §B (FLE ≤ A2, alphabétisation/sec. inf. sans CEB prérequis ; codiplômation ; incarcérés ; 7e aide-soignant ; numérique éducatif ; alternatives 7e) |

➜ **Renvois explicites aux colonnes du Document 1 EPROM** (spec 03) :
- Cas « demandeur d'emploi » (chômeur émargeant à la mutuelle) → **colonne 7 « Demandeur d'emploi » du DOC 1** = `nbEleveDem`.
- Cas « autres exemptés » (FLE/alphabétisation, codiplômation, alternatives 7e) → **colonne 7'' « autres exemptés » du DOC 1** = `nbEleveExm`.

### Exemption du DIS ↔ `MotifExemptionSpecType` (spec 11)
Réservé aux nationalités **hors CEE** (sinon erreur `30023`). Les 13 motifs `C01`-`C13` (spec 11) reprennent les catégories de séjour/famille/CPAS/réfugié (loi 15/12/1980), cf. circulaire 8681 référencée.

---

## Registre matricule des étudiants et des droits d'inscription

Registre **par ordre alphabétique**, recensant **tous** les étudiants inscrits à tout moment de l'année académique, en colonnes : **nom, prénom, date de naissance, codes des UE suivies, montant du DI ou motif d'exemption**. Regroupe les étudiants dont le **1ᵉʳ/10ᵉ** d'une UE tombe dans l'année académique. **Conservation : 30 ans** (édité ou archivé électroniquement).

➜ **Jonction SEPS** : le registre matricule est la **vue agrégée par établissement** des données renvoyées par `rechercherInscriptions` (spec 12) + signalétique `rechercheEtudiants`/`lireEtudiant` (spec 09). Le **`cfNum`** est l'identifiant pivot.

---

## NISS / NISS bis / identification

- **NISS** (NissType, specs 09-10) : n° de registre national **ou** n° de registre des étrangers. Contrôle **mod 97**.
- **NISS bis** : numéro de registre **BIS** créé quand aucune correspondance RN n'existe (étudiant non répertorié au RN). Côté SEPS : `enregistrerEtudiant` mode DETAILS avec `createBisFlag=true` → appel **PUBLISHPERSON** (spec 10).
- **cfNum** : identifiant interne DB SEPS (≠ NISS), attribué à la création.
- Les **annexes** d'exonération (Actiris/Forem/FEDASIL) demandent « **NISS ou NN** » et, pour FEDASIL, « **SP ou RN** » (n° Sécurité Publique / Registre National) — cohérent avec la double identité RN/bis.

---

## Présences (jonction comptage)

Registre de présence **par UE**, par ordre alphabétique (inscrits au 1ᵉʳ/10ᵉ puis ajouts). Annotations quotidiennes :

| Marque | Signification | Comptage |
|---|---|---|
| `\|` ou `P` | Présent | présence |
| `-` ou `A` | Absent | absence |
| `CM` | Absence couverte par **certificat médical** | **assimilée à présence** |
| `D` | Dispense **partielle** | (valorisation d'activités) |
| `M` | Présence à un cours **à distance** (UE hybride) | présence |
| (trait continu / « abandon ») | Moment de l'**abandon** | sortie |
| `CH` | Étudiant en **codiplômation** (réputé assidu) | présence présumée |

Toute autre annotation = absence au comptage. Dossier incomplet à la date de comptage → étudiant **rayé** des registres. **Conservation : 4 ans** (FSE/VOV : délais spécifiques).

➜ **Jonction SEPS** : les présences ne sont **pas** transmises par les services SEPS (gérées localement) ; elles **conditionnent** le statut `regulier1`/`regulier5` (spec 11) et, en cas d'abandon, la `sanction` (`codeSanction = AB`, `motifAbandon`).

---

## Glossaire (extrait — utile pour la doc utilisateur pyetnic)

| Sigle | Signification |
|---|---|
| EA | Enseignement pour Adultes (ex-« promotion sociale ») |
| DI / DIS / DIC | Droit d'inscription / spécifique / complémentaire |
| RIS / ERIS | Revenu d'intégration sociale / aide équivalente |
| CPAS | Centre public d'action sociale |
| FLE | Français langue étrangère |
| FSE | Fonds social européen |
| UE | Unité d'enseignement |
| ECTS | European Credits Transfer System |
| RGE | Règlement général des études |
| CEB | Certificat d'études de base |
| AVIQ / INAMI / CAAMI | Organismes santé/handicap (documents probants) |
| Forem / Actiris / ADG / VDAB | Offices régionaux de l'emploi (exemptions chercheurs d'emploi) |
| BCSS / BCED / RN | Banque Carrefour Sécurité Sociale / Échange de Données / Registre National |

**Annexes (modèles d'attestation d'exemption)** : 1 Actiris · 2 Forem · 3 FEDASIL/aide matérielle · 4 personnel enseignant (TIC) · 5 personnel enseignant · 6 obligation autorité publique · 7 aide à la vie journalière (SAFA/SAD).

---

## Points à confirmer avec l'ETNIC

- Correspondance exacte **`MotifExemption` C0x ↔ libellés circulaire** : la circulaire structure les cas légèrement différemment (regroupements Pacte scolaire) ; le mapping ci-dessus est **fonctionnel**, à valider au cas par cas (notamment C02 chômeur vs C04 RIS vs C07 autres).
- Articulation **`statut` de l'inscription SEPS (DE/AN)** vs « abandon » des registres de présence (la sanction `AB` n'annule pas l'inscription `DE`).
- Le **DIC** n'a pas de champ SEPS : confirmer qu'il reste hors périmètre des web services.
