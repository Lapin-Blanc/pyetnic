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

### Session 4 — (à planifier) : Document 3 (Attributions) v1.0

**À faire** :
- Document 3 v1.0 (Attributions) → fichiers dans `contrat_document3_v1/` et `manuel_document3_v1.pdf`
- Identifier le workflow inter-documents (doc3 dépend de doc1+doc2 approuvés)

---

### Session 5 — (à planifier) : Formation Droits Inscription v1.0

**À faire** :
- Formation Droits Inscription v1.0 → fichiers dans `contrat_formation_droits_inscription_v1/` et `manuel_formation_droits_inscription_v1.pdf`

---

### Session 6 — (à planifier) : Synthèse + Architecture + Mock server

**À faire** :
- Synthèse cross-services
- Architecture cible pyetnic v2
- Prototype mock server SOAP stateful
- Plan d'implémentation

## Services EPROM identifiés (extranet ETNIC)

| Service | Version | Analysé | Spec produite |
|---|---|---|---|
| Formations Liste | 2.0 | ✅ session 1 | ✅ `01_formations_liste_v2.md` |
| Formation Organisation | 7.0 | ✅ session 2 | ✅ `02_formation_organisation_v7.md` |
| Formation Population (Document 1) | 1.0 | ✅ session 3 | ✅ `03_formation_population_v1.md` |
| Formation Périodes (Document 2) | 1.0 | ✅ session 3 | ✅ `04_formation_periodes_v1.md` |
| Document 3 (Attributions) | 1.0 | ❌ session 4 | ❌ |
| Formation Droits Inscription | 1.0 | ❌ session 5 | ❌ |
