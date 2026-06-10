# Circulaire 9589 — EA12 / attributions / codes — Modèle de données fonctionnel

> Analyse du modèle « demande de mise en liquidation » (Doc12) et des référentiels de codes,
> orientée implémentation. Fichier 2/2 — voir `07_circulaire_9589_contexte_personnel.md`
> pour le contexte (acteurs, identifiants, calendrier, GEDI).
> Source : circulaire 9589 du 19/09/2025, Fiche III (p.109-290).

---

## 1. Les trois variantes du Doc12 en EA

| Document | Annexe | Périmètre | Mode d'emploi |
|---|---|---|---|
| **EA12** | A1 | EA **niveau secondaire** | p.118-158 |
| **EA12 bis** | A1bis | EA **niveau supérieur** | p.158-175 |
| **EA12 ter** | A1ter | **Experts** (secondaire et/ou supérieur) | p.175-188 |

Principes transversaux :

- Un Doc12 est une **« photographie » des attributions du MDP à la date de l'événement,
  dans un établissement donné** (1 document par établissement, et par niveau :
  secondaire et supérieur → 2 EA12 distincts).
- **Numérotation** par établissement et par MDP, redémarrant à `01` à chaque rentrée ;
  un rectificatif porte toujours un **nouveau numéro** ; on référence la **date du Doc12
  précédent** (même année scolaire ou non).
- Transmission **exclusivement via GEDI**, en PDF, avant la date-limite mensuelle
  (échéancier au fichier 07, §6). Concordance stricte exigée avec la déclaration **DIMONA**.
- Statut mixte (temporaire + définitif) : un seul document, cases multiples cochées.
  Mais ACS/APE/PTP + T/D : **deux documents** (services gestionnaires différents).

### Quand envoyer un EA12 (p.120-122)

