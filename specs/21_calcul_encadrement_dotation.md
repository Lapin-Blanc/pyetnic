# Calcul de l'encadrement et de la dotation de périodes (Enseignement pour Adultes / Promotion sociale)

> Spécification fonctionnelle « financement » — comment les chiffres récupérables via les services
> EPROM/SEPS se transforment en **encadrement** (équipe) et en **dotation de périodes** (rémunération des enseignants).
> Sources : décret du 16/04/1991 (coordonné) + arrêtés + circulaires « PS » recensées par la circulaire-répertoire **2816 du 13/07/2009** ; circulaires calendrier/DI/renseignements déjà analysées (specs 16-19) ; apport métier de l'utilisateur.
> Date d'analyse : 2026-06-10 (session 9bis — mise à jour avec le décret coordonné)
>
> ✅ **Statut** : **complet et confirmé verbatim**. (1) **Décret coordonné du 16/04/1991** (`circulaires/16184_0036.pdf`,
> MAJ Gallilex 19/12/2025) — dotation, périodes-élèves, catégories, norme d'autonomie. (2) **Arrêté GCF du 22/11/2002**
> « fixant les règles des ajustements des dotations de périodes dans l'Enseignement pour Adultes » (numac `2003029045`,
> **version coordonnée Justel MAJ 18/08/2025**) — **table de pondération et mécanisme d'ajustement** (art. 3-4).
> → la chaîne de calcul est désormais entièrement spécifiée ; il ne reste plus de 🔶 bloquant.

---

## 1. Les deux grandeurs à ne pas confondre

| Grandeur | Ce qu'elle finance | Base de calcul |
|---|---|---|
| **Encadrement** | l'**équipe** (personnel **administratif**, direction, auxiliaire d'éducation) | les **périodes-élèves (PE)** |
| **Dotation de périodes** | les **périodes à consommer pour rémunérer les enseignants** (chargés de cours) | les **périodes-élèves *pondérées*** (coefficients par catégorie) |

> C'est la distinction structurante (confirmée par l'utilisateur). Les **mêmes périodes-élèves** servent de base aux deux, mais la **dotation applique une pondération** que l'encadrement n'applique pas.

Deux principes temporels/financiers (specs 17 & 19) :
- La **dotation de périodes** est une **enveloppe attribuée chaque juillet pour l'année civile suivante** → gestion **par année civile** (découpage 16 semaines 2025 + 24 semaines 2026 = 40 semaines numérotées, spec 17). D'où la **ventilation par année civile** des périodes du Doc 2 (spec 04).
- Les périodes des **dossiers pédagogiques** des UE organisées sont **prélevées** sur la dotation (décret art. 82-93, 102).

---

## 2. Cadre légal et réglementaire

| Texte | Objet | Spec liée |
|---|---|---|
| **Décret 16/04/1991 (coordonné 19/12/2025), art. 82-93, 99-102** | ✅ **dotations de périodes** (ch. II) et **périodes-élèves** (art. 99) — base légale confirmée verbatim | — |
| Décret 30/06/1998, art. 55 | encadrement différencié / discriminations positives | — |
| **Arrêté GCF 22/11/2002** (numac 2003029045, coord. 18/08/2025) | ✅ **règles des ajustements** + **table de pondération** (art. 1-7) — délégué par l'art. 87 du décret | — |
| **Arrêté GCF 09/07/2004, art. 7** | dossiers pédagogiques → **part d'autonomie** (cf. décret art. 8/137 : « part d'autonomie de l'horaire de référence minimum ») 🔶 | — |
| Arrêté GCF 20/07/1993 | dédoublements et regroupements (min. 1 élève, régime 1) | spec 19 |
| Décrets « diverses mesures » 09/02/2017, 14/11/2018, 20/07/2022 | modifications EPS/EA (état courant) 🔶 | — |
| **Circulaire PS 327/96** | **calcul des périodes-élèves** + cas particuliers (encadrement stages, épreuve intégrée, alternance) 🔶 | — |
| **Circulaire PS 402/03** | nouvelles règles des **ajustements** des dotations de périodes 🔶 | — |
| Circulaires PS 357/98 & PS 422/06 | conseil des études, part supplémentaire, périodes supplémentaires, **expertise pédagogique et technique** | spec 19 (lignes 95/96) |
| Circulaire **5447 (2015)** + dossiers pédagogiques | **part d'autonomie ≈ 20 %** | — |
| Circulaire-répertoire **2816 (13/07/2009)** | recense l'ensemble des dispositions PS (vade-mecum) | — |
| Circulaires **8684** (renseignements annuels), **9487** (calendrier/dotation), DI **9217/9488/9731** | mise en œuvre annuelle | specs 19, 17, 16 |

