# Circulaire 8829 (01/02/2023) — Enseignement hybride : conditions d'organisation et encodage EPROM

> Source : `circulaires/50609_000.pdf` (15 p. dont annexe AGCF, texte natif). Circulaire administrative,
> validité 01/02/2023, **toujours en vigueur** (jamais abrogée). Base légale : **AGCF du 21/12/2022**
> (effets dès la rentrée 2022-2023), en annexe 1 de la circulaire.
> Date d'analyse : 2026-06-10 (session 8)

---

## 1. ⭐ « DOC A » identifié — résolution du point ouvert sessions 4/5

La circulaire écrit (section « Encodage du Document A ») :

> « Lors de l'encodage du **DOC A (déclaration d'ouverture dans l'application Eprom)**, il convient
> de cocher la case « enseignement hybride » si l'UE / AF est organisée sous cette forme. »

et : « il ne sera plus possible d'utiliser les cases « **e-learning** » et « **partiellement à
distance** » […] La case « **enseignement hybride** » devra donc être cochée ».

Ces trois « cases » sont exactement les champs `eLearning`, `partiellementDistance`,
`enseignementHybride` de **`FormationOrganisationCT`** (service Formation Organisation v7, spec 02).

**Conclusion** : **Doc A = la déclaration d'ouverture = le document « Organisation »** (géré par le
service Formation Organisation), et **non le Document 1 (Population)** comme supposé en session 4.

Conséquence sur le workflow inter-documents (erreur `20102` du Doc 3 : « Les "Doc A" et "Doc 2"
doivent être approuvés pour pouvoir accéder au "Doc 3" ») :

```
Organisation (« Doc A », statut StatutCT → Approuvé) ─┐
                                                       ├─► Document 3 (Attributions) accessible
Document 2 (Périodes, swAppD2=1) ─────────────────────┘

Document 1 (Population) et Doc 1D (Droits) : workflows propres, non bloquants pour le Doc 3
(sous réserve du libellé exact : voir « Limite » ci-dessous).
```

> **Limite** : le manuel du Doc 3 reste ambigu (libellé littéral « Doc A »), mais la 8829 fournit la
> première **définition officielle** du terme. L'ancienne hypothèse « Doc A = Document 1 » est
> rétrogradée ; on note toutefois que la vue Formations Liste fusionne Population+Périodes dans un
> même statut, donc un test TQ (approuver Organisation+Doc 2 sans approuver Doc 1, puis appeler
> Doc 3) trancherait définitivement.

## 2. Définition et conditions d'organisation de l'hybride

- **Enseignement hybride** = forme d'enseignement **mixant** des activités d'apprentissage en
  présentiel et à distance (synchrone ou asynchrone), avec outils numériques de communication /
  interaction / collaboration. Remplace l'« e-learning » depuis le 29/08/2022.
- **Organisation distincte** : toute UE/AF en hybridation fait l'objet d'une **organisation distincte**
  de celle proposée entièrement en présentiel (art. 3 AGCF) → côté EPROM, **deux
  `numOrganisation` différents** pour la même UE selon le mode.
- **Concertation sociale préalable** obligatoire (art. 2 AGCF) — sauf bascule exceptionnelle.
- **Bascule exceptionnelle présentiel → hybride** (art. 3) : possible pour raisons conjoncturelles
  (grève des transports, confinement…) avec **préavis de 48 h** ; dans ce cas **ni avis de
  concertation ni déclaration à l'Administration** → l'organisation EPROM reste « présentiel ».
- **Horaire obligatoire pour toutes les activités**, quel que soit le mode (présentiel, distanciel
  synchrone ou asynchrone), et respect du **volume total des périodes du dossier pédagogique**
  (cohérent avec la règle 100 %/90 % — spec 17).
- Une même organisation hybride peut comporter **plusieurs groupes d'étudiants** ; la scénarisation
  pédagogique (art. 5 AGCF) s'applique intégralement par mode et par groupe, sinon étudiants
  considérés absents.
- **AF (activités de formation)** : mêmes règles (réf. circulaire 6351 du 13/09/2017) — lien avec le
  switch `activiteFormation` (Organisation v7).

## 3. Neutralité sur les périodes, la dotation et le DI

L'hybride est **strictement neutre** sur les paramètres de financement :

1. **Cadre PNCC** (personnel non chargé de cours) : périodes-élèves = total des périodes des UE/AF
   suivies par tous les élèves **réguliers** (hors cas particuliers) — comme en présentiel.
2. **Ajustement de la dotation de périodes** : périodes-élèves **pondérées** calculées comme en
   présentiel.
3. Les périodes prévues au dossier pédagogique de l'UE hybride sont **prélevées de la dotation de
   périodes** de l'établissement — comme en présentiel.
4. **DI inchangé** : mêmes montants, mêmes exemptions, mêmes conditions de régularité (spec 16).

> → Pour pyetnic : `enseignementHybride` est un **marqueur déclaratif** (statistique + état des lieux
> pluriannuel gouvernemental) sans effet sur les calculs de périodes/DI. La circulaire insiste sur le
> respect « scrupuleux » de cette instruction d'encodage.

## 4. Traçabilité documentaire (hors services SOAP, utile au contexte)

- Reçu/fiche d'inscription : UE hybrides identifiées par la lettre **M**.
- Listes de présence : mention **HYBRIDE** ; codes de présence : `P` (ou trait vertical) présence en
  classe, **`M` cours à distance**, `A` (ou trait horizontal) absent, `D` dispensé partiellement.
  Les anciens codes `HA`/`HS` (circulaire 8710 du 05/09/2022) sont abrogés, lus comme `M`.
- Cours asynchrone : participation rattachée à la **date prévue à l'horaire initial** ; comptage selon
  la participation validée par le chargé de cours ; justificatifs à disposition du vérificateur.
- Dossier étudiant identique au présentiel (pièce d'identité, reçu signé, paiement DI ou exemption
  valable à la date du **1ᵉʳ dixième**…).

## 5. Impacts sur les specs existantes

| Spec | Impact |
|---|---|
| **02 (Organisation v7)** | sémantique précise de `enseignementHybride` (≥ 2022-2023, erreurs `20031`/`30008`) ; `eLearning`/`partiellementDistance` interdits pour UE débutant ≥ 29/08/2022 ; organisation hybride = organisation **distincte** ; bascule 48 h sans réencodage |
| **05 (Doc 3)** | ⭐ « Doc A » (erreur `20102`) = **Organisation**, pas Document 1 — hypothèse session 4 corrigée |
| **04 (Doc 2)** | volume des périodes du dossier pédagogique inchangé en hybride ; périodes-élèves (pondérées) calculées comme en présentiel |
| **16 (DI)** | hybride sans effet sur le DI |

## 6. Points ouverts

- Test TQ pour confirmer définitivement le déclencheur de `20102` (approbations Organisation + Doc 2
  suffisantes ?).
- Récupérer la circulaire **6351** (13/09/2017, activités de formation) si le switch `activiteFormation`
  doit être documenté plus finement.
- Annexe 1 (texte AGCF 21/12/2022) non dépouillée en détail (attributions chargé de cours / PO —
  hors périmètre pyetnic).
