# Test grandeur nature en production — ouverture organisation F328 (2026-2027)

**Date du test :** 2026-06-11
**Environnement :** production (`ENV=prod`, services-web.etnic.be)
**Compte :** ec003052@adm.cfwb.be — établissement 3052, implantation 6050
**Objectif :** ouvrir une organisation de la formation 328 sur l'année scolaire 2026-2027, du 15/09/2026 au 13/10/2026, et valider le comportement de `pyetnic.eprom` en conditions réelles.

## Déroulement

### 1. `lister_formations_organisables(annee_scolaire="2026-2027")` — OK

- 110 formations organisables retournées pour 2026-2027.
- Formation 328 présente : `INFORMATIQUE : INTRODUCTION A L'INFORMATIQUE`, code `750102U21D1`, `organisations=[]` (aucune organisation existante).

### 2. `creer_organisation(...)` — OK

Appel minimal (uniquement les champs obligatoires, tous les booléens optionnels à `None`) :

```python
eprom.creer_organisation(
    annee_scolaire="2026-2027",
    etab_id=3052,
    impl_id=6050,
    num_adm_formation=328,
    date_debut=date(2026, 9, 15),
    date_fin=date(2026, 10, 13),
)
```

Réponse serveur :

- `numOrganisation=1` attribué par le serveur et correctement reconstruit dans l'`OrganisationId` retourné (parsing de la réponse `CreerOrganisation` sans id fourni — OK).
- `nombreSemaineFormation=4` calculé côté ETNIC (15/09 → 13/10 = 4 semaines).
- Statut : `Encodé école`, daté du 2026-06-11.

### 3. `lire_organisation(...)` — relecture OK

Relecture avec l'id complet (`implId=6050`) : données identiques à la création.
Valeurs par défaut appliquées côté serveur pour les champs optionnels omis :

- Tous les booléens (`organisationPeriodesSupplOuEPT`, `valorisationAcquis`, `enPrison`, `eLearning`, `reorientation7TP`, `activiteFormation`, `conseillerPrevention`, `partiellementDistance`, `enseignementHybride`, `interventionExterieure50p`) → `False`
- `numOrganisation2AnneesScolaires` → `0`
- `typeInterventionExterieure` → `None`
- Statuts Doc 1/2/3 (`statutDocumentPopulationPeriodes`, `statutDocumentDroitsInscription`, `statutDocumentAttributions`) → `None` (cohérent avec SPEC : statut « Encodé école » ⇒ Doc 1/2/3 pas encore accessibles)

### 4. `lister_formations(annee_scolaire="2026-2027")` — OK

La nouvelle organisation apparaît dans l'aperçu de la formation 328.
**Confirmation du gotcha implId** : dans l'`OrganisationApercu` retourné par `ListerFormations`, `implId=None` alors que l'organisation a bien été créée sur l'implantation 6050. L'implId doit donc être réinjecté par l'appelant pour les appels suivants (comportement déjà documenté dans `docs/SPEC.md`).

## Points de développement confirmés

| Point | Verdict |
|---|---|
| Strip des champs `None` à la création (défaut D2 : élément XML vide = « effacer ») | ✅ Aucune erreur, défauts serveur propres (`False`/`0`) |
| Reconstruction de l'id depuis la réponse `CreerOrganisation` (numOrganisation serveur) | ✅ |
| `strict_errors()` sur le chemin nominal (aucune exception parasite) | ✅ |
| Format année scolaire `AAAA-AAAA` | ✅ |
| Gotcha `implId=None` dans les aperçus de `ListerFormations` | ✅ Reproduit en prod |
| Calcul serveur de `nombreSemaineFormation` | ✅ (4 semaines) |

## État final en production