| Statut | Événements déclencheurs |
|---|---|
| Définitif | À chaque rentrée scolaire (même sans changement) ; à chaque modification (augmentation/réduction d'attributions, absence avec impact paie, reprise après longue absence, congé, fin de fonction…) |
| Temporaire / qui devient définitif | À chaque entrée en fonction ; à chaque rentrée ; à chaque modification (augmentation/réduction/**prolongation** d'attributions, remplacement avec dates précises…) ; à la fin de fonction (sauf si elle coïncide avec la fin d'année scolaire) |

**Ne PAS déclarer via Doc12** (p.122, 130) :

- congé de maladie (DI 27) — sauf allocation pour fonction mieux rémunérée, maladie à charge
  de la mutuelle, ou reprise après absence mutuelle/disponibilité maladie ;
- ANRJ (DI 97) — relevé mensuel A14 ;
- grèves (DI EE) — relevé A15 ;
- l'accident du travail, lui, **se déclare** via Doc12.

Particularité temporaires EA (attribution d'heures/année) : lors d'un événement, définir les
heures/année **déjà prestées**, celles **qui auraient dû l'être** pendant l'absence et celles
**restant à prester**.

---

## 2. Structure logique du EA12 (A1, secondaire) — page 1

| Rubrique | Contenu / règles (p.123-131) |
|---|---|
| En-tête | Année académique ; n° de document (2 cases) ; date du dernier Doc12 transmis (JJ/MM/AAAA) |
| Identification établissement | Réseau (WBE / OS / LS) ; **n° ECOT** (10 cases, structure au fichier 07 §4) ; **n° FASE** ; nom PO + établissement ; coordonnées (e-mail officiel `@adm.cfwb.be`) ; personne de contact |
| Identification MDP | **Matricule** (11 cases, format fichier 07 §4) ; NOM (majuscules, nom de jeune fille) ; 1ᵉʳ prénom officiel ; titres de capacité (liste des diplômes — copies à transmettre) |
| Expérience utile | 3 cases : `Néant` / `EU métier` (art. 17 AR-15/04/1958, dépêches via VALEXU) / `EU enseignement` — impacte l'ancienneté pécuniaire |
| Statut | Cases multiples : `T`, `TPr`, `St`, `D`, `ACS/APE/PTP` |
| Cumul | `Pas de cumul interne` **ou** cases de cumul ; si prestations dans un autre établissement → joindre **A2** (§10) |
| Transmission tardive | Case « par la faute du MDP » (responsabilité PO de le signaler) |
| Jours de fonctionnement | Nombre de jours d'ouverture de l'établissement **par semaine** |
| Événement | **Date de début** de l'événement (JJ/MM/AAAA) |
| Semaines de fonctionnement | Uniquement si l'établissement est ouvert **moins de 40 semaines** : nombre de semaines + niveau |
| Type d'événement | 1 case parmi le référentiel ci-dessous (§3) + champ libre `Autres` |
| Justifications | Toujours compléter ; champ `Autres` (ex. n° d'article pour extension de nomination au LS, art. 41bis) |
| Absences | 1 case parmi 3 types ; intitulé précis + **code DI** + dates début/fin |
| Situation ancienne-nouvelle / Observations | Zone libre (ex. réaffectation + congé : préciser heures et codes DI) |

## 3. Référentiel « type d'événement » (p.129-130)

| Événement | Condition | Date à indiquer |
|---|---|---|
| Entrée en fonction | Pas de prestation la veille (nouveau dossier ou reprise après interruption) | 1ᵉʳ jour ouvrable scolaire de la relation de travail (prestation effective ou non) |
| Rentrée en fonction | Temporaire confirmé à la rentrée dans ses fonctions de l'année précédente ; reconduction de réaffectation | Date de rentrée ou de reconduction |
| Maintien d'attributions | Même total de périodes et même traitement (réorganisation interne éventuelle) | 1ᵉʳ jour ouvrable scolaire concerné |
| Augmentation d'attributions | Plus de périodes | 1ᵉʳ jour ouvrable scolaire des prestations augmentées |
| Prolongation d'attributions | Désignation/engagement prolongé | 1ᵉʳ jour suivant la fin de l'intérim précédent |
| Réduction d'attributions | Moins de périodes | 1ᵉʳ jour des attributions réduites (même samedi/férié) |
| Fin de fonction | Définitif : démission, licenciement, retraite, décès / Temporaire : fin de contrat, démission, décès | Définitif : veille du 1ᵉʳ jour sans attributions (ou décès) / Temporaire : dernier jour ouvrable presté (ou décès) |
| Nomination / engagement à titre définitif | Joindre PV d'ETD ou acte de nomination | Date de la nomination/ETD |
| Extension nomination/ETD | Au LS : préciser l'article dans `Justifications – Autres` | Date de l'extension |
| Passerelle | Directeur EA → fonction définitive vacante de chef de travaux d'atelier / recrutement / sélection (art. 29bis D.-06/06/1994, 41ter D.-01/02/1993) | Date choisie par le PO |
| Changement d'affectation | Définitif affecté à un autre établissement du **même PO**, même fonction | Date du changement |
| Mutation | Subventionné uniquement : passage chez un **autre PO**, même fonction à titre définitif | Date de la mutation |
| Autres | À préciser | Date de l'événement |

---

## 4. Ligne d'attribution (page 2 du EA12) — le cœur du modèle

Deux niveaux de lignes (p.131-137) : la **ligne de la fonction** (régime de titres, codes
fonction, total des périodes, titre, PVC) et les **lignes de détail** par UE/cours.

### 4.1 Ligne de la fonction

| Champ | Règles |
|---|---|
| Ancien/nouveau régime | Case déterminant le régime de titres applicable au MDP pour cette fonction (§6) |
| **Code RTF** | Code de la fonction (liste sur PRIMOWEB) |
| **Code RL10** | Code fonction du moteur de paie (tables de la circulaire, §9) |
| **Code FADI** | Code du référentiel fonctions/absences/disponibilités (liste sur enseignement.be) |
| Fonction + sous-niveau | Libellé PRIMOWEB ; `SI` = secondaire inférieur, `SS` = secondaire supérieur |
| Nombre total de périodes | Total attribué au MDP dans la fonction |
| Titre (abrégé) | Voir table §6 |
| PVC | Case si procès-verbal de carence joint (spécificité du subventionné) |

### 4.2 Colonnes du détail des attributions

| # | Colonne | Règles |
|---|---|---|
| 1 | **U.E.** | Code de l'unité d'enseignement : **9 chiffres et 2 lettres** — c'est le `codeFormation` EPROM (ex. `761001U31C1`, spec 01/registre). |
| 2 | **F** (source de financement) | `D` = dotation de périodes (y compris part dotation d'actions FSE/conventions) ; `F` = FSE hors dotation (au prorata de l'intervention, circulaire 1462 du 09/05/2006) ; `C` = convention (remboursée par le partenaire, hors dotation) ; `E` = EHR pour le compte d'un CEFA ; `Ag Q` = agent qualité ; `RRFC` = RRF appel à collaboration ; `RRFT` = RRF techno-pédagogue |
| 3 | **CLA** (classification du cours) | `CG` cours généraux ; `CT` cours techniques ; `PP` pratique professionnelle et stages ; `PPM` psychologie-pédagogie-méthodologie ; `CS` cours spéciaux. **Respecter scrupuleusement le document 2** (ou 8bis en 1ʳᵉ ouverture) |
| 4 | Dénomination du cours | Fonction + libellé du **cours** (pas l'intitulé de l'UE), tel qu'au **document 8 ou 8bis**, avec spécialité (bois, électricité…) — indispensable pour fixer l'échelle de traitement. NCC : indiquer la fonction. EPT : préfixer `EPT` (§7.1) |
| 5 | Périodes d'occupation | **Temporaires uniquement** (définitifs : ne pas compléter). Format `JJMMAA-JJMMAA` (ex. `021017-300118`). Supprimer les interruptions fictives, regrouper le volume prévisible (circulaire PS 314/95 du 06/06/1995). **Dates = celles du contrat = celles de DIMONA** (y compris débuts 01-06/09 et fins 24-30/06) |
| 6 | Nb de périodes | Heures **prestées et non prestées** (CAD, perte partielle…) |
| 7 | Sit. adm. | Lettre de situation administrative (§5) |
| 8 | **DI** | Code disponibilité/remplacement/congé (§5.2) — un code DI entraîne obligatoirement une justification et, le cas échéant, un formulaire CAD ou DPPR. Réaffectation + congé : le DI du congé **prime** |
| 9 | N° OE | Renvoi au n° d'« origine de l'événement » (tableau en fin de document : matricule, nom, statut D/T, motif avec code DI et période d'absence du MDP **remplacé**) |
| 10 | Bascule | Case si le MDP a basculé dans cette fonction via le tableau de correspondance de l'AGCF-05/06/2014 |

### 4.3 Attributions actuelles (récapitulatif global, p.137)

Par fonction (et donc par niveau) : périodes actuelles **y compris** disponibilités par défaut
d'emploi et pertes partielles de charge subventionnées. **À exclure** : rappels en service par
réaffectation/remise au travail, CPR convenances personnelles/sociales/50 ans/2 enfants < 14 ans,
interruptions de carrière, congés pour motifs impérieux familiaux, fonctions exercées à titre
provisoire (AR-13/06/1976, D.-12/07/1990), disponibilités pour convenances personnelles,
disponibilités pour mission spéciale sans traitement d'attente, périodes en demande de
suspension du droit à la subvention-traitement d'attente.
Sous-niveau : `SI`/`SS`. Puis bloc « Attributions du EA12 précédent » (mêmes colonnes,
+ date du PS12 précédent).

### 4.4 Fin de document

Mention type : sauf précision contraire, pas de Doc12 nécessaire pour la fin de fonction si la
désignation court jusqu'à la fin de l'année scolaire ; durées spécifiques à préciser
(personnel administratif, sélection/promotion — aussi ACS/APE). Signatures **facultatives**
depuis GEDI (le MDP consulte ses Doc12 sur Mon Espace).

### 4.5 Prestations pendant les vacances d'été (p.134-135)

- EA12 **distinct** obligatoire ; la période juillet-août est une **période d'occupation sui
  generis** (ex. `040717-120818`).
- Nombre de périodes + période d'occupation ; à transmettre **au plus tard le 30 septembre**
  de l'année scolaire suivante.
- Une notification d'attributions ne concerne **jamais qu'une seule année scolaire** :
  formation à cheval sur l'été → EA12 séparés.

---

## 5. Situations administratives et codes DI

### 5.1 Situation administrative (colonne « Sit. adm. », p.135-136)

| Groupe | Code | Signification |
|---|---|---|
| Définitif | `D` | MDP définitif |
| Définitif | `Z` | MDP en disponibilité/congé dont l'emploi est devenu définitivement vacant |
| Temporaire | `V` | Temporaire dans un emploi vacant |
| Temporaire | `S` | Temporaire dans un emploi non vacant ≥ 15 semaines (« stable ») |
| Temporaire | `I` | Temporaire dans un emploi non vacant < 15 semaines (« intérimaire ») |
| Temporaire | `St` | Directeur stagiaire (ou professeur de religion stagiaire à l'organisé) |
| Dispo/Réaffectation | `P` | Disponibilité par défaut d'emploi ou perte partielle de charge |
| Dispo/Réaffectation | `R` | Réaffectation dans un emploi vacant |
| Dispo/Réaffectation | `A` | Réaffectation dans un emploi non vacant |
| Dispo/Réaffectation | `T` | Remise au travail / rappel provisoire dans un emploi vacant |
| Dispo/Réaffectation | `M` | Remise au travail / rappel provisoire dans un emploi non vacant |

Compléments : `STPrior`/`VTPrior` = temporaire prioritaire (emploi non vacant / définitivement
vacant). WBE n'utilise pas « remise au travail » : RAS (rappel provisoire en activité de service),
RPDI (rappel pour période indéterminée), réaffectation ; perte partielle compensée par
complément de charge/d'horaire/d'attributions ou tâches pédagogiques (p.157-158).
Fonctions de promotion : statut admissible `S`, `I`, `St`, `D` (directeur) ; `S`, `I`, `V`, `D` (autres).

> ⚠️ **Ne pas confondre** avec `teStatut` du Document 3 EPROM (spec 05 : `C` ACS,
> `P` ACS discriminations positives, `A` définitif accessoire, `D` définitif, `E` expert,
> `X` EPT, `T` temporaire). Les deux tables se recoupent partiellement (`D`, `T`) mais
> servent des systèmes différents (paie RL10 vs document pédagogique EPROM).

### 5.2 Codes DI (p.188-212)

Référentiel des codes de congés/absences/disponibilités, classés par thème, avec signe
`+` (rémunéré) / `-` (non rémunéré). Correspond fonctionnellement à la table `coDispo`
du Document 3 EPROM (spec 05, ~80 codes au 01-05-2023).

Classement thématique de la circulaire (6.1, p.188-205) :

A. Disponibilités par défaut total d'emploi ou perte partielle de charge —
sans réaffectation : `01+` (2 premières années), `DP+` (dès la 3ᵉ), `17+` (perte partielle),
`72-` (avec suspension du traitement d'attente) ; avec réaffectation même établissement :
`84+`/`85+` (même fonction, emploi vacant/non vacant) ; avec réaffectation autre
établissement ; compléments de charge/attributions/horaire (WBE).
B. DPPR. C. Autres disponibilités. D. Fonction de promotion et de sélection.
E. Fonction de recrutement également/mieux/moins bien rémunérée (lignes fictives DI `4A`/`ST`).
F. Congé pour mission. G. Maternité et parentalité. H. Prestations réduites (CPR).
I. Interruption de carrière. J. Congés autres et absences diverses.
K. Cas spécifiques temporaires et/ou ACS/APE/PTP. 6.2 : congé pour exercice d'une autre
fonction vers les Hautes Écoles.

Codes cités dans les instructions EA12 : `27` (maladie — ne pas déclarer sauf cas précis),
`97` (ANRJ — ne pas déclarer), `EE` (grève — ne pas déclarer), `14` (accompagnement FSE/EHR),
`15` (périodes prises en charge convention) — `14`/`15` sont les **seuls** codes DI admis sur
l'EA12 ter expert, liés à la source de financement.

> La plupart des codes DI influencent la déclaration fiscale (ex. 281.10 case 250 :
> codes 04, 14, 15, 17, 21, 35, 36, 66, 68 ; 01, 06, 84, 85 si traitement 100 %).

---

## 6. Régimes de titres (colonne « Titre », p.131-132 et 139-151)

### Nouveau régime (RTF, depuis le 01/09/2016)

| Code | Signification |
|---|---|
| `TR` | Titre requis |
| `TS` | Titre suffisant |
| `TPL` | Titre de pénurie listé |
| `TPNL` | Titre de pénurie non listé (« autres titres ») |
| `ATS` | Assimilation au titre suffisant (joindre l'attestation, circulaire 7728) |
| `ATP` | Assimilation au titre de pénurie listé (plus délivrée depuis le 01/09/2020, droits maintenus) |

### Ancien régime (avant RTF)

| Code | Signification |
|---|---|
| `R` | Titre requis (avant RTF) |
| `A` | Titre jugé suffisant du groupe A (AR-30/07/1975 ou 14/04/1964) |
| `B` | Ni TR ni groupe A (secondaire) |
| `N` | Titre « néant » (art. 6 §4 AR-30/07/1975) |
| `3B` | Groupe B + 3 décisions ministérielles consécutives favorables (assimilé suffisant) |
| `AC` | Situation acquise (dispositions transitoires) |
| `Art. 20` | Article 20 (WBE) |

### Règles fonctionnelles clés

- Le choix **ancien/nouveau régime** se fait par fonction : « ancien régime » si le MDP était,
  avant le 01/09/2016, nommé/ETD, temporaire prioritaire ou protégé (art. 285 D.-11/04/2014) —
  et si l'ancien barème est plus avantageux (p.149).
- **Priorisation au primo-recrutement** (p.145-146) : TR/TS avant TP, TP avant TPNL ;
  l'égalité TR=TS est prolongée jusqu'au 1ᵉʳ jour de l'année scolaire **2026-2027**
  (art. 7 D.-20/07/2023). PVC requis dans certains cas ; pas de nouveau PVC si prolongation
  d'intérim (même candidat, même emploi, volume ≤, dans le mois — art. 29ter).
- **Droits statutaires TPNL** (p.147-148) : titre pédagogique + 600 jours (OS/WBE) ou
  720 jours (LS) d'ancienneté sur ≥ 4 années consécutives, même fonction, même PO
  (art. 36 §3 D.-11/04/2014). Barème TPNL = TP depuis le 01/09/2020.
- Mesures transitoires et **portabilité** inter-PO/inter-réseaux : art. 262 et 286 D.-11/04/2014
  (détail des catégories bénéficiaires p.143-144).

---

## 7. Dénominateurs de charge et fonctions particulières (p.151-158)

### 7.0 Dénominateurs (base du calcul de fraction de charge)

**Fonctions de promotion, sélection, auxiliaire d'éducation — 1 période = 60 minutes :**

| Fonction | Dénominateur | Code RL10 |
|---|---|---|
| Directeur | 36 périodes/semaine | 110 |
| Chef d'atelier | 30 périodes/semaine | 220 |
| Directeur adjoint | 36 périodes/semaine | 111 |
| Éducateur-économe | 36 périodes/semaine | 530 |
| Secrétaire de direction | 36 périodes/semaine | 540 |
| Éducateur secrétaire | 36 périodes/semaine | 552 |

**Personnel administratif :**

| Fonction | Dénominateur | Code RL10 |
|---|---|---|
| Commis | 38 heures/semaine | 810 |
| Rédacteur | 38 heures/semaine | 830 |
| Comptable | 38 heures/semaine | 80A |

**Personnel enseignant — 1 période = 50 minutes, dénominateur annuel :**

| Fonction | Dénominateur | Code RL10 |
|---|---|---|
| Professeur de cours généraux (CG) | 800 périodes/année | 282 |
| Professeur de PPM | 800 périodes/année | 280 |
| Professeur de cours spéciaux (CS) | 800 périodes/année | 275 |
| Professeur de cours techniques (CT) | 800 périodes/année | 260 |
| Professeur de pratique professionnelle (PP) | 1000 périodes/année | 265 |
| Professeur de CT et PP | 1000 périodes/année | 270 |

**Fonctions transversales :**

| Fonction | Dénominateur | Code RL10 |
|---|---|---|
| Coordinateur qualité | 36 périodes/semaine, scindable en quarts temps 9/36 | conversion 250 périodes B par quart temps — code 384 |
| Conseiller à la formation | 36 périodes/semaine, scindable en quarts temps 9/36 | conversion 250 périodes B par quart temps — code 2D4 |
| Expertise pédagogique et technique (EPT) | 800 périodes/année, minimum 40 périodes | — |
| Techno-pédagogue | 800 périodes/année | 2G2 |

### 7.1 EPT (expertise pédagogique et technique, D.-20/06/2013)

- Activités **rattachées à une fonction de recrutement** existante (personnel directeur et
  enseignant) → mêmes dispositions statutaires et barémiques.
- Sur l'EA12 : préfixer le libellé par `EPT` et **séparer les lignes** (ex. 200 périodes fonction X
  + 100 périodes EPT liées à X = 2 lignes distinctes).

### 7.2 Coordinateur qualité / Conseiller à la formation (D.-20/06/2013, circulaire 4930)

- Fonctions de la catégorie personnel directeur et enseignant, barème unique transversal,
  régime de TR et TS propre. Organisables par quart-temps de 36 h/semaine (9/36).

### 7.3 RRF (plan de relance européen, D.-programme 14/07/2021 art. 80-87)

- **Appel à collaboration** (`RRFC` en colonne F) : 40 périodes par enseignant lauréat,
  au niveau de l'UE développée — périodes `A` = secondaire supérieur, `B` = secondaire
  inférieur, `C` = supérieur TC/TL. Indiquer la fonction et l'UE concernées.
- **Techno-pédagogue** (`RRFT` en colonne F) : code fonction spécifique, **RL10 `2G2`
  obligatoire** ; existe en SI, SS, supérieur TC et TL.

### 7.4 Fonctions de promotion/sélection — questions EA12 (p.155-157)

Système de mentions à porter en `Justifications – Autres` : pas d'appel à candidats →
`moins de 15 semaines` ; sinon `1er appel` / `2ème appel` (3ᵉ+ assimilé au 2ᵉ) ;
et caractère de l'emploi `TV` / `DV` / `mixte` (directeur) ou combinaisons
`1er/2ème appel TV|DV` (directeur adjoint), `appel à candidats TV|DV` (autres sélections).

---

## 8. EA12 bis (supérieur) et EA12 ter (experts) — différences

### 8.1 EA12 bis — spécificités supérieur (p.158-175)

- Pas de codes RTF/FADI ni d'ancien/nouveau régime : colonne **Titre** = `R` (titre requis)
  ou `D` (non porteur du titre requis → **dérogation requise**). La case à cocher « dérogation
  aux titres requis (art. 17 §4 al. 2, loi du 07/07/1970) » **remplace l'ancienne annexe 26**.
- Classification : `CPPM` au lieu de `PPM` (sinon CG/CT/PP/CS idem).
- Colonne supplémentaire **TC / TL** (type court / type long) — remplace le sous-niveau SI/SS.
- La colonne U.E. (9 chiffres + 2 lettres) est identique au secondaire.
- Fonctions de recrutement (AECF-02/10/1968, p.169-170) — **type court** : professeur de CG,
  de PPM, de CS, de CT, de PP, de CT et PP, de philosophie ; **type long** : chargé de cours,
  assistant, professeur, chef de travaux, chef de bureau d'études ; **transversal** : coordinateur
  qualité, conseiller à la formation. NCC : promotion = directeur ; sélection = chef d'atelier,
  directeur adjoint, éducateur-économe, secrétaire de direction ; recrutement = éducateur-
  secrétaire, rédacteur, commis-dactylographe, comptable (CLA et périodes d'occupation non
  remplis pour les NCC ; « part d'autonomie »/« périodes complémentaires » : rattacher à CG/CT/PP).
- Attributions actuelles : globalisation par classification CG/CT/PP/CPPM (pas par fonction).
- EU métier au supérieur : dépêches via l'Inspection (secrétariat DENO), pas VALEXU.

### 8.2 EA12 ter — experts (p.175-188)

Statut (AECF-26/01/1993 ; art. 87bis et 118 D.-16/04/1991) :

- Recrutement possible **jusqu'à 70 ans** (fin de l'année scolaire des 70 ans — art. 76 loi
  du 24/12/1976 ; MDP pensionné admis ; circulaire 8869).
- Diplômes : nécessaires à l'**immatriculation** uniquement (copie obligatoire avec l'EA12 ter
  à l'entrée en fonction) ; pas de régime de titres.
- Document : `EXP.` + intitulé du cours du doc 8bis ; sous-niveau en majuscules `SU`/`SS`/`SI`
  (commencer par le plus élevé) ; **prestations mensuelles** (mois entier, quels que soient les
  jours prestés) ; nb de périodes = celui du contrat pour l'UE visée ; codes DI limités à
  `14` (FSE) et `15` (convention) liés à la source de financement.
- Seules les prestations d'expert figurent sur l'EA12 ter ; les autres prestations vont sur
  EA12/EA12 bis (toujours séparer secondaire et supérieur).

**Relevé mensuel A27** (p.185) : peut désormais regrouper **plusieurs UE** ; une ligne par cours
avec classification, niveau, dates, périodes, financement. Envoi **avant le 1ᵉʳ du mois** si
prestations connues d'avance (paie fin de mois) ; rectificatif obligatoire le mois suivant si
prestations réelles inférieures. Heures non prestées (maladie…) → horaire de récupération
(art. 12 al. 3 AECF-26/01/1993).

**Plafonds (p.186-188)** — règles de validation à implémenter pour tout calcul :

| Règle | Valeur |
|---|---|
| Plafond annuel expert (année scolaire, fonction accessoire incluse) | **260 périodes** (art. 2 AECF-26/01/1993) ; **360** avec autorisation ministérielle (A28) |
| Rémunération d'une période d'expert | `12/1000` du traitement annuel brut (CG/CT) ; `12/1200` (PP) |
| Plafond mensuel en fonction accessoire | `267/1000` (CG/CT) ; `333/1250` (PP) |
| Plafond en fonction principale (expert pur) | `1000/1000` (CG/CT, soit max 83 périodes/mois car 84×12 > 1000) ; `1200/1200` (PP) |
| Dépassement du tiers en fonction accessoire | Max le double (2/3 charge), dans un seul établissement (art. 77 §2 loi 24/12/1976 → annexe A34) |

Exemple de la circulaire : 200/1000 enseignant accessoire + 10 périodes expert
(= 120/1000) → 320/1000 calculé, payé 267/1000 (plafond), 53/1000 perdus ; l'engagement
expert aurait dû être limité à 5 périodes (200 + 60 = 260 ≤ 267).

---

## 9. Codes RTF – RL10 – FADI (p.212-225)

Triple référentiel de codes par fonction enseignante (secondaire) :

- **RTF** : code numérique de la fonction au sens du décret 11/04/2014 (référentiel PRIMOWEB).
- **RL10** : code fonction du moteur de paie — alphanumérique, organisé en séries :
  `A**` = CG, `B**`-`C**` = CT, `D**`-`E**` = PP ; numériques pour NCC/administratif.
- **FADI** : code à 6 chiffres du référentiel fonctions/absences/disponibilités —
  préfixes observés : `29….` = CG, `35….` = CT, `42….` = PP (DI et DS).

Tables complètes dans la circulaire (≈ 480 fonctions) :

| Section | Contenu | Pages |
|---|---|---|
| 7.1 | Professeur de CG au DI (37 fonctions : langues, math, sciences, FLE…) | 212-213 |
| 7.2 | Professeur de CG au DS (36 fonctions) | 213 |
| 7.3 | Professeur de CT au DI (≈ 115 fonctions) | 214-216 |
| 7.5 (sic) | Professeur de CT au DS (≈ 120 fonctions) | 216-219 |
| 7.5 | Professeur de PP au DI (≈ 90 fonctions) | 219-221 |
| 7.6 | Professeur de PP au DS (≈ 95 fonctions) | 221-223 |

> La numérotation des sections de la circulaire comporte un doublon « 7.5 » (CT au DS puis
> PP au DI) ; l'ordre réel est celui des pages.

Exemples (vérifiés) : `Professeur de CG : Français au DI` = RTF 489 / RL10 A15 / FADI 290648 ;
`Professeur de CG : Mathématiques au DS` = RTF 699 / RL10 A27 / FADI 290651 ;
`Professeur de CT : Informatique au DI` = RTF 558 / RL10 B85 / FADI 350706.

**Tables courtes intégrales :**

7.7 — Professeur dans l'EA **supérieur** (RL10 uniquement) :

| Fonction | RL10 |
|---|---|
| Professeur de cours généraux | 282 |
| Professeur de PPM | 280 |
| Professeur de CS musique, éd. musicale | 277 |
| Professeur de CS dessin, éd. plastique | 276 |
| Professeur de CS sténodactylographie | 278 |
| Professeur de CS éducation physique | 289 |
| Professeur de cours techniques | 260 |
| Professeur de pratique professionnelle | 265 |
| Professeur de CT et PP | 270 |
| **Expert** | **228** |

7.8 — Personnel non chargé de cours :

| Fonction | RL10 | FADI |
|---|---|---|
| Éducateur secrétaire | 552 | 710502 |
| Coordinateur qualité | 394 | 470001 |
| Conseiller à la formation | 2D4 | 480001 |
| Agent service interne de prévention et protection du travail | 385 | — |

> Incohérence interne : le code RL10 du coordinateur qualité vaut `384` dans le tableau des
> dénominateurs (p.152) et `394` dans la table 7.8 (p.224). À vérifier auprès de la Direction
> de gestion en cas d'usage.

7.9 / 7.10 / 7.11 — Promotion, sélection, administratif :

| Fonction | RL10 | FADI |
|---|---|---|
| Directeur (promotion) | 110 | 650016 |
| Chef d'atelier | 220 | 70006 |
| Directeur adjoint | 111 | 914001 |
| Éducateur économe | 530 | 707008 |
| Secrétaire de direction | 540 | 709005 |
| Sous-directeur | 150 | 659007 |
| Auxiliaire administratif | 899 | 511010 |
| Commis | 810 | 512012 |
| Comptable | 80A | 514014 |
| Rédacteur | 830 | 522011 |

> Si une application doit valider/proposer les ≈ 480 codes des grandes tables CG/CT/PP,
> les extraire programmatiquement du PDF (texte natif, `pdftotext -layout`, pages PDF
> 214-227) vers un CSV — extraction fiable, colonnes régulières.

---

## 10. Cumul (A2, p.225-229)

- **Cumul interne** = fonctions dans un autre établissement organisé ou subventionné FWB
  (tout niveau : fondamental, secondaire, HE, EA, artistique, CPMS…).
  Procédure : cocher `cumul interne` sur le Doc12 + le MDP complète l'**A2** (nom, adresse,
  n° ECOT de chaque autre établissement ; fonctions ; situation administrative
  définitif/stagiaire/temporaire/contractuel ; niveau ; type ordinaire/spécialisé ; charge
  par semaine ou par année scolaire ; dates début/fin) ; le PO transmet A2 + Doc12 ensemble
  via GEDI. Nouvelle A2 à **chaque modification** en cours d'année.
- Fonction de sélection/promotion/éducateur/paramédical **à horaire complet** qui accepte des
  heures de cours → fonction accessoire, max **1/3 de charge**, mention obligatoire en
  observations : « Fonction accessoire MDP à charge complète et ne pouvant prétendre à des PA ».
- Congé pour exercer provisoirement une autre fonction : **pas** d'A2.
- **Cumul externe** = activité hors enseignement FWB (indépendant, salarié, autre Communauté,
  université, fonds propres…) : depuis le D.-27/01/2006, sans impact pécuniaire/administratif ;
  déclaration auprès du **PO uniquement** (pas à la Direction de gestion).
- La Direction de gestion utilise l'A2 pour appliquer le statut pécuniaire (cumul jusqu'à plus
  d'un temps plein), payer en fonction principale ou accessoire.

---

## 11. Synthèse des règles de validation implémentables

Récapitulatif des contraintes machine-vérifiables extraites de la circulaire :

1. **Identifiants** : ECOT 10 chiffres (structure par réseau, fichier 07 §4) ; FASE entier ;
   matricule 11 positions `[12]AAMMJJNNNN` (4 derniers vides si immatriculation en cours).
2. **Document** : n° séquentiel ≥ 01 par établissement/MDP/année scolaire ; rectificatif =
   nouveau numéro ; date du Doc12 précédent requise.
3. **Code UE** : 9 chiffres + 2 lettres (= `codeFormation` EPROM — validation croisée possible
   avec ListerFormations, spec 01).
4. **1 document par établissement** ; secondaire ≠ supérieur ≠ expert (3 formulaires) ;
   ACS/APE/PTP séparé de T/D.
5. **Énumérations** : F ∈ {D, F, C, E, Ag Q, RRFC, RRFT} ; CLA ∈ {CG, CT, PP, PPM|CPPM, CS} ;
   sit. adm. ∈ {D, Z, V, S, I, St, P, R, A, T, M} ; titre (secondaire) ∈ {TR, TS, TPL, TPNL,
   ATS, ATP} ∪ {R, A, B, N, 3B, AC, Art.20} ; titre (supérieur) ∈ {R, D} ;
   sous-niveau ∈ {SI, SS} (secondaire), {TC, TL} (supérieur), {SU, SS, SI} (expert).
6. **Périodes d'occupation** : format `JJMMAA-JJMMAA`, temporaires uniquement, dans l'année
   scolaire, == dates contrat == DIMONA ; été = EA12 séparé (échéance 30/09).
7. **Codes DI interdits sur Doc12** : 27 (sauf exceptions), 97, EE ; expert : seulement 14/15 ;
   tout DI ⇒ justification (+ formulaire CAD/DPPR le cas échéant) ; congé prime sur réaffectation.
8. **Dénominateurs** : cf. §7.0 (800/1000 annuel enseignant, 36/30/semaine NCC, 38 h admin) ;
   période = 50 min (enseignant) / 60 min (promotion/sélection/auxiliaire).
9. **Plafonds expert** : 260/an (360 avec A28) ; mensuel 267/1000 (CG/CT) ou 333/1250 (PP) en
   accessoire ; 1000/1000 ou 1200/1200 en principal ; rémunération 12/1000 ou 12/1200 par période.
10. **Échéances** : dates-limites mensuelles de réception (fichier 07 §6) ; type d'événement ⇒
    règle de date spécifique (§3).
