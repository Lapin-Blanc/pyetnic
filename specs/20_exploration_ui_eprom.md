# Exploration de l'application EPROM Web (2.12.0) — confrontation UI ↔ specs

> Session 9 (2026-06-10) — exploration **en lecture seule** de l'application de production
> (`enseignement.cfwb.be/EPROM_WEB`, compte collectif école EICA Auvelais, année 2024-2025,
> formation témoin : 157 « ESS - Méthodes de travail », code `971111U21D2`, organisation n° 1).
> Objectif : valider les déductions des specs 01-19 contre la réalité de l'interface.

---

## 1. Confirmations majeures

### 1.1. ⭐ « Doc A » : définitivement confirmé

L'écran d'une organisation (« Description de l'organisation de la formation ») contient un tableau
**« DOCUMENTS ANNUELS »** :

| Type Document | Date Encodage | Statut | Date de màj du statut |
|---|---|---|---|
| **Doc A** | 21/11/2024 | Approuvé | 04/12/2024 |
| **Doc 1 et 2** | 11/03/2025 | **Approuvé / Approuvé** | 03/04/2025 |
| **Doc 1D** | 06/06/2025 | Approuvé | 13/06/2025 |
| **Doc 3** | 02/03/2026 | **Encodé école** | 02/03/2026 |

- **Doc A = l'organisation elle-même** (l'écran de description porte les champs du Doc A) —
  triple confirmation (circ. 8829, circ. 8684, UI).
- « Doc 1 et 2 » est **une seule entrée avec deux statuts** (« Approuvé / Approuvé ») → cohérent avec
  l'unique `statutDocumentPopulationPeriodes` de `OrganisationApercuCT` (spec 01), qui agrège Doc 1
  et Doc 2.
- Les valeurs de statut affichées (« Approuvé », « Encodé école ») = les valeurs de `StatutCT.statut`.
- **Chaque ligne du tableau est cliquable** et ouvre l'écran du document correspondant.

### 1.2. Tuple de statuts dans la liste des formations