Organisation **conservée** (objectif réel d'ouverture, pas un test jetable) :

- `anneeScolaire=2026-2027`, `etabId=3052`, `implId=6050`, `numAdmFormation=328`, `numOrganisation=1`
- Du 2026-09-15 au 2026-10-13, statut « Encodé école »

Prochaine étape possible : encodage Doc 1 (population) une fois l'organisation validée côté administration.

---

# Test 2 — ouvertures depuis l'horaire inspecteur « Bureautique Soir 2026-2027 » (échec attendu, règle 20030)

**Date du test :** 2026-06-11

Source : PDF « Horaire inspecteur — Bureautique Soir — 2026-2027 ». Ouvertures déduites :

| N° adm | Code UF | Libellé | Début | Fin |
|---|---|---|---|---|
| 406 | 754501U21D2 | INFORMATIQUE : TABLEUR - NIVEAU ÉLÉMENTAIRE | 03/11/2026 | 20/04/2027 |
| 405 | 754201U21D2 | INFORMATIQUE : ÉDITION ASSISTÉE PAR ORDINATEUR - NIV. ÉLÉMENTAIRE | 03/11/2026 | 20/04/2027 |

## Observations

1. **Concordance référentiel** : les deux `numAdmFormation` (405, 406) et codes UF du PDF correspondent
   exactement à `ListerFormationsOrganisables` 2026-2027. Aucune organisation préexistante.
2. **Refus métier `20030`** : `CreerOrganisation` avec début au 03/11/2026 rejeté —
   « La date de début d'organisation ne peut excéder un délai de 4 mois maximum ».
   - Levée proprement en `EtnicValidationError` sous `strict_errors()` (hiérarchie d'exceptions ✅).
   - La règle (spec `02_formation_organisation_v7.md` §codes erreur) est confirmée en prod : le délai
     s'applique aux dates de début **futures**. Point de mesure : J+3 mois 4 j accepté (test 1,
     15/09/2026), J+4 mois 22 j rejeté. Borne probable : J+4 mois calendaires (→ pour un début au
     03/11/2026, création possible à partir du **03/07/2026**).
3. **Atomicité** : échec sur la première création (406) → aucun résidu en prod, vérifié par relecture
   (405 et 406 toujours sans organisation, la 328 du test 1 intacte).

## État final

Aucune création. **À refaire à partir du 03/07/2026** : ouvrir 406 et 405, 2026-2027,
du 03/11/2026 au 20/04/2027, étab 3052 / impl 6050.

---

# Test 3 — ouverture depuis l'horaire inspecteur « Technique Soir 2026-2027 »

**Date du test :** 2026-06-11

Source : PDF « Horaire inspecteur — Technique Soir — 2026-2027 ». Deux candidates :

| N° adm | Code UF | Libellé | Début | Fin | Mention PDF |
|---|---|---|---|---|---|
| 537 | 752247U21D1 | PROGRAMMATION : NIVEAU 1 | 14/09/2026 | 21/06/2027 | Organisation1 |
| 511 | 750402U21D2 | INFORMATIQUE : MAINTENANCE SOFTWARE | 17/09/2026 | 03/06/2027 | **Organisation2** |

Décision utilisateur : ouvrir **uniquement la 537** (ambiguïté « Organisation2 » sur la 511 :
aucune organisation n'existe côté ETNIC pour cette formation, alors que le PDF numérote 2 —
le numOrganisation étant attribué par le serveur, une création aurait produit un n°1 discordant).

## Observations

1. Débuts à ~J+3 mois : règle `20030` non déclenchée, comme prédit (cohérent avec la borne
   mesurée au test 2).
2. **Création 537 OK** : `numOrganisation=1`, `nombreSemaineFormation=40` calculé serveur
   (14/09/2026 → 21/06/2027), statut « Encodé école » au 2026-06-11. Relecture conforme.
3. **Dixièmes absents du modèle SOAP** : le PDF inspecteur affiche « Premier dixième » et
   « Cinquième dixième » (12/10/2026 et 01/02/2027 pour la 537), mais l'objet `Organisation`
   ETNIC n'expose aucun champ dixième. Ces dates sont donc calculées ailleurs (UI EPROM ?
   à partir des périodes du Doc 2 ?) — point à creuser pour les specs.

## État final

- 537/1 ouverte : 2026-2027, 14/09/2026 → 21/06/2027, étab 3052 / impl 6050, « Encodé école ».
- 511 **non ouverte** : à clarifier (pourquoi « Organisation2 » sur le PDF ?) avant création.

---

# Test 4 — recherche de l'UE sur 2 années scolaires se terminant en 2026-2027 (lecture seule)

**Date du test :** 2026-06-11

Contexte : la 511 n'a pas été ouverte (UE liée à une UE sur deux années scolaires se terminant
en 26-27). Recherche par balayage de toutes les organisations 2025-2026 de l'établissement.

## Résultat

Une seule organisation 2025-2026 se termine dans l'année scolaire 2026-2027 :

- **UE 510 — INFORMATIQUE : MAINTENANCE HARDWARE (750401U21D3), organisation 3** :
  09/03/2026 → 29/01/2027, 40 semaines, statut « Approuvé », `numOrganisation2AnneesScolaires = 0`.

C'est donc la tête du couple : son prolongement 2026-2027 devra être créé avec **les mêmes dates
complètes** (09/03/2026 → 29/01/2027) et `numOrganisation2AnneesScolaires = 3`.

## Sémantique du lien 2 années scolaires (confirmée sur le couple 511 de 2024-2025/2025-2026)

- Un enregistrement d'organisation **par année scolaire**, chacun portant les **dates complètes**
  de l'UE (la date de début/fin peut donc tomber hors de l'année scolaire de l'enregistrement).
- Tête (1re année) : `numOrganisation2AnneesScolaires = 0`.
- Queue (2e année) : `numOrganisation2AnneesScolaires` = `numOrganisation` de la tête.
- Exemple réel : 511 org 4 (2024-2025) et 511 org 2 (2025-2026), toutes deux 22/05/2025 →
  30/01/2026, la seconde pointant vers 4. Code erreur associé : `20028` (numéro année précédente
  incorrect). Sémantique ajoutée à `specs/02_formation_organisation_v7.md`.

## Création de la queue 2026-2027 de la 510 (confirmée, exécutée le 11/06/2026)

`CreerOrganisation` : 2026-2027, étab 3052 / impl 6050, formation 510,
09/03/2026 → 29/01/2027, `numOrganisation2AnneesScolaires=3` → **succès**.

- `numOrganisation=1` attribué, 40 semaines (identique à la tête 2025-2026), statut
  « Encodé école » au 11/06/2026.
- Relecture conforme : dates complètes et `numOrganisation2AnneesScolaires=3` persistés.
- **Règle `20030` non déclenchée avec une date de début passée** (09/03/2026 = J−3 mois) :
  confirmation qu'elle ne borne que l'anticipation, pas le rétroactif (complète le point
  de spec 19).
- Le serveur accepte une `dateDebutOrganisation` hors de l'année scolaire de l'enregistrement
  (09/03/2026 ∈ 2025-2026 pour un enregistrement 2026-2027) dès lors que le lien 2 années
  est renseigné — cohérent avec la sémantique « dates complètes sur les deux enregistrements ».

## Reste à faire

- La 511 du PDF (« Organisation2 », 17/09/2026 → 03/06/2027) reste à ouvrir ; son
  numéro sera attribué par le serveur.