> Terminologie : depuis 2025, l'« enseignement de promotion sociale » est dénommé **« Enseignement pour Adultes »** ; le décret du 16/04/1991 est désormais intitulé « organisant l'enseignement pour adultes ». Les textes « PS » historiques restent la référence opérationnelle jusqu'à refonte.

---

## 3. Périodes-élèves (PE) — l'assiette commune

**Formule légale — décret art. 99 (✅ verbatim)** :

```
PE(UE)          = nombre de périodes de l'UE réellement organisées durant l'année civile
                  × nombre d'élèves réguliers concernés
PE(établissement) = Σ PE(UE ou parties d'UE réellement organisées durant l'année civile)
```
> Donc : produit **périodes réellement organisées × élèves réguliers**, sommé sur toutes les UE. La base
> est l'**année civile** (cohérent avec la gestion de la dotation par année civile, §1) et les périodes
> **réellement organisées** (pas seulement planifiées).

**Norme de rationalisation (art. 98, 100, 101 — à ne pas confondre avec la « part d'autonomie » du §4)** :
chaque établissement autonome doit générer un **minimum de périodes-élèves** : **30 000 PE** (siège dans un
arrondissement < 125 hab/km²) ou **40 000 PE** (autres cas). En-dessous au 31/12, l'établissement **perd son
autonomie** au 1er janvier suivant (fusion ou fermeture). C'est ici le sens « autonomie **de l'établissement** ».

- **Étudiants réguliers comptabilisés** : déterminés par les règles de comptage aux **1ᵉʳ/10ᵉ et 5ᵉ/10ᵉ** (circulaire 9593, spec 14) → matérialisés par `regulier1`/`regulier5` côté SEPS (spec 11). CM (certificat médical) assimilé à présence ; dispense complète = exclu.
- **Périodes de l'UE** : périodes du **dossier pédagogique** (Doc 8bis, `nbPeriodesDoc8`), **part d'autonomie comprise** (cf. §4).
- **Exclusion** : les étudiants **redevables du droit d'inscription non en ordre de paiement** ne sont **pas** pris en compte pour l'encadrement, l'**ajustement de la dotation**, ni les subventions de fonctionnement (specs 16 & 19).

### Cas particuliers (comptés à part — PS 327/96 ; specs 19)
| Cas | Règle de calcul (spec 19) |
|---|---|
| Encadrement de **stage** / **épreuve intégrée** | col. 18+19 = **col. 14 × périodes prévues par étudiant** |
| Périodes **réservées** (cas particuliers) | **périodes réservées × nombre moyen de PE par période organisée** (arrondi 2ᵉ décimale) |
| **Interventions extérieures (IE)** | **comptent pour les PE** (encadrement) mais **n'entrent pas dans l'ajustement** de la dotation |
| Suivi pédagogique (ligne 96), expertise pédagogique/technique (ligne 95), périodes supplémentaires, valorisation des acquis (VA), conseil des études, milieu carcéral / e-learning | régimes spécifiques (lignes 91-96, PS 357/98 / 422/06) 🔶 |

---

## 4. Part d'autonomie (≈ 20 %)

> ⚠️ **Deux « autonomie » distinctes** : (a) ici, la **part d'autonomie de l'horaire de référence** d'une UE
> (notion de **dossier pédagogique**) ; (b) au §3, la **norme d'autonomie de l'établissement** (30 000/40 000 PE,
> art. 100-101). Sans rapport l'une avec l'autre.

Le décret (art. 8 et 137 ; compétence du Conseil général) prévoit « la fixation de la **part d'autonomie de
l'horaire de référence minimum** et de la **part supplémentaire maximale** de l'horaire de référence des unités
d'enseignement […] qui peut être utilisée par chaque établissement **sans modifier la certification** obtenue sur
la base du dossier de référence minimum ». Le **dossier pédagogique** fixe donc le nombre **minimum** de périodes
par cours **et** cette part d'autonomie ; elle **correspond généralement à ≈ 20 %** du total des périodes (valeur
issue des dossiers / arrêté 09/07/2004 art. 7 ; circ. 5447 — 🔶 taux exact à confirmer par dossier).

