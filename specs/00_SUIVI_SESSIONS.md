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

### Session 8 — (à planifier) : Synthèse + Architecture + Mock server

**À faire** :
- Synthèse cross-services (EPROM + **SEPS**)
- Architecture cible pyetnic v2 (gérer **2 familles** : auth UsernameToken EPROM **et** X.509 SEPS)
- Prototype mock server SOAP stateful
- Plan d'implémentation
- Intégrer les **référentiels** (pays/communes) comme données embarquées + helpers de validation

**Points à trancher / confirmer (hérités des sessions précédentes)** :
- **Mapping « Doc A »** : confirmer formellement que le « Doc A » de l'erreur `20102` (Doc 3) = Document 1
  (Population). Le Doc 1D (session 5) **ne mentionne pas « Doc A »** → hypothèse inchangée. Nomenclature
  interne consolidée : Doc 1 (Population), Doc 1D (Droits), Doc 2 (Périodes), Doc 3 (Attributions), Doc 8bis.
  Reconstituer la chaîne d'approbation : Organisation → Population (Doc A/1) + Périodes (Doc 2) →
  Attributions (Doc 3) ; **Droits d'Inscription (Doc 1D) = branche indépendante** (pas de `20102`, workflow
  interne population→montants).
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

## Services SEPS identifiés (Étudiants & Inscriptions — Enseignement pour Adultes)

| Service | Contrat / release | Opérations | Analysé | Spec produite |
|---|---|---|---|---|
| SEPS Recherche Étudiants | external v1 / 2.1.9 | lireEtudiant, rechercherEtudiants | ✅ session 7 | ✅ `09_seps_recherche_etudiants_v1.md` |
| SEPS Sauvegarde Étudiant | external v1 / 2.1.9 | enregistrerEtudiant, modifierEtudiant | ✅ session 7 | ✅ `10_seps_enregistrer_etudiant_v1.md` |
| SEPS Enregistrer Inscription | external v1 / 2.1.9 | enregistrerInscription, modifierInscription | ✅ session 7 | ✅ `11_seps_enregistrer_inscription_v1.md` |
| SEPS Recherche Inscriptions | external v1 / 2.1.9 | rechercherInscriptions | ✅ session 7 | ✅ `12_seps_recherche_inscriptions_v1.md` |
| SEPS Notifications | external v1 / 1.0.8 | lireNotifications | ✅ session 7 | ✅ `13_seps_notifications_v1.md` |
