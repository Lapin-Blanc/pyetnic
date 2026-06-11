# Circulaire 8684 (16/08/2022) — Renseignements annuels : instructions d'encodage EPROM

> **LA circulaire métier des services EPROM** : instructions officielles d'encodage des Documents A, 1,
> 1D, 2 et 3 dans « EPROM Formations ». Source : `circulaires/49854_000.pdf` (90 p. : 25 p. de corps +
> 8 annexes dont manuels HOD/CICS et EPROM). **Toujours en vigueur** (jamais abrogée ; abroge la 6313,
> complète la 6382). Gestionnaire : Direction EPS — Service de la Vérification.
> Validité : année 2022-2023 (les exemples d'années civiles 2022/2023 se transposent).
> Date d'analyse : 2026-06-10 (session 8)

---

## 0. Confirmations structurantes

1. ⭐ **« DOCUMENT A » = « Déclaration d'organisation »** (titre de la section 2.1) — double
   confirmation de la découverte de la spec 18 : Doc A = le document Organisation (service Formation
   Organisation v7).
2. ⭐ **Les web services EPROM sont officiellement prévus** (§ Doc 1D, encadré) : « L'Administration a
   mis à la disposition des développeurs d'applications de gestion (ENORA, GIPS, PROSOC…) la
   possibilité d'organiser les transferts d'informations relatives aux **DOCUMENTS A, 2, 1D et 3** par
   l'utilisation de **webservices** […] en un seul encodage. » → c'est exactement le périmètre pyetnic
   (Organisation, Doc 1+2, Doc 1D, Doc 3).
3. **Workflow** : le Document 2 « est **généré par l'application** pour toute formation déclarée
   ouverte par un DOCUMENT A **et approuvée par l'Administration** » → le Doc 2 n'existe qu'en aval
   d'un Doc A approuvé (cohérent avec `20102` et la génération des lignes du Doc 3 depuis le Doc 2).
4. **Accès à l'application** : `www.am.cfwb.be`, comptes `ec00xxxx@adm.cfwb.be` / `po00xxxx@…`
   (xxxx = matricule FASE) ; PO = consultation d'office, « approbation » sur demande au Service de la
   Vérification → éclaire les statuts « Encodé école » / « Encodé PO » / « Approuvé » (`StatutCT`).

## 1. DOCUMENT A — déclaration d'organisation (→ spec 02)

- **Seule preuve d'ouverture** d'une formation ; initie tout le processus déclaratif.
- **Numéro de séquence attribué par le système** (nombre d'organisations non limité) = `numOrganisation`.
- Données : dates **réelles** de début/fin, nombre de semaines, intervention extérieure éventuelle,
  et finalités à cocher — correspondance directe avec `FormationOrganisationCT` :

| Finalité (circulaire) | Champ service |
|---|---|
| uniquement périodes supplémentaires et/ou EPT | `organisationPeriodesSupplOuEPT` |
| uniquement organisation de la valorisation | `valorisationAcquis` |
| partiellement à distance (→ hybride dès 2022-2023, spec 18) | `enseignementHybride` |
| milieu carcéral | `enPrison` |
| activités de formation (circ. 6351) | `activiteFormation` |
| intervention extérieure | `typeInterventionExterieure` (+ détail au Doc 2) |

  ⚠️ La case « uniquement périodes suppl./EPT » ne doit **pas** être cochée pour le suivi
  pédagogique (ligne 96 — voir §3.4).

- **UE sur 2 années scolaires** : **deux** Documents A — le 1ᵉʳ dans l'année du **1ᵉʳ dixième**, le 2ᵈ
  l'année suivante avec **le numéro d'organisation de l'année précédente**
  (= `numOrganisation2AnneesScolaires`). Les deux mentionnent les dates réelles de **l'ensemble** de
  la formation. Art. 14 du décret 16/04/1991 : début et fin séparés de **365 jours calendrier max**
  (= erreur `20012`).
- **Après validation** : la formation est « ouverte » ; toute modification/suppression passe par le
  **Service de la Vérification** (courriel) — éclaire la contrainte `30003` et le caractère sensible de
  `ModifierOrganisation`/`SupprimerOrganisation`.
- **Désactivation automatique** : un dossier pédagogique non activé dans les **4 ans** de
  l'autorisation est désactivé ; réactivation préalable obligatoire (annexe 1 ; circ. 5273/5447) —
  cause plausible de l'erreur `20029` (« date début ≥ date fermeture formation »).
- **Échéance** : transmission dans les **5 jours ouvrables suivant la fin de la semaine du 1ᵉʳ jour de
  cours**.

## 2. DOCUMENT 1 — populations au 1ᵉʳ dixième (→ spec 03)

Onglet « POPULATIONS », tableau « par année d'étude » (16 colonnes, 9 à renseigner). Le 1ᵉʳ et le 5ᵉ
dixième sont **calculés d'après les dates du Doc A**. Sémantique officielle des colonnes :

| Col. | Contenu | Remarques |
|---|---|---|
| 1 | année d'étude | préremplie |
| 2 | étudiants réguliers **≥ 18 ans** au 1ᵉʳ dixième (exonérés ou non du DI) | exclut ceux des col. 3 et 5 ; un étudiant déjà en col. 2 d'une autre formation ne va que dans la col. 8 |
| 3 | réguliers inscrits pour la 1ʳᵉ fois via un **CEFA** | |
| 4, 4' | ~~FSE HPI / FSE PI~~ | **plus demandées** (≈ `nbEleveFse`/`nbElevePi` obsolètes de la spec 03) |
| 5 | réguliers **< 18 ans** non soumis à l'obligation scolaire à temps plein | |
| 6 | **auto** = 2+3+5, étudiants « **comptés 1 fois** » (jamais déjà dans une col. 6 d'un autre Doc 2 de l'année) | |
| 7 | exemptés DI sur attestation **FOREM/ACTIRIS/VDAB/Arbeitsamt** | sous-ensemble de la col. 2 |
| 7' | exemptés DI **RIS/ERIS** (CPAS, ILA, Fedasil) | sous-ensemble de la col. 2 |
| 7'' | exemptés DI **autres motifs** | sous-ensemble de la col. 2 |
| 8 | réguliers multi-formations déjà comptés dans une col. 6 ailleurs (« **comptés plusieurs fois** ») | |
| 9 | **auto** = 6+8 = total des inscriptions | |
| 10, 10' | ~~FSE comptés plusieurs fois~~ | plus demandées |
| 11, 11' | total réguliers **masculin** / **féminin** | |

- **Validation** : case à cocher + sauvegarde → données **figées** (= `swAppPopD1` posé via
  `ApprouverDocument1`). Cette validation **ouvre la partie périodes (Document 2)**.
- « Le Document 1 doit être transmis **en même temps** que le Document 2 » (35 jours, cf. §6).
- Jonctions session 7 confirmées : col. 7/7'/7'' ↔ exemptions DI (`MotifExemptionType` SEPS) ;
  comptage 1 fois / plusieurs fois ↔ logique `regulier1`/`regulier5`.

## 3. DOCUMENT 2 — périodes organisées (→ spec 04)

### 3.1. Tableau « population par activité d'enseignement » (colonnes 12-19)

| Col. | Contenu | Champ service probable |
|---|---|---|
| 12 | branche préremplie + n° d'ordre administratif | `coNumBranche` + `teNomBranche` (+ `coCategorie`) |
| 13 | année d'études | `noAnneeEtude` |
| 14 | nb d'étudiants réguliers au 1ᵉʳ dixième suivant la branche (hors dispensés) | population par branche |
| 15 | **auto** : total des périodes organiques de la branche (**document 8bis**) | `nbPeriodesDoc8` (Doc 3) |
| 16/17 | périodes **organiques effectives** de la 1ʳᵉ/2ᵉ **année civile** | prévues an 1 / an 2 |
| 18/19 | périodes **réellement organisées** (dédoublements compris) 1ʳᵉ/2ᵉ année civile | réelles an 1 / an 2 |

**Règles de cohérence officielles** (sources probables des erreurs `4004`-`4012`, `1527`/`1528`,
`1574`) :

1. UE entièrement organisée dans l'année : **col 16 + 17 = col 15**. UE sur 2 années
   scolaires : 16+17 < 15 par Doc 2, mais la **somme des deux Documents 2 = Doc 8bis**.
2. **Col 18 = multiple entier de col 16** (idem 19/17), sauf suppression de dédoublement ou
   regroupement — **permis uniquement au 5ᵉ dixième**.
3. Ligne par ligne : **18+19 = multiple entier ou entier-et-demi de 15** (explique les périodes en
   `float` — « multiple entier et demi »).
4. **Encadrement** (stage, épreuve intégrée) : 18+19 = **col 14 × périodes prévues par étudiant**
   (Doc 8) — strictement.
5. UE à cheval sur les 2 semestres : périodes **obligatoires sur les deux années civiles**
   (« conforme à la réalité de terrain »).
6. **Somme des totaux 18+19 = total des périodes attribuées aux professeurs titulaires** au Doc 3
   (hors remplacements) — c'est l'erreur `1574` côté Doc 3.
7. Les périodes des col. 18/19 sont **décomptées de la dotation de périodes organique de l'année
   civile correspondante** → c'est la raison d'être de la ventilation par année civile (la dotation
   est gérée par année civile, 16+24 semaines — spec 17).

### 3.2. Lignes spéciales (référentiel `coNumBranche`/catégories)

| Ligne | Usage | Règles |
|---|---|---|
| 91/93 | **valorisation** : admission ou dispense (formelle/informelle/non formelle) | circ. 6677 → 9447 |
| 92/94 | **valorisation** : sanction | encodage possible **après approbation**, jusqu'au **31/10 de l'année scolaire suivante** |
| 95 | **expertise pédagogique et technique** (périodes supplémentaires) | min. **40 périodes par chargé de cours** sur dotation organique (pas de minimum en IE) |
| 96 | **suivi pédagogique** (art. 5bis 25°/27° et 91/6 du décret) | sur dotation organique **ou** pot K ; **aucun DI** ; **aucune population** aux 1ᵉʳ/5ᵉ dixièmes → « valider les Document 1 et Document 1D **sans population** » ; UE « à blanc » possible (conseiller à la formation, méthodes de travail, orientation/guidance, remédiation math/français) |

> Art. 91/6 : plafond global de **10 % de la dotation organique** pour conversions d'emplois, conseil
> des études, admission/suivi/sanction, expertise, activités de formation (sauf dérogation et
> conventions art. 114).

### 3.3. Regroupements

- Encodés dans un cadre dédié : n° administratif de la formation où la branche est réellement
  dispensée + n° d'organisation + n° d'activité + année d'étude (= champs `regroupement*` du Doc 2,
  erreurs `1527`/`1528`).
- Conditions de l'AGCF du 20/07/1993 (art. 5) : même **niveau**, même **catégorie de cours**, même
  **nombre de périodes**, mêmes **capacités terminales/acquis d'apprentissage**.
- Étudiants regroupés comptés **une seule fois**, dans la formation où la branche est enseignée ;
  dans l'autre formation, col. 16-19 = 0 pour la branche regroupée.
- ⚠️ Regroupements non conformes : périodes **déduites complètement de la dotation**.

### 3.4. Interventions extérieures (IE)

- **Définition** : toute utilisation de périodes d'origine **autre qu'organique**, ne devant pas
  intervenir dans le **calcul de l'ajustement de la dotation** : conventions, projets FSE, périodes
  « cabinet », périodes complémentaires, conversion d'emploi NCC (antigel)…
- Les périodes IE **n'entrent pas** dans l'ajustement de la dotation **mais comptent** pour les
  périodes-élèves (encadrement) → ventilation obligatoire cas **généraux** vs cas **particuliers**
  (art. 21 AECF 27/12/1991).
- **TYPE + SOUS-TYPE** (annexe 2) = exactement les tables `coCatCol` (type, 1 lettre) et `coObjFse`
  (sous-type, 2 lettres) de la spec 04 : A (PNCC), B (périodes suppl.-bonus : AE/AL/RE), C (Convention :
  AC/AF/BF/CA/CD/CE/CF/CO/FC/FO/FP/FS/NE/RW), D (discriminations positives), E (EHR), F (Fonds
  européens : BW/BX/CG/WL), G (antigel), I (publics infrascolarisés : AP/BF/CC/CI/CP/CQ/CS/FO/MI/NT),
  K (périodes cabinet : EL/EN/IN/PP/PR/RC/SP), P (formations continuées), Q (Agence Qualité),
  U (UE : RR), V (validation des compétences). Liste « non exhaustive, susceptible d'évoluer » ;
  chaque type a **sa propre circulaire administrative**.
- **Contrôle global** : total IE + colonnes 18/19 = **périodes effectivement utilisées** pour la
  formation (= plafonds du Doc 3, erreurs `1575`/`1576` CG/CP).
- Cas particuliers (annexe 3) : Coordinateur Qualité, Conseiller à la formation, Personne de référence
  EPS inclusif → UE dédiées (codes `980301U21D1`/`980302U21D1`/`980302U36D1`/`980303U21D1`…),
  branche 1 « ORIENTATION GUIDANCE », volumes en multiples de 20/25/30 périodes selon barème A/B/C,
  pots A (conversion PNCC), K (suivi pédagogique/inclusif IN), I (CQUA via ligne 95).
- Formule PE des cas particuliers : **périodes réservées × nombre moyen de PE par période organisée**
  (arrondi 2ᵉ décimale) — la formule repérée dès la session de recherche initiale.

## 4. DOCUMENT 1D (→ spec 06)

- « Vous devez renseigner le nombre d'étudiants réguliers au **5ᵉ dixième** de la formation ainsi que
  le **montant total des droits d'inscription perçus**. »
- ⚠️ Évolution terminologique : la **9731** (2026-2027, spec 16) précise désormais que le montant du
  Doc 1D = DI **constatés** (perçus ou non) — la 8684 (2022) disait « perçus ». La règle 9731, plus
  récente, fait foi.
- Échéance : **25 jours calendrier après le 5ᵉ dixième**.

## 5. DOCUMENT 3 (→ spec 05)

- Particularité : **reste toujours accessible en modification** (contrairement aux Doc A et 2) — pour
  concordance permanente avec les documents de traitement (**PROM S 12 / PS CF 12**, cf. circulaire
  9589 spec 07/08).
- Remplacements : **lignes supplémentaires** par activité (d'où `enseignant [0..*]` et
  `coNumAttribution`).
- Ligne subdivisée si : plusieurs professeurs se partagent les périodes ; partenaire extérieur prend
  en charge la rémunération (**codes dispo 14 ou 15**) ; remplacements.
- Statuts : définitif, temporaire, expert… (= table `teStatut`) ; motif d'absence du titulaire via
  menu déroulant (= table `coDispo`).
- **Seules les périodes réellement prestées** figurent au Doc 3 ; si un remplaçant ne couvre pas tout,
  le total Doc 3 < total Doc 2 (le contrôle `1574` est bien un **plafond**, pas une égalité).
- Échéance : **35 jours calendrier après l'approbation du Document 2**.

## 6. Échéancier récapitulatif (chapitre 4 de la circulaire)

| Document | Échéance |
|---|---|
| **Doc A** | 5 jours ouvrables après la fin de la semaine du 1ᵉʳ jour de cours |
| **Doc 1 + Doc 2** | 35 jours calendrier après le **1ᵉʳ dixième** (transmis ensemble) |
| **Doc 1D** | 25 jours calendrier après le **5ᵉ dixième** |
| **Doc 3** | 35 jours calendrier après l'**approbation du Doc 2** |
| Doc 6 (horaires, hors SOAP) | au 1ᵉʳ dixième |
| Doc 6bis (PNCC, papier), fiche signalétique | dernier jour ouvrable de septembre (et janvier) |
| Calendrier général | dernier jour ouvrable de septembre (cf. spec 17) |
| Registre DIS | 15 janvier / 15 juillet + 15 jours |

## 7. Impacts sur les specs existantes

| Spec | Impact |
|---|---|
| **02 (Organisation)** | mapping finalités ↔ switches ; 2 Doc A pour UE sur 2 ans (`numOrganisation2AnneesScolaires`) ; 365 jours max (`20012`) ; modification après validation = via Vérification (`30003`) ; échéance 5 jours ouvrables |
| **03 (Doc 1)** | sémantique officielle des colonnes 1-11' ; colonnes obsolètes 4/4'/10/10' = champs FSE/PI dépréciés ; validation = figeage ; transmis avec le Doc 2 |
| **04 (Doc 2)** | sens des périodes prévues/réelles **par année civile** (dotation par année civile !) ; règles de multiples (entier, entier-et-demi) ; encadrement = effectif × périodes/étudiant ; lignes 91-96 ; regroupements (AGCF 20/07/1993) ; IE = `coCatCol`/`coObjFse` avec sémantique complète |
| **05 (Doc 3)** | toujours modifiable ; concordance paie ; dispo 14/15 = prise en charge partenaire ; total ≤ Doc 2 (`1574` plafond) |
| **06 (Doc 1D)** | 5ᵉ dixième + montant DI (perçus 2022 → **constatés** 9731) ; à valider « sans population » pour les UE ligne 96 |
| **16 (DI)** | colonnes 7/7'/7'' = la ventilation des exemptions ; « cohérence forfait ↔ colonnes A et B » *(voir point ouvert)* |

## 8. Points ouverts

- ~~« Colonnes A et B » du Document 1~~ : ✅ **résolu en session 9** (exploration UI, spec 20) — dans
  l'application, les colonnes 2 et 5 du Doc 1 sont libellées « **Elèves A** » et « **Elèves B** »
  (réguliers ≥ 18 ans / < 18 ans non soumis à l'obligation scolaire). La « cohérence forfait ↔
  colonnes A et B » des circulaires DI vise ces deux comptages.
- La 8684 date de 2022 : vérifier l'existence d'un **successeur** (aucune abrogation sur Gallilex au
  10/06/2026 — elle reste la référence) et surveiller les ajouts de catégories/lignes annoncés « par
  circulaire, note ou courriel ».
- Échéances vs erreurs `20030` (« date début ne peut excéder 4 mois ») : le lien exact (délai
  d'encodage rétroactif ?) reste à confirmer. **Précision mesurée en production le 11/06/2026** :
  le délai s'applique à l'**anticipation** (date de début future), pas au rétroactif —
  `CreerOrganisation` avec début au 15/09/2026 (J+3 mois 4 j) accepté, début au 03/11/2026
  (J+4 mois 22 j) rejeté avec `20030`. La borne exacte (J+4 mois calendaires ?) reste à cerner
  entre ces deux points. Le rétroactif passe : début au 09/03/2026 (J−3 mois) accepté le
  11/06/2026 (queue 2 années scolaires de l'UE 510).
- HOD/CICS (écran 59, pot K) : système hôte historique de consultation de la dotation — hors
  périmètre SOAP mais utile pour comprendre les références « écran 59 » dans les libellés.
