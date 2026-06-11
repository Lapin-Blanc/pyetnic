# Suivi des sessions d'analyse — Refonte pyetnic

## Objectif global
Établir la spécification technique et fonctionnelle exhaustive de tous les services
SOAP ETNIC EPROM, en vue de refondre la bibliothèque pyetnic avec :
- Architecture propre (bons patterns)
- Tests exhaustifs (unitaires + intégration avec mock server SOAP stateful)
- Support multi-services, multi-versions
- Focus initial : services EPROM (promotion sociale)

## Décisions d'architecture prises

1. **Client SOAP** : zeep (conservé, approche éprouvée)
2. **Mock server** : vrai serveur SOAP stateful (spyne ou équivalent) — pas juste des fixtures
   → nécessaire pour tester les workflows complets (ex: doc3 inaccessible tant que doc1+doc2 non approuvés)
3. **Gestion d'erreurs** : exceptions typées (modèle SEPS) pour tous les services
4. **Versions** : toujours la dernière version de chaque service
5. **Authentification** : WS-Security Username Token pour EPROM, certificat X509 pour SEPS (plus tard)

## Sessions réalisées

### Session 1 — 2026-04-14 : Formations Liste v2 + analyse pyetnic existant

**Services analysés** :
- ✅ EPROM Formations Liste v2.0 (WSDL + PDF 18 pages)

**Fichiers produits** :
- `specs/01_formations_liste_v2.md` — spécification complète
- `specs/00_REGISTRE.md` — registre des types XSD partagés (initialisé)
- `specs/00_SUIVI_SESSIONS.md` — ce fichier
- `contrat_formations_liste_v2/` — WSDL + 10 XSD extraits