La liste de recherche (« LISTE DES FORMATIONS ORGANISABLES », 110 résultats pour 2024-2025) affiche
par organisation : `N° du JJ/MM/AAAA au JJ/MM/AAAA` + **`(O - O - O - O - E)`** = les statuts des
**5 documents dans l'ordre (Doc A, Doc 1, Doc 2, Doc 1D, Doc 3)**, abrégés :
`O` = apprOuvé, `E` = Encodé (école). L'exemple `(O - O - O - O - E)` correspond exactement au
tableau ci-dessus. Colonnes de la liste : N° Administratif | Libellé Formation | Code Formation |
**IE** (lettre du type d'intervention, ex. `I`) | Organisation(s) | Statuts Documents.
Export **XLS** de la liste disponible (`lnk_generationRapport_imgBtnXls`).

### 1.3. Écran Doc A ↔ `FormationOrganisationCT` (spec 02)

Champs affichés : N° Organisation (1) ; Début 18/04/2024 ; Fin 10/10/2024 ; **Nbr semaines 25** ;
puis les switches avec leurs libellés UI exacts :

| Libellé UI | Champ service |
|---|---|
| Uniquement pour l'organisation de périodes suppl. et/ou d'EPT | `organisationPeriodesSupplOuEPT` |
| Uniquement pour l'organisation VA | `valorisationAcquis` |
| Enseignement hybride | `enseignementHybride` |
| en-prison | `enPrison` |
| Activité de formation | `activiteFormation` |
| **Uniquement pour l'organisation de la mission de conseiller en prévention ou de DPO** | `conseillerPrevention` |
| UE sur 2 années scolaires : **N° d'organisation année précédente** | `numOrganisation2AnneesScolaires` |
| Informations liées à une organisation en partenariat / Type d'intervention extérieure **à 50 % et plus** | `typeInterventionExterieure` / `interventionExterieure50p` |

> La formation témoin a `numOrganisation2AnneesScolaires = 1` : UE de 60 périodes à cheval
> 2023-2024 → 2024-2025, déclarée par deux Doc A (cf. règle 8684, spec 19 §1).

### 1.4. Écran « Doc 1 et 2 » (`Description du document annuel 2`) — spec 03/04

Trois onglets : **POPULATIONS | Intervention Extérieure | REGROUPEMENT DES ACTIVITÉS D'ENSEIGNEMENT**.

**⭐ « Colonnes A et B » — point ouvert résolu.** En-têtes réels du tableau
« POPULATION SCOLAIRE PAR ANNÉE D'ÉTUDES, AU 1/10ᵉ » :

| UI (n° de colonne 8684) | Sémantique (8684/9593) | Champ Doc 1 |
|---|---|---|
| Année Études (1) | préremplie | `coAnnEtude` |
| **Elèves A (2)** | réguliers ≥ 18 ans | — |
| EHR (3) | inscrits via CEFA *(libellé UI « EHR »)* | — |
| Elèves FSE HPI (4) / FSE PI (4') | plus demandées | `nbEleveFse`/`nbElevePi` (obsolètes) |
| **Elèves B (5)** | réguliers < 18 ans non soumis à l'obligation scolaire t.p. | — |
| Total de 2 à 5 (6) | comptés 1 fois (auto) | — |
| Demandeur Emploi (7) | exemptés DI FOREM/ACTIRIS/VDAB/Arbeitsamt | `nbEleveDem` |
| **Minimexés (7')** | exemptés RIS/ERIS | — |
| Autres exemptés (7'') | autres motifs | `nbEleveExm` |
| Elèves comptés plusieurs fois (8) | déjà dans un col. 6 ailleurs | — |
| Total de 6 + 8 (9) | total inscriptions (auto) | — |
| FSE HPI (10) / FSE PI (10') | plus demandées | obsolètes |
| Nbre Total Homme (11) / Femme (11') | ventilation par sexe | — |
| *(dernière colonne)* | **« Validé »** | statut de validation de la ligne |

→ Les « **colonnes A et B** » des circulaires DI = **« Elèves A » (col 2) et « Elèves B » (col 5)** :
le forfait DI doit être cohérent avec ces comptages de réguliers. (À reporter dans le mapping des
champs `nbEleve*` de la spec 03 — les noms `A`/`B` sont les libellés métier officiels.)

**Tableau « population par activité d'enseignement »** (colonnes 12-19), en-têtes UI :
`N° | Catégorie | Activité d'enseignement (12) | Année Études (13) | Nb Elèves (14) | Pér. prévues (15) |
Prévue (16) 2024 | Prévue (17) 2025 | Réel (18) 2024 | Réel (19) 2025` — la ventilation par **année
civile** est explicite dans les en-têtes (cf. dotation par année civile, specs 17/19).
Exemple réel : branche 1 `CTms` Méthodes de travail, 19 élèves, **48,00** (Doc 8bis), prévue 2024
**20,00**, réel 2024 **20,00** ; branche 2 `Auto` Autonomie **12,00** ; total UE 60 périodes sur
2 années scolaires (16+17 < 15 conforme à la 8684).

**Lignes spéciales affichées (91-99)** — complète la liste 91-96 de la 8684 :

| Ligne | Catégorie | Libellé UI |
|---|---|---|
| 91 | SEtu | VAF impliquant une admission ou une dispense |
| 92 | SEtu | VAF impliquant la sanction |
| 93 | SEtu | VANFI impliquant une admission ou une dispense |
| 94 | SEtu | VANFI impliquant la sanction |
| 95 | ExPT | EXPERTISE PEDAGOGIQUE ET TECHNIQUE |
| 96 | SEtu | ADMISSION, SUIVI PEDAGOGIQUE ET SANCTION DES ETUDES |
| **97** | PeSu | PERIODES S… *(périodes supplémentaires)* |
| **98** | PSup | PART SUPPLEMENTAIRE |
| **99** | CEtu | CONSEIL DES ETUDES |

> VAF = valorisation formelle ; VANFI = valorisation non formelle/informelle. Les codes de la
> colonne « Catégorie » (`CTms`, `Auto`, `SEtu`, `ExPT`, `PeSu`, `PSup`, `CEtu`…) = la table
> **`coCategorie`** (30 codes, specs 04/05).

**Onglet Intervention Extérieure** (vide pour la formation témoin) : champs
`Intervention n°` (=`coNumIex`), `Type` (=`coCatCol`), `Sous-Type` (=`coObjFse`),
`Projet global / Référence` (=`coRefPro`), `N° agrément` (=`coCriCee`) ; tableau « Périodes en
intervention extérieure » : colonnes **2024 | 2025** (années civiles), lignes **Cas généraux /
Cas particuliers / Suppléments** (= les `teLibPeriode` des `Doc2PeriodeExt*` de la spec 04).

### 1.5. Écran Doc 1D (`Description du document annuel 1D`) — spec 06

Titre du bloc : « **Droits d'inscription et population au 5/10ᵉ de fonctionnement, comptant pour
les subventions** ». Colonnes : Année Études | Nombre d'élèves | Droits d'inscription |
**Droits d'inscription occupationnel** (toujours affiché bien que « plus utilisé ») | **Validé**.

### 1.6. Écran Doc 3 (`Document 3 - Liste des attributions`) — spec 05

Trois compteurs en tête (le mécanisme des plafonds `1574`/`1575`/`1576` rendu visible) :
**Périodes réelles organiques** (20,00) ; **Périodes prises en interventions extérieures** (0,00) ;
**Périodes déjà attribuées** (20,00).

Liste des activités : `N°Activité | Catégorie | Activité d'enseignement | Année Études |
Périodes Doc 8 | Pér. prévues doc2 | Pér. réelles doc2` — mapping 1:1 avec `Doc3ActiviteDetailCT`
(valeurs affichées en décimal « 48,00 » → confirme la nature `float` malgré le XSD `int`, cf.
divergence spec 05). Détail d'une activité : `N°Attribution | Enseignant | Code dispo | Statut |
Périodes attribuées | Suppr.` = `Doc3EnseignantDetailCT`.

## 2. ⭐ Référentiels extraits de l'UI (listes déroulantes du Doc 3)

### 2.1. `teStatut` (8 options dont vide) — libellés officiels

| Code (spec 05) | Libellé UI |
|---|---|
| C | ACS |
| P | ACS Discriminations **P**ositives |
| A | Définitif **A**ccessoire |
| D | **D**éfinitif |
| E | **E**xpert |
| X | E**X**pertise pédagogique et technique |
| T | **T**emporaire |

*(Correspondance lettre↔libellé déduite des initiales — ordre UI : ACS, ACS DP, Déf. Accessoire,
Définitif, Expert, eXpertise, Temporaire ; à figer après un Lire SOAP de contrôle.)*

### 2.2. `coDispo` (60 codes + vide) — libellés officiels

`BE` Bénévolat · `02` Dispo retrait emploi intérêt service · `03` Dispo mesure disciplinaire ·
`04`/`11` Dispo mission spéciale gvt/orga inter. · `05` Dispo maladie (même traitement) ·
`07` Dispo convenances personnelles · `09` Absence longue durée raisons familiales ·
`12` Congé mission cabinet du Roi · `13` Congé mission groupe politique ·
**`14` Accompagnement FSE ou EHR** · **`15` Périodes prises en charge Convention** ·
`20` Congé interr. carrière (rempl. chômeur) · `23` Accident de travail ·
`24` Maladie professionnelle · `25` Dispo maladie (autre traitement) ·
`27` Congé maladie/infirmité rémunéré · `28` Congé maternité rémunéré CF ·
`29` Congé allaitement ou parental · `30` Congé interr. carrière (pas rempl.) ·
`31` Congé de prophylaxie · `33` Désignation juré / désignation provisoire (2 entrées) ·
`35` Congé mission SHAPE · `36` Dispo mission école européenne · `37` Congé mission orga. jeunesse ·
`38` Congé mission cabinets/jurys CF · `39` Congé mission associations parents ·
`44` Congé mission… · `46` Congé pour suivre des cours · `47` Prest. réduites 50+ & 2 enf. <14 ·
`48` Détachement fct sél/promo (titulaire malade) · `50` Congé mission enseign./guidance PMS ·
`52`/`53` Désign. prov. même/autre niveau (titul. malade) · `54` Suspension disciplinaire ·
`55` Suspension préventive · `58` Congé politique · `60` Congé accueil adoption/tutelle ·
`61` Congé mission cabinet non CF · `62` Congé mission programme spécifique ·
`63` Congé mission éduc. permanente · `64` Prest. réduites maladie/infirmité ·
`65`/`67` Congé mission non repris nb global · `69` Congé syndical permanent ·
`70` Prest. réduites raisons soc./famil. · `71` Prest. réduites raisons personnelles ·
`74` Prest. réduites membres du personnel · `76` Congé maladie payé mutuelle ·
`78` Congé maternité payé mutuelle · `79` Congé raisons familiales · **`80` Détachement EHR/CEFA** ·
`81` Détachement fct sél/promo (titul. non malade) · `94`/`95` Désign. prov. même/autre niveau
(titul. non malade) · `97` Absence non réglementairement justifiée ·
`98`/`99` Dispo mission spéciale (pas nb global).

> Les codes **14/15** (« partenaire extérieur prend en charge la rémunération » — 8684, spec 19 §5)
> sont bien dans la liste. Recouvrement confirmé avec les « codes DI » de la circulaire 9589 (spec 08).

## 3. Notes techniques d'automatisation (pour de futures explorations)

- **Stack** : IBM WebSphere JSF (« hxclient » v3.1.12), JSP : `rlRlFormationsOrganisations.jsp`
  (recherche+liste+description, multi-écrans sur la même URL), `dlDlOrganisation.jsp`,
  `dDDocument1D.jsp`, `dDDocument3.jsp`. Version affichée : **2.12.0**.
- La page garde une requête GET « pending » perpétuelle → les outils attendant `document_idle`
  (screenshot, get_page_text, read_page, find) **échouent** ; seul `javascript_tool` fonctionne.
- Boutons (`input type=button` toolbar, sprites) : `element.click()` et la soumission de formulaire
  forcée **ne marchent pas** (handlers du framework). Ce qui marche : **séquence de `MouseEvent`
  réels** `mousedown`/`mouseup`/`click` (bubbles) sur l'élément (bouton-toolbar, ligne de tableau,
  label d'onglet).
- Liens (`<a>`) : `a.click()` fonctionne. **`history.back()` interdit** (casse l'état JSF —
  re-naviguer depuis l'URL d'entrée). Boutons toolbar utiles : `[title="Lancer la recherche"]`,
  `[title="Retour à l'écran de liste"]`, `[title="Retour à l'écran de recherche"]`.
- Recherche : sélectionner `form0:i_anneeScolaire` **et** `form0:i_nsFaseIdImpl` (implantation)
  avant de lancer.
- Les pages contiennent des données personnelles (matricules/noms enseignants, liste
  `lstEnseignant`) → n'extraire que des **structures** (en-têtes, options de référentiels).
- Étabissement affiché « 3052 - 9017001 » = matricule EPS - matricule FASE ; implantation
  « 6050 - 0 - adresse ».

## 4. Points restants

- Confirmer le mapping lettre↔libellé de `teStatut` par un appel SOAP `LireDocument3` (les lettres
  ne sont pas visibles dans l'UI, seulement les libellés).
- Ligne 97 « PERIODES S… » : libellé tronqué à l'écran (vraisemblablement « périodes
  supplémentaires », catégorie `PeSu`) — à confirmer.
- Tester une organisation **avec** intervention extérieure (colonne IE = `I` dans la liste) pour
  voir l'onglet IE rempli.
- Le test TQ du déclencheur `20102` reste à faire côté SOAP (l'UI ne permet pas de le simuler sans
  modifier des données).