- La part d'autonomie **entre dans le total des périodes** de l'UE → donc dans les **PE** et dans la **consommation de dotation**, mais son emploi est **à la main de l'établissement**.
- Lien horaire (spec 17) : l'horaire doit couvrir **100 %** des périodes du dossier pédagogique (autonomie comprise), avec **≥ 90 %** effectivement dispensées.

---

## 5. De l'assiette aux deux résultats

### 5.1 Encadrement (équipe administrative)
Calculé directement sur les **PE** (cas généraux + particuliers), sans pondération de catégorie. Sert à déterminer les charges du **personnel administratif / direction / auxiliaire d'éducation** (décret art. 35 pour le comptage des étudiants réguliers ; art. 82-93 pour l'encadrement). 🔶 (paramètres/seuils exacts à confirmer).

### 5.2 Dotation de périodes (rémunération des enseignants)

**Unité & catégories (✅ décret)** : la dotation est exprimée en **périodes de 50 minutes** (art. 82, « périodes
organiques »). Chaque période appartient à une **catégorie** (art. 83 §1) — c'est l'**axe de pondération** :

| Catégorie | Périmètre |
|---|---|
| **A** | enseignement **secondaire supérieur** (EA) |
| **B** | enseignement **secondaire inférieur** (EA) |
| **C** | enseignement de **niveau supérieur** (EA) |

> Dotation **attribuée par année civile** (art. 86). L'art. 87 délègue les règles d'ajustement à l'**arrêté GCF du
> 22/11/2002** (✅ ci-dessous).

#### Périodes-élèves **pondérées** (arrêté 22/11/2002, art. 3-4 — ✅ verbatim)

```
PE pondérées(cours) = périodes-élèves(cours) × coefficient pédagogique × coefficient de niveau
```

**Coefficient pédagogique** (art. 3, 1°, a) :
| Valeur | Cours concernés |
|---|---|
| **1** | cours généraux ; cours techniques (industriels et non-industriels) ; cours spéciaux ; psychopédagogie et méthodologie |
| **1,6** | cours généraux de remise à niveau / méthodologie spéciale ; cours techniques de méthodologie spéciale ; travaux de labo (ind./non-ind.) ; pratique professionnelle **non** industrielle ; cours techniques et de pratique professionnelle ; cours spéciaux de dactylographie |
| **2,8** | pratique professionnelle **industrielle** ; pratique professionnelle de **nursing** |

