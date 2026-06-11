# Circulaires « Droit d'inscription » (DI) — règles métier pour Doc 1D (EPROM) et Inscription (SEPS)

> Spécification fonctionnelle issue des circulaires annuelles « Dispositions applicables en matière de
> droit d'inscription dans l'Enseignement de promotion sociale / pour Adultes ».
> Sources : **9217 du 03/04/2024** (texte intégral, via miroir ICC Bruxelles), **9488 du 16/04/2025**
> (montants via synthèse établissement GHA-WBE), **9731 du 27/05/2026** (métadonnées Gallilex ; PDF à analyser).
> Date d'analyse : 2026-06-10 (session 8)

---

## 1. Chaîne d'abrogation (circulaire annuelle)

| Circulaire | Date | Année concernée | Statut | Gallilex |
|---|---|---|---|---|
| 8914 | 28/04/2023 | 2023-2024 | abrogée par 9217 | — |
| **9217** | 03/04/2024 | 2024-2025 | abrogée par 9488 | doc 51?? — texte intégral récupéré ([miroir ICC](https://www.iccbxl.be/web/data/uploads/pdf/circulaire-9217-di-24-25.pdf)) |
| **9488** | 16/04/2025 | 2025-2026 | abrogée par 9731 | [doc 52388](https://gallilex.cfwb.be/circulaires/52388) |
| **9731** | 27/05/2026 | **2026-2027** (validité 24/08/2026) | **en vigueur** | [doc 53231](https://gallilex.cfwb.be/circulaires/53231) — **texte intégral : `circulaires/53231_0000.pdf`** |

> Gestionnaire : AGE-DGESVR, Direction de l'Enseignement pour Adultes, **Service de la Vérification**
> (C. Simons et al.) — le même service qui gère la circulaire 8684 « Renseignements annuels ».
> ⚠️ Le **mécanisme** (formule, assiette, plafond, exonérations) est stable d'année en année ; seuls les
> **montants indexés** changent. La structure ci-dessous suit la 9217 ; montants 2025-2026 d'après la 9488.

## 2. Formule de calcul du DI

```
DI = forfait (1×/année scolaire) + tarif_niveau × min(périodes, 800)
```

Indexation : `DI(2015+N) = DI(2015) × IPC(01/2015+N) / IPC(01/2015)` (indice des prix à la consommation).

| Montant | 2024-2025 (9217) | 2025-2026 (9488) | 2026-2027 (9731) |
|---|---|---|---|
| Forfait annuel (sec. + sup.) | 32 € | 33 € | **34 €** |
| Tarif/période — secondaire | 0,28 € | 0,29 € | **0,30 €** |
| Tarif/période — supérieur | 0,45 € | *non repris dans la synthèse GHA — à confirmer (≈0,46 €)* | **0,47 €** |
| Plafond de périodes payantes | 800 | 800 | **800** |

> Exemples normatifs 9731 (mêmes cas que la 9217, montants 2026-2027) : 120 p. sec → 70 € ;
> 860 p. sec → 274 € ; 500 sec + 400 sup → 34 + 500×0,30 + 300×0,47 = **325 €** ; remboursement
> multi-étab. : 410 € → 376 € → B rembourse **34 €**. La mécanique est inchangée.

### Règles d'assiette (stables)

1. **Assiette = totalité des périodes prévues au dossier pédagogique** des UE auxquelles l'étudiant
   s'inscrit — « donnant lieu à une rémunération de chargé de cours », **y compris les périodes
   d'encadrement** (stage, épreuve intégrée), de 50 minutes — *que la totalité soit enseignée ou non
   durant l'année*. → côté services : c'est le nombre de périodes du **dossier pédagogique** (cf. Doc 8/8bis,
   `nbPeriodesDoc8`), pas les périodes réellement organisées (Doc 2).
2. **Rattachement à l'année** : une UE compte pour l'année académique dans laquelle se situe son
   **premier dixième** (règle du 1/10ᵉ — même pivot que `regulier1` SEPS).
3. **Plafond 800 périodes** : au-delà, périodes gratuites. En cas de mixte secondaire/supérieur, on
   compte **d'abord les périodes du secondaire**, puis le solde du plafond au tarif supérieur
   (ex. 9217 : 500 sec + 400 sup → 32 + 500×0,28 + **300**×0,45 = 307 €).
4. **Forfait unique par année scolaire**, y compris multi-établissements.
5. **Moment du paiement** : avant le **1ᵉʳ dixième** de l'UE/section (condition de régularité de
   l'étudiant). *(La formulation « au moment de l'inscription » de la synthèse GHA est une pratique
   d'établissement, pas la règle de la circulaire.)*

### Exemples normatifs (9217, montants 2024-2025)

| Cas | Calcul | DI |
|---|---|---|
| 120 p. secondaire | 32 + 120×0,28 | 65,60 € |
| 860 p. secondaire | 32 + 800×0,28 | 256 € |
| 240 p. sec + 10 p. encadr. stage + 4 p. encadr. épreuve intégrée | 32 + 254×0,28 | 103,12 € |
| 120 p. sec + 10 p. sup | 32 + 120×0,28 + 10×0,45 | 70,10 € |
| 500 p. sec + 400 p. sup | 32 + 500×0,28 + 300×0,45 | 307 € |
| Remboursement : étab. A 900 p. sup (392 €) puis étab. B 200 p. sec | recalcul global 32 + 200×0,28 + 600×0,45 = 358 € → **B rembourse 34 €** | |

> ⭐ **Implication client** : le DI est **recalculé globalement** à chaque nouvelle inscription dans
> l'année (multi-établissements compris), avec obligation de remboursement par le 2ᵉ établissement.
> Un helper pyetnic de calcul/contrôle du DI doit donc prendre en entrée *toutes* les inscriptions de
> l'année de l'étudiant, pas seulement celle en cours.

## 3. Exonérations (art. 12 §3 de la loi du 29/05/1959 « Pacte scolaire »)

Liste 9217/9488 (stable) — rapprochement avec l'énumération SEPS `MotifExemptionType` (C01-C07,
spec 11 / registre §7.5) :

| Condition d'exonération (circulaire) | Code SEPS probable |
|---|---|
| Mineurs soumis à l'obligation scolaire | C01 (mineur) |
| Chômeurs complets indemnisés ; travailleurs temps partiel avec AGR | C02 (chômeur) |
| Chômeurs complets indemnisés en formation professionnelle | C02 |
| Demandeurs d'emploi inoccupés inscrits obligatoirement, stage d'insertion, DE en formation prof., demandeurs d'allocations, DE sans revenu (conjoint cohabitant avec charge) | C02 *(à confirmer)* |
| DE dans programmes d'aide à l'emploi (hors ACS/APE) | C02 *(à confirmer)* |
| Personnes en situation de handicap (document probant) | C03 (handicap) |
| Bénéficiaires RIS ou ERIS | C04 (RIS) |
| Miliciens | C07 (autre) *(à confirmer)* |
| **(9731, nouveau)** Étudiants BES AeSI (180 crédits/3 ans) boursiers (décret allocations d'études 18/11/2021) ou titulaires d'une attestation de boursier (coopération au développement) | C07 *(à confirmer — « sera inséré lors de la prochaine actualisation » de la circulaire dossier personnel)* |
| Personnel directeur/enseignant/auxiliaire — formation continuée reconnue | C05 (personnel enseignant) |
| Personnel de l'enseignement CF — recyclage lié à la fonction | C05 |
| Personnes soumises à une obligation imposée par une autorité publique | C06 (autorité publique) |
| Inscrits en UE **FLE ≤ A2** (CECRL) | C07 *(à confirmer)* |
| Inscrits en UE d'**alphabétisation** et UE de niveau **secondaire inférieur dont le CEB n'est pas le titre requis** | C07 *(à confirmer)* |

> ⚠️ **Mapping C01-C07 partiellement hypothétique** (la circulaire liste ~13 conditions, l'enum SEPS
> en code 7). À confirmer avec l'ETNIC ou la circulaire « dossier personnel » (9593, spec 14) qui
> détaille les pièces justificatives par motif.

Autres règles d'exonération :

- **Valorisation des acquis / dispense complète** : pas de DI exigible pour les UE dispensées — lien avec
  `valorisationAcquis` (Organisation v7) et `ValorisationAcquisType` (SEPS). Référence : circ. 6677 du
  30/05/2018, **remplacée par la circ. 9447 du 25/02/2025** (« Modalités de valorisation des acquis pour
  l'admission, la dispense partielle ou complète ») — citée par la 9731.
- **Codiplômation** (≥ 1 étab. supérieur plein exercice CF + 1 étab. EPS, depuis 2024-2025, décret
  09/11/2023) : DI payé auprès de l'**établissement référent** ; si le référent est le plein exercice,
  **aucun DI** côté EPS.
- Les exonérations sont vérifiées **par chaque établissement** à la date du 1ᵉʳ dixième de ses UE
  (multi-établissements hors codiplômation) ; preuve de paiement de l'autre établissement à archiver
  dans le dossier étudiant (circ. 9022 → 9593).

## 4. Règles de déclaration (jonction EPROM)

1. **Forfait ↔ Document 1** : le forfait est déclaré dans l'UE dont le **1ᵉʳ dixième est le plus proche
   du début de l'année académique** ; en cas d'égalité, l'UE **qui se termine en premier**. Le forfait
   doit être **cohérent avec le comptage du Document 1 (colonnes A et B)** — c'est-à-dire les colonnes
   UI « **Elèves A** » (col 2, réguliers ≥ 18 ans) et « **Elèves B** » (col 5, réguliers < 18 ans non
   soumis à l'obligation scolaire à temps plein) du Doc 1 (résolu session 9, spec 20 §1.4).
2. **Étudiants redevables non en ordre de paiement** : exclus du calcul de l'**encadrement**, de
   l'**ajustement de la dotation de périodes** et des **dotations/subventions de fonctionnement**
   → impacte `nbEleves5ieme` (Doc 1D) et les comptages du Doc 1.
3. **Règle de l'arrondi** (loi 02/05/2019, depuis 01/12/2019) : paiements espèces/électroniques arrondis
   aux 0/5 cents **sur le total perçu uniquement** — jamais sur le DI calculé par UE. Les discordances
   minimes DI perçus vs constatés sont tolérées. → `mtDroitsInscription` (Doc 1D) porte des montants
   **constatés** (non arrondis).
4. **Frais de dossier (DIC)** : mentionnés par les établissements (synthèse GHA) au prorata des périodes —
   propres à l'établissement, **hors circulaire DI** et hors `mtDroitsInscription`. Le « périmètre DIC »
   était déjà un point à confirmer de la session 7.

## 5. Impacts sur les specs existantes

| Spec | Impact |
|---|---|
| **06 (Doc 1D)** | ⭐ **Règle explicite 9731 (§2, Remarque)** : « le montant des droits d'inscription pris en compte sur le **Document 1D** doit correspondre au montant total des droits d'inscription **constatés** sur la dernière version du reçu/fiche d'inscription, **qu'il ait été perçu ou non perçu** ». Tout DI perçu doit être constaté et comptabilisé par le vérificateur (l'inverse n'est pas vrai). → `mtDroitsInscription` = constaté, jamais arrondi par UE ; exclusion des non-payeurs du comptage `nbEleves5ieme` |
| **11 (SEPS Enregistrer Inscription)** | sémantique de `droitInscription`/`MotifExemptionType` (§3) ; pivot du 1ᵉʳ dixième = `regulier1` ; DIS (hors CEE) régi par d'autres textes |
| **03 (Doc 1 Population)** | cohérence forfait ↔ colonnes A/B ; non-payeurs hors comptages |
| **04 (Doc 2 Périodes)** | l'assiette DI n'est **pas** le Doc 2 (réellement organisé) mais le dossier pédagogique (Doc 8/8bis) |
| **05 (Doc 3)** | confirme le rôle de référence de `nbPeriodesDoc8` (périodes « dossier pédagogique ») |

## 6. Points ouverts

- ~~Extraire du PDF 9731 les montants 2026-2027~~ ✅ fait (34 € / 0,30 / 0,47). Reste : tarif supérieur
  2025-2026 exact de la 9488 (anecdotique — année écoulée).
- Confirmer le mapping exonérations ↔ `MotifExemptionType` C01-C07 (ETNIC / 9593 ; la 9731 renvoie
  explicitement à la circulaire « dossier personnel » pour le détail des cas). Le cas BES AeSI boursier
  (nouveau 2026-2027) n'a probablement **pas encore de code SEPS dédié**.
- La 9217/9731 référencent la **8684** pour le comptage Document 1 (colonnes A/B) → voir spec 17.
- Se procurer la **9447** (VA admission/dispense, 25/02/2025) si la VA devient un sujet pyetnic.