**Code existant analysé** :
- pyetnic sur GitHub (https://github.com/Lapin-Blanc/pyetnic)
- 5 services EPROM + 4 services SEPS
- Architecture en couches, config lazy par métaclasse
- Défauts identifiés : D1 (cache), D2 (asdict None), D3 (erreurs inconsistantes)
- Sprint 0 en cours (69 tests de régression)

**Informations clés du PDF non présentes dans le WSDL** :
- Valeurs possibles StatutCT.statut : "Encodé école", "Encodé PO", "Approuvé"
- Organisation ignorée dans ListerFormationsOrganisables
- Codes d'erreur complets (00009, 00025, 00999, 30001, 30002, 30007)
- Deux endpoints (EPROM spécifique vs Ecole générique déprécié)

---

### Session 2 — 2026-04-14 : Formation Organisation v7

**Services analysés** :
- ✅ EPROM Formation Organisation v7.0 (WSDL + PDF 23 pages, rev5.1 du 01-07-2025)

**Fichiers produits** :
- `specs/02_formation_organisation_v7.md` — spécification complète
- `specs/00_REGISTRE.md` — registre enrichi (Common_v2, FormationOrganisation_v7, codes erreur 20xxx/30xxx)
- `contrat_formation_organisation_v7/` — WSDL + 7 XSD extraits
- `manuel_formation_organisation_v7.pdf` — PDF téléchargé

**Découvertes clés** :
- **4 opérations CRUD** : CreerOrganisation, LireOrganisation, ModifierOrganisation, SupprimerOrganisation
- **Common_v2.xsd** remplace Common_v1.xsd : nouveau pattern ResponseType avec attributs
  requestId + transactionId (au lieu de header SOAP séparé)
- **FormationOrganisation_v7.xsd** : nouveaux champs booléens par rapport à v2
  (reorientation7TP, activiteFormation, conseillerPrevention, enseignementHybride,
  partiellementDistance, numOrganisation2AnneesScolaires)
- **eLearning et partiellementDistance** supprimés en entrée depuis 2022-2023, remplacés par
  enseignementHybride, mais toujours présents dans le type de retour
- **implId obligatoire uniquement en Créer** : absent des requêtes Lire/Modifier/Supprimer
- **numOrganisation auto-généré** à la création
- **nombreSemaineFormation** calculé automatiquement par le système
- **Table d'erreurs très riche** : 26 codes spécifiques (20005-20038, 30001-30009)
- **typeInterventionExterieure** : 15 valeurs possibles dont "J" (nouveau v7) et 2 supprimées ("R", "S")
- **Contrainte code 30003** : modifier/supprimer bloqué si statut documents ne le permet pas
- XSD partagés (AnneeScolaire_v1, Etablissement_v1, ResponseStatus_v3, requestId_v1) **identiques** à Formations Liste
- Pas de Addressing_v2.xsd ni Authorisation_v2.xsd (endpoint spécifique EPROM uniquement)

---

### Session 3 — 2026-04-14 : Formation Population v1 + Formation Périodes v1

**Services analysés** :
- ✅ EPROM Formation Population (Document 1) v1.0 (WSDL + PDF 23 pages, rev1.1 du 01-05-2023)
- ✅ EPROM Formation Périodes (Document 2) v1.0 (WSDL + PDF 25 pages, rev1.3 du 01-07-2025)

**Fichiers produits** :
- `specs/03_formation_population_v1.md` — spécification complète
- `specs/04_formation_periodes_v1.md` — spécification complète
- `specs/00_REGISTRE.md` — registre enrichi (Organisation_v1.xsd, codes erreur Doc 1/Doc 2)

**Découvertes clés** :

- **Document 1 (Population)** : 3 opérations (Lire, Modifier, Approuver)
  - Utilise `Common_v1.xsd` (comme Formations Liste, pas Common_v2)
  - Nouveau XSD `Organisation_v1.xsd` (namespace `/organisation/v1`) avec `OrganisationReqIdCT`
    (sans implId) et `OrganisationResIdCT` (avec implId optionnel)
  - Population par année d'étude : 20 champs en réponse, 10 en requête (Save)
  - 4 champs obsolètes (`nbEleveFse`, `nbElevePi`, `nbEleveTotFse`, `nbEleveTotPi`)
  - 2 switchs d'approbation : `swAppPopD1` (école/PO) + `swAppD1` (administration)
  - Contrôles de cohérence riches (codes 4004-4012)
  - Divergence PDF/XSD : `implId` dans `OrganisationResIdCT` marqué obligatoire dans le PDF
    mais `minOccurs="0"` dans le XSD

- **Document 2 (Périodes)** : 2 opérations seulement (Lire, Modifier — PAS d'Approuver)
  - Structure plus complexe : activités d'enseignement + interventions extérieures + périodes
  - Tables de valeurs riches : `coCategorie` (30 codes), `coCatCol` (15 codes actifs, 2 supprimés),
    `coObjFse` (50+ codes dont beaucoup dépréciés)
  - Nouveau code `coCatCol "J"` (Réorientation 7TQ/7P) → nécessite `coObjFse "OA"` obligatoire
  - Un seul switch d'approbation (`swAppD2`) vs deux dans Document 1
  - Types float pour les périodes (pas int)

- **XSD partagés** : tous identiques entre Document 1 et Document 2, et identiques aux sessions 1-2
  pour les fichiers communs (AnneeScolaire, Etablissement, ResponseStatus, requestId, Common_v1,
  Addressing_v2, Authorisation_v2)

- **Observation workflow** : Document 1 a une opération Approuver, Document 2 non. L'approbation
  semble gérée côté administration pour Document 2 (erreur 1530 = déjà approuvé). Le workflow
  inter-documents reste à confirmer en session 4 (Document 3).

---

### Session 4 — 2026-06-02 : Document 3 (Attributions) v1

**Services analysés** :
- ✅ EPROM Formation Document 3 (Attributions) v1.0 (WSDL + PDF 22 pages, rev1.3 du 01-05-2023)

**Fichiers produits** :
- `specs/05_document3_v1.md` — spécification complète
- `specs/00_REGISTRE.md` — registre enrichi (types Doc3, codes erreur Doc3, traçabilité XSD)

**Méthode PDF** : la couche texte native du PDF était exploitable (`pdftotext -layout`) → extraction
complète du texte ; rendu en image (`pdftoppm`) des pages à diagrammes (8, 9, 10, 14, 15, 22) pour
vérification visuelle. L'OCR n'a pas été nécessaire pour ce manuel.

**Découvertes clés** :

- **2 opérations** : LireDocument3, ModifierDocument3 — **pas d'Approuver** (comme Document 2).
- **SOAP 1.1 UNIQUEMENT** : confirmé par le binding WSDL (`wsdl/soap/`, pas de `soap12/`) **et** par le
  PDF (§2.2). Particularité vs Organisation v7 (SOAP 1.1 ou 1.2).
- **Pattern Common_v1** (ancien), bloc retour `AbstractExternalResponseType` — comme Doc 1/Doc 2/Liste v2.
- **Modèle hiérarchique** : Document 3 → `activite` (branches, `[1..*]` en écriture) → `enseignant`
  (attributions). C'est « qui enseigne quoi et combien de périodes ».
- **Pas de switch d'approbation** dans `FormationDocument3CT` (ni `swApp*`). L'approbation du Doc 3 n'est
  pas gérée par ce service.
- **⭐ WORKFLOW INTER-DOCUMENTS CONFIRMÉ** (erreur `20102`) : « Les "**Doc A**" et "**Doc 2**" doivent être
  approuvés pour pouvoir accéder au "Doc 3" ». → Doc 3 inaccessible tant que Population (« Doc A » =
  vraisemblablement Document 1) **et** Périodes (Doc 2) ne sont pas approuvés. ⚠️ Le libellé est
  littéralement « Doc A » (couche texte native, page 22, pas OCR) ; le mapping « Doc A = Document 1 »
  reste à confirmer formellement avec l'ETNIC.
- **Contrôles de plafond** : les périodes attribuées (Doc 3) ne peuvent dépasser les périodes organisées
  au Doc 2 (IE comprise) — erreurs `1538` (par branche), `1574` (total), `1575` (CG), `1576` (CP).
- **`coCategorie`** : table **identique** au Document 2 (30 codes) → référentiel partagé confirmé.
- **`coCatCol` / `typeInterventionExterieure "J"`** : **sans objet** pour le Doc 3 (pas d'intervention
  extérieure propre ; le Doc 3 n'en voit que l'effet agrégé sur les plafonds).
- **2 nouvelles tables** : `coDispo` (~60 codes de disponibilité) et `teStatut` (7 codes : C/P/A/D/E/X/T),
  toutes deux « validées hors contrat XML » (contrôle métier, absentes du XSD).
- **9 divergences PDF ↔ XSD** recensées, dont :
  - `implId` (`OrganisationResIdCT`) : PDF « obligatoire » vs XSD `minOccurs="0"` — **même divergence
    qu'en session 3**, confirmée sur les 3 documents (le diagramme UML, lui, affiche bien `[0..1]`).
  - `nbPeriodesPrevuesDoc2` / `nbPeriodesReellesDoc2` : PDF « float obligatoire » vs XSD « int `[0..1]` » ;
    de plus le flux réel sérialise « 24.0 » → risque de `ValueError` avec un parseur int strict (zeep).
  - `coNumAttribution` (`Doc3EnseignantDetailSaveCT`) : **présent au XSD, absent du texte PDF** → permet
    de cibler une attribution existante.
  - `coNumBranche`/`noAnneeEtude`/`enseignantListe` (Save) : facultatifs au PDF, obligatoires au XSD.
- **8 XSD partagés byte-for-byte identiques** à la session 3 (vérifié par `diff`).

---

### Session 5 — 2026-06-02 : Formation Droits d'Inscription (Document 1D) v1.0

**Services analysés** :
- ✅ EPROM Formation Droits d'Inscription v1.0 (WSDL + PDF 23 pages, rev1.1 du 01-05-2023)

**Fichiers produits** :
- `specs/06_formation_droits_inscription_v1.md` — spécification complète
- `specs/00_REGISTRE.md` — registre enrichi (types Document1D, codes 1545/1546/1530, mapping des 4 statuts, traçabilité XSD)

**Méthode PDF** : couche texte native exploitable (`pdftotext -layout`, ~2750 c/page) ; rendu image
(`pdftoppm`, 300 dpi) des pages à boîtes UML repliées (5, 8, 9, 13, 14, 18). OCR non nécessaire. Les boîtes
UML ont permis de **trancher les coquilles de typage du texte** (types `string` vs « int »/« boolean »).

**Découvertes clés** :

- **« Document 1D » = service Droits d'Inscription** (radical interne `Document1D`/`Doc 1D`, « D » = Droits).
  Pendant « droits d'inscription » de la famille Document 1. Gère **par année d'études** : la **population
  scolaire au 5/10ᵉ** de la formation (`nbEleves5ieme`) **et** les **montants des droits** (`mtDroitsInscription`).
- **3 opérations** : LireDocument1D, ModifierDocument1D, **ApprouverDocument1D** — comme le Document 1
  (Population), contrairement à Doc 2 / Doc 3 (Lire+Modifier seulement).
- **SOAP 1.1 UNIQUEMENT** : confirmé par le binding WSDL (`wsdl/soap/`, pas de `soap12/`) **et** le PDF (§2.2).
  Comme le Document 3.
- **Pattern Common_v1** (ancien), bloc retour `AbstractExternalResponseType`. Type de réponse
  `Document1DReponseCT` **partagé par les 3 opérations**.
- **Deux switches d'approbation** dans la ligne : `swAppPopD1D` (école/PO) + `swAppD1D` (administration) —
  **parallèle exact au Document 1** (`swAppPopD1`/`swAppD1`), avec suffixe « D ».
- **⭐ Règle métier des deux phases** (PDF §3.1.4.1) : `nbEleves5ieme` modifiable *jusqu'à* l'approbation de
  la population (école/PO) ; `mtDroitsInscription` modifiable *seulement après*. `ApprouverDocument1D` pose
  `swAppPopD1D=1` et fait basculer la ligne en phase 2. Verrou final = approbation administration (`swAppD1D`,
  non exposée par ce service). Erreurs associées : `1546` (avant appro.), `1545` (déjà approuvé), `1530`
  (admin a verrouillé), `00011` (concurrence sur `nbEleves5ieme` à l'approbation).
- **⭐ `statutDocumentDroitsInscription` (point d'attention) résolu** : ce champ de `OrganisationApercuCT`
  (Formations Liste) **= ce service Doc 1D**. La vue Liste expose **4 statuts** : Organisation /
  Population+Périodes (Doc 1 + Doc 2) / **Droits d'Inscription (Doc 1D)** / Attributions (Doc 3). Le Doc 1D
  a donc son **propre statut**, distinct de Population+Périodes.
- **« Doc A » (point d'attention)** : **non mentionné** dans ce manuel (0 occurrence). L'hypothèse session 4
  (« Doc A » = Document 1 / Population) reste inchangée. Nomenclature interne consolidée : Doc 1 (Population),
  **Doc 1D (Droits)**, Doc 2 (Périodes), Doc 3 (Attributions), Doc 8bis (réf. Doc 3). **Pas d'erreur `20102`** :
  aucune dépendance inter-documents bloquante déclarée pour le Doc 1D (gérable indépendamment).
- **Coquilles de typage du PDF tranchées par l'UML + XSD** : `coAnnEtude` = `string` (pas « int »),
  `tsMaj`/`teUserMaj` = `string` (pas « boolean »), `nbEleves5ieme` (Approuver) = **obligatoire** (pas
  « facultatif »). `mtDroitsInscriptionOccupationnel` = « n'est plus utilisé ».
- **Pas de divergence de type numérique** (contrairement au Doc 3 et ses « 24.0 » sur `int`) : `nbEleves5ieme`
  est un vrai `int`, les montants des `float` déclarés. Aucun risque de `ValueError` zeep.
- **Réutilisation de codes entre services** : `1545`/`1114`/`2106` ont un libellé différent ici qu'au
  Doc 1/2/3 → indexer les exceptions pyetnic par **(service, code)**.
- **8 XSD partagés byte-for-byte identiques** à la session 4 (diff). `Organisation_v1.xsd` identique aussi à
  la session 3. Référentiel technique stable sur les 5 services.

---

### Session 6 — 2026-06-05 : Circulaire 9589 (rentrée 2025-2026, personnel EA)

**Document analysé** :
- ✅ Circulaire 9589 du 19/09/2025 — rentrée scolaire 2025-2026 des MDP, Enseignement pour
  Adultes (`circulaires/53089_0000.pdf`, 356 p. PDF = 293 p. + annexes A1-A36). Texte natif
  (pas d'OCR nécessaire). Abroge la 9343 du 24/08/2024.

**Fichiers produits** :
- `specs/07_circulaire_9589_contexte_personnel.md` — contexte métier « personnel/paie » :
  acteurs (PR/PO/MDP), identifiants (ECOT vs FASE, matricule, NISS/NISS bis), calendrier
  2025-2026, échéancier de paie, écosystème applicatif (GEDI-PRO/**GEDI-WS**, GESP,
  Mon Espace, DIMONA/DDRS, CAMMAT, VALEXU, Primoweb), sigles, annexes.
- `specs/08_circulaire_9589_ea12_attributions.md` — modèle EA12/EA12bis/EA12ter (demande de
  mise en liquidation) : structure des documents, référentiel des types d'événement, ligne
  d'attribution, situations administratives, codes DI, régimes de titres (RTF), dénominateurs
  de charge, EPT/CQ/CF/RRF, plafonds experts, codes RTF/RL10/FADI, cumul, règles de validation.

**Découvertes clés (jonctions avec les specs EPROM)** :
- **Code U.E. de l'EA12 (« 9 chiffres et 2 lettres ») = `codeFormation` EPROM** (ex. `761001U31C1`).
- **Matricule enseignant** (11 positions : sexe + date naissance inversée AAMMJJ + 4 chiffres)
  = `noMatEns` du Doc 3 (l'exemple `28208171112` de la spec 05 se décode : femme, 17/08/1982, n°1112).
- **Codes DI** de la circulaire ≈ table `coDispo` du Doc 3 (même univers, la circulaire ajoute
  la sémantique rémunéré/non rémunéré et le classement thématique).
- ⚠️ **Faux ami** : situation administrative EA12 (D/Z/V/S/I/St/P/R/A/T/M) ≠ `teStatut` Doc 3
  (C/P/A/D/E/X/T) — deux tables distinctes malgré le recouvrement partiel (D, T).
- L'EA12 référence les **documents 2 et 8/8bis** (classification CLA, intitulés de cours) —
  les mêmes que `nbPeriodesPrevuesDoc2`/`nbPeriodesReellesDoc2`/`nbPeriodesDoc8` du Doc 3.
- **Terminologie officielle** : « Enseignement pour adultes » remplace « promotion sociale »
  (D.-27/03/2025, MB 08/04/2025) — à refléter dans la doc utilisateur pyetnic (les identifiants
  techniques EPROM/PS restent inchangés).
- **GEDI-WS** : canal web service officiel pour transmettre les documents personnel depuis une
  application locale (ProEco, CREOS, EPHEC connectés) — monde distinct des services EPROM.
- Incohérence interne relevée : RL10 coordinateur qualité = `384` (p.152) vs `394` (p.224).

**Portée** : analyse cadrée « complément de contexte pyetnic » (pas d'app de gestion du
personnel visée). Les grandes tables RTF/RL10/FADI (≈ 480 fonctions, p.212-225) sont
décrites structurellement, extraction CSV possible ultérieurement si besoin.

---

### Session 7 — 2026-06-09 : Famille SEPS (Étudiants & Inscriptions) + circulaire 9593 + référentiels

**Services analysés** (5 — nouvelle famille **SEPS**, Enseignement pour Adultes) :
- ✅ SEPS Recherche Étudiants v1 (release 2.1.9) — `lireEtudiant`, `rechercherEtudiants`
- ✅ SEPS Sauvegarde Étudiant v1 (2.1.9) — `enregistrerEtudiant`, `modifierEtudiant`
- ✅ SEPS Enregistrer Inscription v1 (2.1.9) — `enregistrerInscription`, `modifierInscription`
- ✅ SEPS Recherche Inscriptions v1 (2.1.9) — `rechercherInscriptions`
- ✅ SEPS Notifications v1 (release 1.0.8) — `lireNotifications`

**Documents fonctionnels** :
- ✅ Circulaire **9593** du 23/09/2025 (dossier personnel, registre matricule, DI, présences ; 34 p. ; abroge 9350)
- ✅ Référentiels **Codes_Pays.xls** (260) + **INS_communesNais200723.xlsx** (communes INS)

**Fichiers produits** :
- `specs/09_seps_recherche_etudiants_v1.md` … `specs/13_seps_notifications_v1.md` (5 specs services)
- `specs/14_circulaire_9593_dossier_personnel.md` + `specs/15_referentiels_seps.md`
- `specs/referentiels/codes_pays.{csv,json}`, `codes_communes_ins.{csv,json}`, `codes_communes_ins_actives.csv`
- `specs/00_REGISTRE.md` — **section 7 « Famille SEPS »** ajoutée

**Méthode PDF** : manuel SEPS (67 p.) **texte natif** exploitable (`pdftotext -layout`, ~5000 c/page) — pas d'OCR. Rendu image (`pdftoppm` 150 dpi) des pages à diagrammes UML 8/11/12 → confirment le XSD.

**Découvertes clés** :

- **Famille distincte d'EPROM** : auth **WS-Security X.509** (pas UsernameToken), **SOAP 1.1 only**, namespaces `ws.etnic.be/seps/…`, bloc retour `AbstractExternalResponseType` en **`external/v1`** (forme identique à Common_v1, autre namespace). `ResponseStatus_v3`/`requestId_v1` byte-for-byte identiques à EPROM.
- **Identité étudiant** : `cfNum` (numéro Communauté française, pattern `[0-9]{1,10}-[0-9]{2}`) ; double signalétique **`rnDetails`** (Registre National/BCSS) vs **`cfwbDetails`** (établissement). NISS + **NISS bis** (createBisFlag → PUBLISHPERSON).
- **2 niveaux d'erreur** : SOAP Fault technique (`SECU-*`/`ROUT-*`/`VALI-*`) ≠ erreur métier (`success=false` + messages). **Codes métier non universels** (`30042` a 2 sens) → indexer par (service, code). Absence de résultat souvent en **warning + success=false**.
- **Inscription très riche** : `SpecificiteDataType` (regulier1/5, droitInscription/DI, droitInscriptionSpecifique/DIS hors-CEE, FSE, admission, sanction). ~16 énumérations métier documentées (MotifExemption C01-C07, MotifExemptionSpec C01-C13, admission/titre/sanction…).
- **Référentiels** : `codePays`/`codeNationalite` = code INS **5 chiffres** (`CO_ONSS_ID`/`CO_NATIO_ID`, Belgique=00150) ; `localite.code` = INS commune 5 chiffres (obligatoire si belge). Extraits en CSV/JSON.
- **Jonctions** : `regulier1`/`regulier5` ↔ comptage 1/10ᵉ-5/10ᵉ (circulaire) ↔ Doc 1 EPROM ; `MotifExemption` ↔ exemptions DI circulaire ; colonnes 7/7'' du Doc 1 = `nbEleveDem`/`nbEleveExm`.

**Divergences XSD ↔ PDF recensées** (≈ 15) — détail dans chaque spec : host endpoint (ws-tq vs services-web) ; `rnDetail(s)`/`cfwbDetail(s)` ; champs réponse hors XSD (`rnValidityEndDate`, `codeEtatCivil`) ; `anneeScolaire`/`ue`/`specificite` (minOccurs=0 vs obligatoires) ; `SpecificiteDataInputType` type mort ; `StatutFinFormationType` C01-C06 vs 01-06 ; `NotificationDescriptionType` enum incomplet (pas de « STATUT ») ; `forceRnFlag`/`forceRn` ; `dateRequete`/`dateRequest` ; réponse `etudiant` vs `etudiantDetails` ; `codeNationalite` BE vs 00150.

**Points à confirmer ETNIC** : host endpoint à retenir ; mapping fin `MotifExemption ↔ libellés circulaire` ; comportement code `08` (changement statut) sans description enum ; périmètre DIC (hors SEPS).

---

### Session 8 — 2026-06-10 : Circulaires légales (DI, calendrier, hybride, renseignements annuels)

**Documents analysés** :
- ✅ Circulaire **9217** du 03/04/2024 (DI 2024-2025) — texte intégral via miroir ICC Bruxelles
  (Gallilex/enseignement.be bloquent l'accès automatisé — WAF ; PDF Gallilex téléchargés manuellement
  dans `circulaires/`)
- ✅ Circulaire **9488** du 16/04/2025 (DI 2025-2026) — montants via synthèse GHA-WBE
- ✅ Circulaire **9731** du 27/05/2026 (DI **2026-2027**, en vigueur) — `circulaires/53231_0000.pdf`
- ✅ Circulaire **9487** du 16/04/2025 (calendrier EA 2025-2026, dotation) — `circulaires/52387_0000.pdf`
- ✅ Circulaire **8829** du 01/02/2023 (enseignement hybride, AGCF 21/12/2022) — `circulaires/50609_000.pdf`
- ✅ Circulaire **8684** du 16/08/2022 (**Renseignements annuels** : instructions d'encodage EPROM,
  toujours en vigueur) — `circulaires/49854_000.pdf` (90 p.)

**Fichiers produits** :
- `specs/16_circulaires_droit_inscription.md` — formule DI (forfait + tarif×min(p,800), montants
  2024→2027), assiette (dossier pédagogique, 1ᵉʳ dixième), exonérations ↔ `MotifExemptionType`,
  recalcul global multi-établissements + remboursement, arrondi, règle Doc 1D « constaté ≠ perçu » (9731)
- `specs/17_circulaire_9487_calendrier_dotation.md` — année académique, congés, **100 % planifiés /
  90 % dispensés**, dotation par année civile (découpage 16+24 semaines), numérotation des semaines
- `specs/18_circulaire_8829_hybride.md` — hybride : organisation distincte, neutralité dotation/DI,
  bascule 48 h, **« DOC A » = déclaration d'ouverture**
- `specs/19_circulaire_8684_renseignements_annuels.md` — instructions complètes Doc A/1/2/1D/3 :
  sémantique des colonnes, règles de cohérence, lignes 91-96, regroupements, IE, échéancier
- Renvois croisés ajoutés dans `02`, `03`, `04`, `05`, `06`, `11` ; registre (`20102`) mis à jour

**Découvertes clés** :
- ⭐ **« Doc A » = document Organisation (déclaration d'ouverture EPROM)** — confirmé deux fois
  (8829 §Encodage du Document A ; 8684 §2.1 « Déclaration d'organisation DOCUMENT A »). Hypothèse
  « Doc A = Doc 1 » des sessions 4-5 **corrigée** ; chaîne `20102` : Organisation + Doc 2 approuvés
  → Doc 3.
- ⭐ **Les web services EPROM (Doc A, 2, 1D, 3) sont officiellement documentés** dans la 8684 comme
  canal pour les applications de gestion (ENORA, GIPS, PROSOC…).
- **Règle 100 %/90 %** (9487) : prévu Doc 2 = 100 % du Doc 8bis ; réel ≥ 90 % (CO/VH réputées
  dispensées, pas VA/VD/VP/VE) → explique `nbPeriodesPrevuesDoc2`/`nbPeriodesReellesDoc2`.
- **Dotation gérée par année civile** (16+24 semaines) → explique la ventilation an 1 / an 2 des
  périodes du Doc 2 (`nbPerAn1`/`nbPerAn2`).
- **Règles de multiples** (8684) : réel = multiple entier du prévu ; total = multiple entier **ou
  entier-et-demi** du Doc 8bis (→ les périodes sont des `float`) ; encadrement = effectif ×
  périodes/étudiant ; total 18+19 = plafond des attributions Doc 3 (`1574`).
- **Recalcul global du DI** multi-établissements avec obligation de remboursement → helper pyetnic
  sur l'ensemble des inscriptions de l'année. Assiette DI = dossier pédagogique, pas le Doc 2.
- **DI 2026-2027** : 34 € / 0,30 (sec) / 0,47 (sup), plafond 800 ; nouvelle exonération boursiers
  BES AeSI ; VA désormais régie par la circ. **9447** (25/02/2025).
- Lignes spéciales Doc 2 : 91-94 valorisation (92/94 encodables jusqu'au 31/10 N+1 après
  approbation !), 95 expertise (≥40 p./chargé de cours), 96 suivi pédagogique (sans DI ni population —
  Doc 1/1D à valider vides).
- Échéancier : Doc A ≤ 5 j ouvrables ; Doc 1+2 ≤ 35 j (1ᵉʳ dixième) ; Doc 1D ≤ 25 j (5ᵉ dixième) ;
  Doc 3 ≤ 35 j (approbation Doc 2).

**Points restants** : « colonnes A et B » du Doc 1 (réf. des circulaires DI) non élucidées (annexes 7-8
de la 8684 = manuels HOD/CICS-EPROM à dépouiller au besoin) ; test TQ du déclencheur `20102` ;
mapping fin exonérations ↔ C01-C07 ; circulaires connexes non traitées : 9448 (inclusif, périodes
complémentaires), 9447 (VA), 6351 (activités de formation), 4462/6677 (conventions).

---

### Session 9 — 2026-06-10 : Exploration de l'application EPROM Web (lecture seule)

**Méthode** : navigation dans l'application de production (`EPROM_WEB` 2.12.0, IBM Faces) via Chrome
piloté en JavaScript (les boutons exigent des séquences de `MouseEvent` réels ; notes techniques
complètes dans la spec 20 §3). Compte école EICA, année 2024-2025, formation témoin 157.

**Fichier produit** : `specs/20_exploration_ui_eprom.md` + mises à jour specs 05/16/19.

**Confirmations / résolutions** :
- ⭐ **Doc A définitivement confirmé** = l'organisation : tableau « DOCUMENTS ANNUELS » de l'UI
  (Doc A / Doc 1 et 2 / Doc 1D / Doc 3 avec statuts « Approuvé » / « Encodé école » = `StatutCT`).
  « Doc 1 et 2 » = une entrée à 2 statuts → cohérent avec `statutDocumentPopulationPeriodes` unique.
- ⭐ **« Colonnes A et B » résolu** : colonnes UI « Elèves A » (col 2) / « Elèves B » (col 5) du Doc 1.
- ⭐ **Référentiels `teStatut` et `coDispo` extraits avec libellés** depuis les listes déroulantes du
  Doc 3 (60 codes dispo ; 7 statuts ACS/ACS DP/Déf. Accessoire/Définitif/Expert/eXpertise/Temporaire).
- Tuple `(O - O - O - O - E)` de la liste = statuts des 5 documents (A, 1, 2, 1D, 3).
- Champs UI = mapping 1:1 avec `FormationOrganisationCT` (dont « conseiller en prévention ou DPO »),
  `Doc3ActiviteDetailCT`/`Doc3EnseignantDetailCT`, colonnes 12-19 du Doc 2 ventilées **par année
  civile** dans les en-têtes (« Prévue 2024 / Prévue 2025 / Réel 2024 / Réel 2025 »).
- **Lignes 97-99 du Doc 2** découvertes (97 PeSu périodes suppl., 98 PSup part supplémentaire,
  99 CEtu conseil des études) — absentes de la 8684.
- Onglet IE : périodes par année civile en 3 lignes « Cas généraux / Cas particuliers / Suppléments ».

---

### Session 9bis — 2026-06-10 : Calcul de l'encadrement et de la dotation de périodes (spec 21)

**Déclencheur** : question utilisateur — pyetnic peut-il calculer la dotation d'une école à partir de ses chiffres ?

**Fichier produit** : `specs/21_calcul_encadrement_dotation.md`.

**Découvertes clés** :
- ⭐ **Deux grandeurs distinctes** (précision utilisateur) : **encadrement** (équipe administrative) = sur
  **périodes-élèves (PE)** ; **dotation de périodes** (rémunération enseignants) = **PE *pondérées*** (coefficients par catégorie).
- **Aucun service SOAP analysé** ne renvoie la dotation/encadrement (vérifié : 0 champ `dotation/encadrement/NTPP`
  dans WSDL/XSD). La **dotation de base** est communiquée par l'administration (juillet, par année civile ;
  consultée historiquement via HOD/CICS « pot K », écran 59).
- **Cadre du calcul localisé** : décret 16/04/1991 **art. 82-93, 102, 111 §1, 115** ; **arrêté GCF 22/11/2002**
  (ajustements) ; **arrêté 09/07/2004** + circ. **5447** (part d'autonomie ≈ 20 %) ; circulaires **PS 327/96**
  (calcul PE + cas particuliers encadrement), **PS 402/03** (ajustements), **PS 357/98 / 422/06** (expertise,
  périodes suppl.) ; le tout recensé par la circulaire-**répertoire 2816 du 13/07/2009**.
- **Décret coordonné déposé et analysé** (`circulaires/16184_0036.pdf`, MAJ 19/12/2025, 71 p., texte natif) →
  **verbatim confirmé** : **PE = périodes réellement organisées × élèves réguliers, sommées** (art. 99) ;
  **catégories A (sec. sup.) / B (sec. inf.) / C (supérieur)** (art. 83) = axe de pondération ; norme
  **30 000/40 000 PE** (art. 100, « autonomie de l'établissement », ≠ part d'autonomie du dossier péda) ;
  période **50 min** (art. 82) ; dotation **par année civile** (art. 86) ; **déductions** (art. 87bis) ;
  **réserve + dépassement 1,5×** (art. 91/93) ; **plafond 10 %** activités hors cours, **≤ 1 %** formation (art. 91/6) ;
  expertise **40-800 périodes** (art. 91/4) ; **supplément suivi pédagogique** 100/200/300/400/500 **périodes B**
  selon PE générées (30k/120k/240k/360k/500k, art. 36 §2 — ⚠️ corrige une table provisoire erronée).
- ⭐ **Arrêté GCF 22/11/2002 obtenu** (numac 2003029045, version coordonnée Justel 18/08/2025) → **table de pondération
  verbatim** : coef. pédagogique **1 / 1,6 / 2,8** × coef. niveau **B=1 / A=1,25 / C=1,5 / D=1,8** ; PE pondérées en
  6 étapes (cas généraux / part d'autonomie au prorata / organique / cas particuliers / neutralisation augmentations /
  dépassements) ; ajustement par **intervalle de neutralisation ±8 %**, baisse plafonnée à **50 périodes**, redistribution
  au prorata (enveloppe fermée). Base = **avant-dernière année civile** ; dotation de référence = année précédente.
- **Faisabilité pyetnic** : le calcul est désormais **entièrement spécifié** → simulateur/vérificateur complet ; seul
  intrant non récupérable par service = la **dotation de référence** (communiquée par l'administration). Recommander un
  module « financement » paramétrable par millésime (coefficients, ±8 %, plafond 50, plafonds 10 %/1 %).

- **Table de pondération figée** : `referentiels/coefficients_ponderation_coCategorie.csv` — 30 codes `coCategorie`
  (spec 04) → coefficient pédagogique (1 / 1,6 / 2,8), croisés avec l'arrêté art. 3 (15 cas généraux ; 1 autonomie ;
  12 cas particuliers à la moyenne PEP/période ; 2 à confirmer : `PSup`, `PRET`).

**Points mineurs restants** : catégorie « D » du barème (1,8) vs « D » abrogé du décret en 2021 (à clarifier) ;
taux exact part d'autonomie (arrêté 09/07/2004) ; `coCategorie` `PSup`/`PRET` (2/30) ; modèle d'annexe de l'arrêté. **Aucun bloquant.**
PDF arrêté : `ejustice.just.fgov.be/img_l/pdf/2002/11/22/2003029045_F.pdf` (à déposer dans `circulaires/` si souhaité).

---

### Session 9ter — 2026-06-11 : Test prod — UE hors PEP 2024-2025 (limitation organique, Doc 2)

**Déclencheur** : question utilisateur — quelles UE ne sont pas comptabilisées pour les PEP en 2024-2025 ?

**Test prod (lecture seule, étab 3052)** : `lister_formations` + `lire_organisation` + `lire_document_2`
sur les **123 organisations** de 2024-2025 (110 formations). Scripts jetables `/tmp/pep_*.py`.

**Résultats** :
- **45/123 organisations** financées hors dotation (toutes avec `interventionExterieure50p = true`) :
  **32 Convention (C)**, **9 Publics infra-scolarisés (I)**, **3 Validation des compétences (V)**,
  **1 Fonds Européens (F)** — soit **3 691,5 périodes IE** sur 7 986,5 prévues déclarées.
- ⭐ **Cohérence parfaite** flag organisation (`typeInterventionExterieure`) ↔ lignes IE du Doc 2 :
  zéro divergence sur 123 organisations (le flag est un résumé fiable des lignes IE).

**Patterns d'encodage Doc 2 découverts (constat prod, à généraliser avec prudence)** :
1. **IE totale (« miroir »)** : total périodes activités = total périodes IE (ex. 490 : 120 = 120) → UE
   entièrement hors dotation, zéro PEP.
2. **IE partielle 50 %** (395, 396, 568) : `nbTotPeriodeReelle = nbTotPeriodePrevue − périodes IE`
   (ex. 395 : 30 prévues, 15 IE, 15 réelles) → 🔶 hypothèse : les **périodes réelles** du Doc 2 ne
   comptent que la **part dotation** ; les périodes IE vivent uniquement sur leurs lignes propres.
3. **Placeholder** (403/4·7, 455/3-6, 510/3-4, 511/3, 528 — VC et conventions) : activités déclarées à
   **0,5 ou 1 période symbolique**, tout le volume réel porté par les lignes IE (ex. 455/3 : 0,5 prévue,
   300 IE) → ⚠️ le total activités du Doc 2 **n'est pas une assiette fiable** seul ; toujours croiser
   avec `interventionExterieureListe`.
4. **IE composite** : 518/org1 a `typeInterventionExterieure = F` mais **deux lignes** Doc 2
   (`F/WL` = 105 + `K/PR` = 105) → le flag organisation ne reflète que le type dominant.

**Impact spec 21** : note de lecture ajoutée à l'étape 3 (limitation organique) — l'exclusion des
périodes hors dotation est calculable par organisation via les lignes IE du Doc 2.

**Suite (même session) — premier calcul PEP complet, année civile 2025** (`rapport_pep_2025.md`) :
chaîne spec 21 exécutée de bout en bout sur la prod (lecture seule, 207 organisations des années
scolaires 2024-2025 + 2025-2026). Assiette civile 2025 = réelles An2 (24-25) + réelles An1 (25-26).
⭐ **Coefficient de niveau dérivable du `codeFormation`** (segment `Uxx` : U1x → B, U2x → A, U3x → C —
validé sur 971111U21D2 « ESS »). Résultat : **102 175 PEP** (73 104 cas généraux + 17 312 autonomie +
11 759 cas particuliers à la moyenne 18,40 PEP/période ; 4 913,5 périodes organiques ; 54 409 PE).
Aucun `PSup`/`PRET` rencontré. Limites consignées dans le rapport (élèves = `nbEleveC1`, DI non payé
non exclu, prévu vs réel art. 4, étapes 5-6 hors API).
⭐ **Règle de calcul confirmée par l'utilisateur (organisations bi-annuelles)** : le prorata de la part
d'autonomie se base sur la **structure du dossier pédagogique** (`nbPeriodeBranche` des cas généraux),
pas sur la tranche civile — cas 510/org1 2024-2025 (08/04/2024 → 28/01/2025, `org2AnneesScolaires`) :
58 pér. CTln réelles en civil 2024, 24 pér. d'autonomie en civil 2025 → les 24 héritent du coef CTln
(1,6 × 1,25) bien qu'aucun cours général ne tombe en 2025.

⭐ **Écrans officiels HOD identifiés (captures utilisateur, 11/06/2026)** : transaction `MENP052`,
écrans **57L** (`PMM5DM1`, liste PE par année civile 2018-2027) et **57D** (`PMM5EM1`, détail par
école — PE, chef d'atelier, emplois calculés dir./s-dir./surv./chef at., régimes « anciens »/« new »).
PE officielles EICA 2025 = **99 748** (chef at. 18 526) ; série complète dans `rapport_pep_2025.md`.
⚠️ PE (encadrement) ≠ PEP (dotation) — la proximité avec les 102 175 PEP calculées est fortuite.
**Validation** : reconstruction PE encadrement pyetnic (organique 57 772 + cas part. ≈ 3 521 +
IE ≈ 28 895) = **90 189 ≈ 90,4 % de l'officiel** ; écart attribué aux élèves des UE conventionnées
(absents du Doc 2 → croiser Doc 1/SEPS). Complète la mention « pot K écran 59 » de la spec 19.

🎯 **Écran 55L (« pot K ») extrait également** (`PMM5BM1`, « Liste dotations périodes par an. civile ») :
dotation organique initiale/utilisable/solde + **PEP référence/calculée/%** depuis 2018.
**PEP calculée officielle 2025 = 101 710 vs 102 175 pyetnic → +0,46 %** — la chaîne spec 21 est
**validée de bout en bout**. Mécanismes vérifiés exactement sur la série : décalage **N → N+2**,
neutralisation **±8 %** (2022/2023/2025), hausse 2026 = +3 pér. (enveloppe fermée, calc 2024 +9,77 %),
baisse 2021 = **¼ × 6 772 × 10,25 % = 174 pér.** (🔶 **plafond 50 non appliqué** — à clarifier),
référence re-proratisée à la dotation (98 586 × 6 601/6 598 ≈ 98 635). Prévision dotation 2027 :
inchangée (+3,12 % dans ±8 %). Série complète dans `rapport_pep_2025.md`.

⭐ **Écart PE encadrement expliqué** (capture UI Doc 2 web de la 490 + précision utilisateur) : les UE
conventionnées « miroir » portent bien leurs élèves (490 : 7 él. cohérents Doc 1/Doc 2/SEPS) ; les
**11 organisations VC/convention sans élèves** (455 VC ×5, 528/1, 403/7, 510/2+4, 546/1 — 1 005 pér.
IE 2025, aucune population Doc 1/Doc 2/SEPS, vérifié) sont des activités de type **EPT** : pas
d'élèves par nature → valorisées à la **moyenne PE/période** comme les cas particuliers.
Reconstruction corrigée : **100 748 PE (+1,0 % vs officiel 99 748)** avec la moyenne globale
(10,634 PE/pér.) — résidu ≈ DI non payés + arrondis. **Règle PE encadrement complète** :
PE = Σ(pér. × élèves) [lignes avec élèves, IE comprises] + (pér. réservées + pér. EPT) × moyenne.
⭐ Au passage, l'UI Doc 2 web (onglet Intervention extérieure) confirme **en prod** la table
`coCodePar` de la spec 04 (`CG`/`CP`/`SU`, ventilés par année civile) et l'équivalence des colonnes
UI avec l'annexe 8684 (col. 12-19, spec 19).

⭐ **Rapport hôte `ppm_1614` extrait** (« Documents 2 - Année scolaire 2526 », 27 p., 11/06/2026) —
vue mainframe des Doc 2 par UE/organisation, colonnes prévu/réel **ventilées par année civile**
(25/26/TOTAL) + élèves + flag `App`. **Données identiques au SOAP** (sondages : 537/1, 568/1, 396/1,
564/1 — exacts). Confirmations majeures :
1. **Réelles = part dotation, prouvé verbatim** : 568/1 (CTni 10→5, 6→3 ; Auto 9→4,5) et 396/1
   (20→10 ; Auto 4→2) — toutes les réelles = 50 % des prévues sur les UE convention mixtes ;
   réelles = 0 sur les conventions 100 % (qui gardent prévues + élèves).
2. **Placeholders = prévues d'EPT** : ligne 95, prévu symbolique (0,5/1) et **réel = volume effectif**
   (403/1 : 1,00 prévu → 160 réel dont 159 en civil 2026 ; 402/1 : 1 → 40).
3. **Sémantique `PRET` élucidée** : lignes « PRESTATION ETUDIANT (stage/EI) » en tête des UE
   stage/épreuve intégrée — heures prestées par l'étudiant, **toujours 0** chez EICA → relevé pour
   mémoire, pas de valorisation observée (CSV mis à jour, valorisation à confirmer).
4. **Numérotation standard des cas particuliers** : lignes **91-94** VAF/VANFI (`SEtu`), **95** `ExPT`,
   **96** `SEtu` admission/suivi/sanction, **97** `PeSu`, **98** `PSup`, **99** `CEtu` — correspond aux
   `coNumBranche` 91-99 renvoyés par le SOAP, gabarit présent sur toutes les UE.
5. **`App` = `swAppD2`** (O/blanc — les blancs correspondent exactement aux Doc 2 non approuvés).
6. 🔶 **537/1 (flag K)** : les 80 périodes « octroi cabinet-projets transversaux » apparaissent en
   **ligne 96 SEtu prévues** (= les 80 pér. du bloc IE K en SOAP) — mapping type IE → ligne cas
   particulier à creuser.

⭐ **Inventaire du menu hôte A5** (`PMM02M1`, « Année scolaire - Documents annuels ») — rapports
extractibles pour les sessions futures : 1 Documents annuels en attente d'encodage · 2 DI et DIO
encodés /école/formation · 3 Périodes utilisées /formation/école · **4 Doc2 : périodes organiques** ·
**5 Doc2 : EPT organiques** · **6 Int.Ext. : périodes organisées** · **7 Int.Ext. : EPT** ·
8 Organisations illicites · **9 IE /école/projet/année civile** · A Recherche **pots d'heures**/groupe
(fonction) · B Catalogue **pots d'heures**/groupe(fonction) · C Doc1 : population scolaire.
→ Le système distingue nativement **EPT organique** (5) et **EPT en intervention extérieure** (7) —
exactement la dichotomie identifiée pour l'écart PE ; les « pots d'heures » (A/B) sont la matérialisation
du « pot K » (spec 19). Extractions prioritaires : 4+5 (assiette organique PEP), 6+7+9 (valorisation IE,
résidu ~1 000 PE, mapping K→ligne 96), C (élèves comptabilisés / exclusions DI).

**Extractions reçues (suite, 11/06/2026 — les autres rapports vides ou indisponibles)** :
- ⭐ **`ppm_1613` (A55) « Périodes EPT » 2526** = la liste officielle des **EPT organiques** : 402/1
  (40 pér. réelles 2025) + 403/1 (1 pér. 2025 + 159 pér. 2026) — **exactement** l'assiette EPT 25-26
  du calcul pyetnic (41 pér. civil 2025 ✓). Attendu dans l'édition 2425 : 403/5 (179) + 403/6 (99)
  → total EPT organique 2025 = 319 = l'assiette « réservées » du rapport PEP. **Confirme aussi que
  les sessions VC/convention sans élèves ne sont PAS des EPT organiques.**
- ⭐ **`PPM_2002` « IE de type EPT » : vide même correctement relancé** → l'école n'a **aucune IE de
  type EPT** officiellement. Les sessions VC/convention sans élèves sont des **IE ordinaires (C/V/K)** ;
  la question du résidu PE (~1 000) se joue à la valorisation (élèves/moyenne), pas au classement.
- ⭐ **`ppm_2003` (B87) « Liste des Interventions Extérieures »** (éditions 2425 + 2526) — la vue
  officielle des blocs IE du Doc 2 : type (= `coCatCol`), **sous-cat (= `coObjFse`** : FO, WL, FP, SP,
  IN, PR), **agrément**, **projet global** (22516, 22976, 21651… = la « Référence » de l'UI), périodes
  an.1/an.2, classement par **niveau SI/SS**. **Réconciliation exacte** : IE civil 2025 = 1 982,5
  (an.2 éd. 2425) + 1 939,0 (an.1 éd. 2526) = **3 921,5 pér. = lecture SOAP à l'identique** (2 916,5
  avec élèves + 1 005 sans). Par type : C 2 554,5 · I 598 · F 289 · K 181 · V 299. Enseignements :
  (1) **le type d'IE est attaché au projet et à l'année scolaire** — 522/2, 523/3, 524/2 passent de
  `I` (FO 1096/21651) en 2425 à `C` (FO 1153/22550) en 2526 ; (2) **une UE peut cumuler deux types**
  (518/1 : F/WL **et** K/PR sur le même projet 18690 « 3-3111RE », 105 + 105 pér.) ; (3) K se décline
  en sous-cat SP (537/1) et IN (546/1).

**Décision d'architecture (validée par l'utilisateur)** : le moteur de calcul PE/PEP reste **hors de
pyetnic** (conforme spec 21 §7 — pyetnic = client SOAP fidèle, la logique réglementaire vivra dans un
projet dédié, p.ex. la future application école). Les scripts validés sont promus en **démonstrations**
dans `examples/` : `calcul_pep_annee_civile.py` (PEP d'une année civile + rapport markdown, reproduit
102 175,26 pour 2025 ✓) et `calcul_pe_encadrement.py` (PE encadrement, reproduit 100 747,6 ✓) —
paramétrés par année civile, prorata autonomie sur `nbPeriodeBranche`, niveau via `codeFormation`.
- ⭐ **Rapport 4 « Doc2 : périodes organiques » reçu pour 2425 + 2526** : c'est le `ppm_1614`
  (l'extraction précédente 2526 l'était déjà) — il ne contient **pas** le bloc IE, confirmant que
  « périodes organiques » = lignes d'activité du Doc 2. **Réconciliation exacte de l'assiette
  civile 2025** : officiel = 4 126,5 (réel25, éd. 2425) + 1 426,0 (réel25, éd. 2526) = **5 552,5 pér.
  organiques réelles** = **4 913,5 (cas généraux + autonomie) + 639 (cas particuliers) pyetnic — à
  la période près**. La couche d'entrée du calcul PEP est validée à 100 % ; le résidu PEP (+0,46 %)
  ne peut venir que de la pondération/arrondis officiels, plus de l'assiette. (Édition 2425 :
  EPT 403/5 = 1+179, 403/6 = 1+99 ✓ ; conventions 50 % : 395/396/568 réelles = moitié des prévues ✓.)
- ⭐ **`ppm_1544` « Documents 1 : Population scolaire par organisation »** (éditions 2425 + 2526) —
  vue Doc 1 + Doc 1D fusionnée : colonnes annexe 8684 (2)-(10'), **montants DI/DIO perçus par
  organisation** et **comptage au 5/10ᵉ** (`nb elv 5/10`). Enseignements : (1) les organisations
  **placeholder VC/convention n'apparaissent même pas** dans le rapport officiel (455/3-6, 510/3-4,
  528/1, 403/5-7 absents — cohérent avec Doc 1/SEPS vides) ; (2) les conventions « miroir » portent
  leurs élèves surtout en col. (8) « comptés plusieurs fois » ; (3) les organisations **bi-annuelles
  figurent dans les DEUX éditions** (157/2-2425 = 157/1-2526, mêmes dates) ; (4) totaux officiels :
  2425 = **1 285 comptés / 1 060 au 5/10ᵉ**, 2526 (partiel) = 647/550.

---

### Session 10 — (à planifier) : Synthèse + Architecture + Mock server

**À faire** :
- Synthèse cross-services (EPROM + **SEPS**)
- Architecture cible pyetnic v2 (gérer **2 familles** : auth UsernameToken EPROM **et** X.509 SEPS)
- Prototype mock server SOAP stateful
- Plan d'implémentation
- Intégrer les **référentiels** (pays/communes) comme données embarquées + helpers de validation

**Points à trancher / confirmer (hérités des sessions précédentes)** :
- **Mapping « Doc A »** : ✅ **résolu en session 8** (circulaire 8829, spec 18) — « Doc A » =
  **document Organisation (déclaration d'ouverture EPROM)**, pas le Document 1. Chaîne corrigée :
  Organisation (Doc A, `StatutCT` Approuvé) + Périodes (Doc 2, `swAppD2`) → Attributions (Doc 3) ;
  Population (Doc 1) et Droits (Doc 1D) = workflows propres non bloquants. Reste : test TQ de
  confirmation (approuver Organisation+Doc 2 sans Doc 1, appeler Doc 3). Nomenclature consolidée :
  Doc A (Organisation), Doc 1 (Population), Doc 1D (Droits), Doc 2 (Périodes), Doc 3 (Attributions),
  Doc 8bis (dossier pédagogique/horaire).
- **Divergences de type périodes** : décider de la stratégie zeep pour les champs `xs:int` recevant des
  valeurs « 24.0 » (Doc 3 : `nbPeriodesDoc8`, `nbPeriodesPrevuesDoc2`, `nbPeriodesReellesDoc2`).
  ⚠️ **Spécifique au Doc 3** : le Doc 1D n'a pas ce problème (`nbEleves5ieme` vrai `int`, montants `float`).
- **Switches d'approbation** : modéliser les états dans le mock server stateful (Doc 1 : `swAppPopD1`+`swAppD1` ;
  **Doc 1D : `swAppPopD1D`+`swAppD1D`** ; Doc 2 : `swAppD2` ; Doc 3 : aucun) pour tester la contrainte `20102`
  (Doc 3) **et** le workflow deux phases du Doc 1D (`1546`/`1545`/`1530`/`00011`).
- **Exceptions typées par (service, code)** : les codes ne sont **pas universels** (`1545`, `1114`, `2106`
  ont un sens différent selon le service — confirmé Doc 1D). Ne pas mutualiser un registre de codes global naïf.
- **Référentiels partagés** : centraliser `coCategorie` (Doc 2 + Doc 3) ; `coDispo`/`teStatut` (Doc 3) ;
  `coCatCol`/`coObjFse` (Doc 2) — « validés hors contrat XML » donc à maintenir côté client.
- **`FormationEpsocCT` (Formations Liste)** : type défini dans `Formation_v2.xsd` mais **non référencé** par
  les opérations de Formations Liste v2 ; ajoute un champ `dateFermeture` (date, optionnel) vs `FormationCT`.
  Identifier le service qui l'utilise réellement (note héritée de la session 1, non traitée depuis).

## Services EPROM identifiés (extranet ETNIC)

| Service | Version | Analysé | Spec produite |
|---|---|---|---|
| Formations Liste | 2.0 | ✅ session 1 | ✅ `01_formations_liste_v2.md` |
| Formation Organisation | 7.0 | ✅ session 2 | ✅ `02_formation_organisation_v7.md` |
| Formation Population (Document 1) | 1.0 | ✅ session 3 | ✅ `03_formation_population_v1.md` |
| Formation Périodes (Document 2) | 1.0 | ✅ session 3 | ✅ `04_formation_periodes_v1.md` |
| Document 3 (Attributions) | 1.0 | ✅ session 4 | ✅ `05_document3_v1.md` |
| Formation Droits Inscription (Document 1D) | 1.0 | ✅ session 5 | ✅ `06_formation_droits_inscription_v1.md` |

## Documents fonctionnels analysés (hors services SOAP)

| Document | Référence | Analysé | Spec produite |
|---|---|---|---|
| Circulaire de rentrée 2025-2026 — MDP Enseignement pour Adultes | 9589 du 19/09/2025 | ✅ session 6 | ✅ `07_circulaire_9589_contexte_personnel.md` + `08_circulaire_9589_ea12_attributions.md` |
| Circulaire dossier personnel étudiant / matricule / DI / présences (EA) | 9593 du 23/09/2025 | ✅ session 7 | ✅ `14_circulaire_9593_dossier_personnel.md` |
| Référentiels codes pays / nationalités / communes INS | Catalogue SOA ETNIC | ✅ session 7 | ✅ `15_referentiels_seps.md` + `referentiels/*.csv,json` |
| Circulaires DI annuelles (calcul, exonérations, déclaration) | 9217 / 9488 / 9731 | ✅ session 8 | ✅ `16_circulaires_droit_inscription.md` |
| Calendrier général EA + gestion dotation de périodes | 9487 du 16/04/2025 | ✅ session 8 | ✅ `17_circulaire_9487_calendrier_dotation.md` |
| Enseignement hybride (conditions, encodage Doc A) | 8829 du 01/02/2023 | ✅ session 8 | ✅ `18_circulaire_8829_hybride.md` |
| Renseignements annuels (instructions encodage EPROM Doc A/1/2/1D/3) | 8684 du 16/08/2022 | ✅ session 8 (annexes 7-8 partiellement) | ✅ `19_circulaire_8684_renseignements_annuels.md` |
| Calcul de l'encadrement & de la dotation de périodes (PE, pondération, autonomie) | décret 16/04/1991 art. 82-93 + arrêté 22/11/2002 + PS 327/96, 402/03 (répertoire 2816) | ✅ session 9bis (cadre ; verbatim à confirmer 🔶) | ✅ `21_calcul_encadrement_dotation.md` |

## Services SEPS identifiés (Étudiants & Inscriptions — Enseignement pour Adultes)

| Service | Contrat / release | Opérations | Analysé | Spec produite |
|---|---|---|---|---|
| SEPS Recherche Étudiants | external v1 / 2.1.9 | lireEtudiant, rechercherEtudiants | ✅ session 7 | ✅ `09_seps_recherche_etudiants_v1.md` |
| SEPS Sauvegarde Étudiant | external v1 / 2.1.9 | enregistrerEtudiant, modifierEtudiant | ✅ session 7 | ✅ `10_seps_enregistrer_etudiant_v1.md` |
| SEPS Enregistrer Inscription | external v1 / 2.1.9 | enregistrerInscription, modifierInscription | ✅ session 7 | ✅ `11_seps_enregistrer_inscription_v1.md` |
| SEPS Recherche Inscriptions | external v1 / 2.1.9 | rechercherInscriptions | ✅ session 7 | ✅ `12_seps_recherche_inscriptions_v1.md` |
| SEPS Notifications | external v1 / 1.0.8 | lireNotifications | ✅ session 7 | ✅ `13_seps_notifications_v1.md` |