**Coefficient de niveau** (art. 3, 1°, b) — ⚠️ catégories de l'art. 83 du décret + une **catégorie D** maintenue dans le barème :
| Catégorie | Coefficient |
|---|---|
| **B** (secondaire inférieur) | **1** |
| **A** (secondaire supérieur) | **1,25** |
| **C** (supérieur) | **1,5** |
| **D** | **1,8** *(⚠️ « D » abrogé du décret en 2021 mais toujours présent au barème de l'arrêté — à clarifier)* |

**Définition des assiettes (art. 1)** :
- **Cas généraux** = périodes des cours du dossier pédagogique **hors part d'autonomie et hors encadrement**.
- **Cas particuliers** = encadrement, périodes supplémentaires, valorisation des acquis (formels/informels/non-formels),
  suivi pédagogique, conseil des études, expertise pédagogique/technique (+ **carcéral / e-learning** assimilés).
- **Périodes prévues** = déclarées par l'établissement ; **périodes réelles** = déclarées et réellement utilisées.

**Calcul des PE pondérées d'un établissement (art. 4, procédure en 6 étapes)** :
1. **Cas généraux** : cours par cours, PE pondérées générées par les **périodes prévues** de l'**avant-dernière année
   civile** (art. 2).
2. **Part d'autonomie** : on ajoute ses PE pondérées — la part d'autonomie se **répartit au prorata des autres cours**
   du dossier pédagogique.
3. **Limitation « organique »** : réduction au prorata des périodes **ne provenant pas** de la dotation de l'établissement
   → PE pondérées **organiques** par formation, totalisées.
4. **Cas particuliers** : ajout sur la base du **nombre moyen de PE pondérées par période** des activités hors cas
   particuliers. → chaque période d'un cas particulier « vaut » la **moyenne PE pondérées/période** de l'établissement.
   - **EPT = Expertise Pédagogique et Technique** (cas particulier ; = flag `organisationPeriodesSupplOuEPT` spec 02,
     case « périodes suppl./EPT » spec 19, préfixe `EPT` sur l'EA12 spec 08 — **≠ épreuve intégrée**) :
     `PE pondérées(EPT) = périodes réelles organiques d'EPT × moyenne PE pondérées/période`. Volume : **40-800 périodes**
     par activité, 1,8 h/période (décret art. 91/4) ; plafond **10 %** de la dotation organique avec les autres
     activités hors cours (art. 91/6).
   - *Valorisation des acquis non-formels/informels → 10 % des périodes prévues de l'UE.*
5. **Neutralisation** des augmentations ponctuelles de dotation.
6. **Corrections pour dépassements** (périodes utilisées au-delà des périodes utilisables).

#### Mécanisme d'ajustement (arrêté 22/11/2002, art. 3 §2 et art. 5-7)
- **Dotation de référence** = dotation de l'**année précédente** (art. 1, h). On compare les **PE pondérées** de
  l'avant-dernière année civile aux **PE pondérées de référence**.
- **Intervalle de neutralisation ±8 %** (art. 3, 2° ; art. 5) : dans l'intervalle → dotation **inchangée** ; en-deçà →
  **baisse** ; au-delà → **hausse** (seulement si les baisses dégagent du disponible — enveloppe fermée).
- **Baisse** (art. 6) : réduction = **¼ de la dotation × |% de baisse|**, **plafonnée à 50 périodes** ; le total
  récupéré est **redistribué** aux établissements en hausse, au prorata des PE pondérées gagnées.
- **Enveloppe globale** (art. 7) : le % de variation de la dotation globale est appliqué à chaque établissement.
- **Délai** (art. 2) : documents de calcul à l'Administration dans **35 jours calendrier** à compter du 1ᵉʳ dixième.

> Catégories/cours lisibles côté Doc 2 via `coCategorie`/`coCatCol` (spec 04) → c'est l'entrée de la pondération.

**Déductions (✅ art. 87bis)** : périodes hors horaire approuvé, périodes prévues mais non enseignées (sans dispense
régulière), prestations rémunérées non déclarées, ouvertures antérieures à l'autorisation (+ pertes de charge /
disponibilités) — déduites **sans** ajustement.

**Réserve & dépassement (✅ art. 91 et 93)** : `réserve = dotation/école − périodes utilisées`, jamais **négative**.
Tout dépassement → l'année civile suivante, **réduction de 1,5×** le dépassement (puis coefficient correcteur la 2ᵉ
année, réintégration la 3ᵉ).

**Plafonds activités hors cours (✅ art. 91/6 et 91/4)** : conseil des études, suivi pédagogique, admission/sanction,
**expertise pédagogique et technique**, activités de formation consomment la dotation, dans la limite de **10 % de la
dotation organique** (art. 82) — dont **≤ 1 %** pour les seules activités de formation. Une activité d'expertise =
**40 à 800 périodes** (1,8 h/période).

**Supplément « suivi pédagogique » (✅ art. 36 §2)** — en **périodes B**, selon les **périodes-élèves générées**
(⚠️ corrige la table provisoire antérieure, qui était erronée) :

