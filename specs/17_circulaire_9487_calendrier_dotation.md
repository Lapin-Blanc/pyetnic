# Circulaire 9487 (16/04/2025) — Calendrier général EA 2025-2026 et gestion de la dotation de périodes

> Spécification fonctionnelle « temporalité des UE » pour les services EPROM.
> Source : `circulaires/52387_0000.pdf` (16 p., texte natif). Circulaire d'instruction, validité 25/08/2025.
> Abroge et remplace la 9244 du 25/04/2024 (circulaire annuelle ; structure stable d'année en année).
> Gestionnaire : Direction EPS — **Service de la Vérification** (mêmes contacts que circulaires DI et 8684).
> Date d'analyse : 2026-06-10 (session 8)

---

## 1. Cadre temporel de l'année académique 2025-2026

| Élément | Valeur |
|---|---|
| Rentrée académique | **lundi 25/08/2025** |
| Fin de l'année académique | **dimanche 23/08/2026** |
| Vacances d'été | à partir du samedi 04/07/2026 |
| Base légale flexibilité horaire | art. 14 du **décret du 16/04/1991** |

> **Les UE peuvent être planifiées à tout moment de l'année, en journée ou en soirée, selon un rythme
> hebdomadaire variable et une intensité modulable.** Il n'y a pas de « grille horaire » imposée — seule
> la fenêtre de l'année académique borne l'organisation.

### Jonction spec 02 (Formation Organisation v7)

- Erreurs `20010` (« date début ne peut être inférieure à xx/xx/xxxx ») et `20011` (« date fin ne peut
  être supérieure à xx/xx/xxxx ») : les bornes paramétrées côté serveur correspondent
  vraisemblablement aux **dates de l'année académique** de l'`anneeScolaire` visée (ici 25/08/2025 →
  23/08/2026). À vérifier en TQ.
- Erreur `20012` (fin ≤ début + 1 an) : cohérent avec une année académique de 52 semaines.
- `numOrganisation2AnneesScolaires` : une UE peut chevaucher deux années académiques ; son
  rattachement administratif suit la règle du **1ᵉʳ dixième** (cf. spec 16 §2).
- `nombreSemaineFormation` (calculé, 1-52, erreur `20013`) : découle des dates début/fin.

### Régime des congés (2025-2026)

| Type | Code calendrier | Régime |
|---|---|---|
| Jours fériés légaux | `CO` | cours **interdits** (13 jours listés, du 27/09/2025 au 15/08/2026) |
| Vacances d'hiver (22/12/2025 → 02/01/2026) | `VH` | suspension **obligatoire** (AE 22/03/1984, art. 3) ; étendue au samedi 03/01 si cours le samedi |
| Vacances d'automne / détente / printemps | `VA`/`VD`/`VP` | suspension **facultative** |
| Vacances d'été | `VE` | dès le 04/07/2026 |
| Jours de suspension facultatifs | `JS` | au choix de l'établissement, à identifier au calendrier |

L'établissement renvoie son **calendrier général de fonctionnement** (modèle Excel en annexe) au
Service de la Vérification (`verification.eps@cfwb.be` + vérificateur de l'établissement) **avant le
30/09/2025**. Le calendrier couvre **toutes** les activités d'enseignement, y compris l'encadrement
des stages et les épreuves intégrées.

## 2. ⭐ Règle des 100 % planifiés / 90 % dispensés

1. **Planification** : l'horaire d'une UE doit couvrir **100 % des périodes prévues au dossier
   pédagogique** (périodes d'autonomie comprises). Base légale : décret 16/04/1991, art. 136
   (approbation provisoire des UE) et 137 (approbation définitive des dossiers de référence).
   Concrètement : « il est impératif d'intégrer l'ensemble des périodes prévues dans le
   **document 8bis** de chaque UE à l'horaire ».
2. **Réalisation** : si des jours de cours sont annulés (congés, suspensions, absences non remplacées),
   **au minimum 90 % des périodes doivent être assurées** — sinon la fin de l'UE est **reportée**
   (prolongation au-delà de la semaine de fin prévue, ou cours supplémentaires).
3. **Comptabilisation des suspensions** :
   - périodes tombant un `CO` ou en `VH` → **réputées dispensées** si le seuil de 90 % reste atteint,
     sinon reprogrammation obligatoire ;
   - périodes tombant en `VA`/`VD`/`VP`/`VE` non effectivement prestées → **jamais** réputées
     dispensées, reprogrammation **systématique**.
4. **Enjeu FSE** : financement sollicité sur 100 % des périodes → toute UE planifiée à <100 % rend la
   différence inéligible (cas d'audit cité). Responsabilité du chef d'établissement / PO.
5. Remplacement des enseignants absents (maladie/infirmité) possible **dès le 1ᵉʳ jour ouvrable** si
   l'absence dure ≥ 6 jours ouvrables consécutifs (spécificité EA — continuité pédagogique).

### Jonction specs 04 (Doc 2) et 05 (Doc 3)

| Donnée service | Interprétation à la lumière de la 9487 |
|---|---|
| `nbPeriodesDoc8` (Doc 3) | périodes du **dossier pédagogique / document 8bis** = la référence 100 % |
| `nbPeriodesPrevuesDoc2` | périodes **planifiées** à l'horaire (obligation : = 100 % du Doc 8bis) |
| `nbPeriodesReellesDoc2` | périodes **effectivement dispensées** (obligation : ≥ 90 % du Doc 8bis, en comptant les CO/VH réputées dispensées) |

> Exemple normatif de la circulaire : UE de 120 périodes (12/semaine : 6 lu + 6 je), semaines 25→35 ;
> jours fériés + VP suspendus → 102 périodes dispensées < 108 (90 % de 120) → compensation ou
> prolongation obligatoire. → Un contrôle client `reelles ≥ 0,9 × doc8bis` est un garde-fou pertinent
> (la valeur exacte des « réputées dispensées » CO/VH reste côté établissement).

## 3. Gestion de la dotation de périodes

- L'année académique est découpée, **pour la gestion de la dotation**, en **16 semaines sur 2025 et
  24 semaines sur 2026** (40 semaines numérotées, indépendantes de la numérotation ISO du
  calendrier — voir annexe : semaines 1 à 40, de fin août à début juillet).
  **« Cette répartition sera maintenue pour les années suivantes. »**
- La **dotation de périodes de l'année civile 2026** est communiquée aux établissements **avant le
  31/07/2025**. (La dotation est donc gérée par **année civile**, à cheval sur deux années académiques —
  d'où le découpage 16/24.)
- Lien DI (spec 16) : les étudiants redevables non en ordre de paiement sont exclus de l'**ajustement
  de la dotation de périodes**.
- Le calcul de la dotation elle-même (formule, ajustement) n'est **pas** dans cette circulaire → voir
  8684 « Renseignements annuels » (spec 19) et les circulaires « dotation » spécifiques.

### Numérotation des semaines (annexe 2025-2026)

Semaine 1 = semaine du 25/08/2025 ; numérotation continue jusqu'à la semaine 40 (≈ 29/06/2026),
en sautant les semaines entièrement en vacances (VA, VH, VD, VP non numérotées dans l'annexe).
→ 16 semaines numérotées en 2025 (1-16), 24 en 2026 (17-40).

> ⚠️ Cette numérotation « dotation » est un **référentiel métier propre à l'EA** (≠ semaines ISO 8601).
> Si pyetnic expose un helper calendrier, prévoir la conversion date ↔ semaine de dotation à partir du
> calendrier annuel publié (l'exemple §2 — « débute en semaine 25, se termine en semaine 35 » —
> utilise cette numérotation).

## 4. Impacts sur les specs existantes

| Spec | Impact |
|---|---|
| **02 (Organisation v7)** | bornes probables des erreurs `20010`/`20011` = année académique ; sens de `nombreSemaineFormation` ; UE à cheval (`numOrganisation2AnneesScolaires`) |
| **04 (Doc 2 Périodes)** | sémantique prévu (=100 % Doc 8bis) vs réel (≥90 %) ; règles CO/VH vs VA/VD/VP |
| **05 (Doc 3)** | `nbPeriodesDoc8` = référence réglementaire de l'horaire |
| **16 (DI)** | rattachement des UE à l'année académique (fenêtre 25/08 → 23/08) pour la règle du 1ᵉʳ dixième |

## 5. Points ouverts

- Vérifier en TQ que les bornes serveur `20010`/`20011` = dates de l'année académique de la circulaire.
- Récupérer la circulaire calendrier **2026-2027** (successeur de la 9487, parution ~avril 2026) pour
  les dates à jour — le mécanisme est stable.
- Identifier la circulaire « dotation de périodes » proprement dite (communication annuelle avant le
  31/07) — probablement un courrier individuel par établissement plutôt qu'une circulaire publique.