| Périodes-élèves générées | Supplément (périodes B) |
|---|---|
| 30 000 – 119 999 | **100** |
| 120 000 – 239 999 | **200** |
| 240 000 – 359 999 | **300** |
| 360 000 – 499 999 | **400** |
| ≥ 500 000 | **500** |

(+ enveloppe **9 600 périodes B** pour les conseillers pédagogiques EA, répartie au prorata — art. 36bis.)

**Consommation** : les **attributions** aux enseignants (Doc 3, `nbPeriodesAttribuees`) consomment la dotation et sont
**plafonnées** par les périodes organisées (Doc 2 + IE) — erreurs `1538`/`1574`/`1575`/`1576` (spec 05).

---

## 6. Chaîne de calcul ↔ services (récupérable par pyetnic)

```
SEPS Inscriptions (spec 11-12)            EPROM Doc 1 / 1D (spec 03/06)
  regulier1/regulier5, fse,                 nbEleve* (1/10ᵉ), nbEleves5ieme (5/10ᵉ),
  droitInscription (payé ?)                  DI / motif exemption
        │                                            │
        └─────────────┬──────────────────────────────┘
                      ▼
         Étudiants réguliers comptabilisés  ── (DI non payé → exclu)
                      │
   Doc 2 (spec 04) ───┤  périodes par UE (prévues/réelles, par année civile),
   Doc 8bis ──────────┤  catégories CG/CT/PP/CS (coCategorie), IE, part d'autonomie
                      ▼
              PÉRIODES-ÉLÈVES (PE)  = Σ (périodes UE × étudiants) + cas particuliers
                ├────────────────────────────► ENCADREMENT (équipe)        [PE]
                └──(× coefficients de catégorie)► DOTATION DE PÉRIODES       [PE pondérées]
                                                   │  + supplément par tranches de PE
                                                   │  − ajustement (population réelle, DI exclus)
                                                   ▼
                            Doc 3 (spec 05) : attributions enseignants ≤ dotation (consommation)
```

---

## 7. Faisabilité pyetnic

**Récupérable / calculable** :
- Tous les **intrants** : populations (Doc 1/1D), périodes et catégories (Doc 2, Doc 8bis), attributions (Doc 3), inscriptions individuelles + statut régulier + FSE + DI (SEPS).
- Le **comptage** des étudiants réguliers (règles 1/10ᵉ-5/10ᵉ) et donc les **périodes-élèves** (cas généraux ; cas particuliers stage/épreuve intégrée via col. 14).
- ✅ Le **calcul complet** des **PE pondérées** (coefficients pédagogiques 1/1,6/2,8 × coefficients de niveau B/A/C/D) et le **mécanisme d'ajustement** (±8 %, baisse plafonnée, redistribution) — formule désormais entièrement spécifiée (décret art. 99 + arrêté 22/11/2002 art. 3-4).

**Non disponible via les web services** :
- La **dotation de base / dotation de référence** (enveloppe de l'année précédente) — **communiquée par l'administration** (juillet, par année civile), historiquement consultée via le système hôte **HOD/CICS « pot K » (écran 59)**, hors API (spec 19). C'est le **seul intrant non récupérable** par service.

**Conclusion** : pyetnic peut désormais **reproduire le calcul** — périodes-élèves, **pondération** (table embarquée), encadrement, consommation, contrôle 90 %/100 %, plafonds Doc 3 — et **estimer la dotation** dès lors qu'on lui fournit la **dotation de référence** (saisie) et qu'on neutralise l'effet « enveloppe fermée » (l'ajustement inter-établissements ±8 % dépend des autres écoles, donc une **estimation par établissement** est exacte *à la dotation de référence + variation d'enveloppe près*). La **valeur officielle** reste celle de l'administration. Un module « financement » paramétrable par **millésime** (coefficients, ±8 %, plafond 50, plafonds 10 %/1 %) est recommandé, séparé du client SOAP.

---

## 8. Points à confirmer (verbatim, sur les textes)

✅ **Confirmé verbatim** — décret coordonné (`16184_0036.pdf`, MAJ 19/12/2025) **et** arrêté GCF 22/11/2002
(numac `2003029045`, coord. 18/08/2025) :
- **PE** = périodes réellement organisées × élèves réguliers (décret art. 99) ; **catégories A/B/C** (art. 83) ;
  norme **30 000/40 000 PE** (art. 100) ; période **50 min** (art. 82) ; dotation **par année civile** (art. 86) ;
  **déductions** (art. 87bis) ; **réserve + dépassement 1,5×** (art. 91/93) ; **plafond 10 %** activités hors cours,
  **≤ 1 %** formation (art. 91/6) ; expertise **40-800 périodes** (art. 91/4) ; supplément suivi pédagogique
  100-500 périodes B (art. 36 §2).
- **Pondération** : coefficient pédagogique **1 / 1,6 / 2,8** × coefficient de niveau **B=1 / A=1,25 / C=1,5 / D=1,8** ;
  **cas généraux / part d'autonomie / cas particuliers** ; calcul des PE pondérées en 6 étapes ; **neutralisation ±8 %** ;
  baisse plafonnée à **50 périodes** (¼ × |%|) ; redistribution au prorata (arrêté art. 1-7).

Restent ouverts (mineurs, **non bloquants**) :
1. 🔶 **Catégorie « D » du barème** (coef. niveau 1,8) : présente dans l'arrêté mais le « D » a été **abrogé de
   l'art. 83 du décret en 2021** → clarifier ce que recouvre encore « D » (sortie en voie d'extinction ?).
2. 🔶 **Arrêté GCF du 09/07/2004** (dossiers pédagogiques, art. 7) : **taux exact** de la part d'autonomie (≈ 20 %).
   Gallilex `textes-normatifs/40726` (à confirmer) ; circ. **5273**/**5447**.
3. 🔶 **Modèle d'annexe** de l'arrêté 22/11/2002 (documents administratifs de calcul, art. 2) : utile pour le mapping
   exact avec les colonnes des Doc 1/2 (déjà largement couvert par les specs 19 et 20).
4. ✅ **Actualisation EA** : décret coordonné 19/12/2025 et arrêté coordonné 18/08/2025 — **tous deux à jour**.

---

## Sources
- [Circulaire 2816 du 13/07/2009 — répertoire des dispositions PS (recense décret art. 82-93, arrêté 22/11/2002, PS 327/96, PS 402/03)](http://www.enseignement.be/upload/circulaires/000000000002/3023_20090715153104.pdf)
- **Décret du 16/04/1991 (coordonné, MAJ 19/12/2025)** — déposé localement : `circulaires/16184_0036.pdf` (71 p.) — articles 82-93, 99-102 (source verbatim de cette spec). Page Gallilex : https://gallilex.cfwb.be/textes-normatifs/16184
- **Arrêté GCF du 22/11/2002 (coordonné, MAJ 18/08/2025)** — règles d'ajustement + **table de pondération** (art. 1-7), source verbatim §5.2. [Justel](https://www.ejustice.just.fgov.be/eli/arrete/2002/11/22/2003029045/justel) · [PDF consolidé](https://www.ejustice.just.fgov.be/img_l/pdf/2002/11/22/2003029045_F.pdf) (à déposer dans `circulaires/` si souhaité).
- [Enseignement.be — dossiers pédagogiques / part d'autonomie (circ. 5447/2015)](https://gallilex.cfwb.be/sites/default/files/imports/41427_000.pdf)
- [Circulaire 4903 du 26/06/2014 — DI (redevables non payés exclus du calcul de l'encadrement / ajustement de la dotation)](https://gallilex.cfwb.be/sites/default/files/imports/39963_000.pdf)
- Specs internes liées : `04_formation_periodes_v1.md`, `05_document3_v1.md`, `06_formation_droits_inscription_v1.md`, `16_circulaires_droit_inscription.md`, `17_circulaire_9487_calendrier_dotation.md`, `19_circulaire_8684_renseignements_annuels.md`.
