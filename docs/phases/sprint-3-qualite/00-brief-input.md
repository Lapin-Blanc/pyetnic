# Brief Sprint 3 — pyetnic

> Dossier à destination d'une conversation d'analyse Claude web pour construire le plan Sprint 3.
> Généré le 2026-04-23 depuis l'état courant du repo (branche `main`, tag implicite post-merge PR #4).

---

## 1. Contexte global

**pyetnic** — client Python pour les SOAP ETNIC (services EPROM + SEPS). Refactoring en 4 sprints vers **0.1.0 beta**.

- Sprint 0 (prep), 1 (robustesse), 2 (structure) : **terminés et mergés dans `main`**.
- Sprint 3 (qualité/hygiène) : **à construire**.
- Sprint 4 (publication) : CHANGELOG / bump / PyPI.

**Décisions structurantes déjà prises** (toujours valables pour S3) :
- Rester en dataclasses (pas de Pydantic avant 0.1.0).
- Pas de default-mode switch vers `raise` avant 0.2.0 (strict mode reste opt-in).
- Backwards compat : API stable vs API construction — voir `docs/PUBLIC_API_SURFACE.md` et `docs/BACKWARDS_COMPAT.md`.
- Git workflow : 1 branche par sprint, 1 commit par phase, PR en fin de sprint, Conventional Commits.
- Conversations segmentées (2 phases max par conversation Claude Code).

---

## 2. Rétrospective Sprint 2 (métriques probantes)

**Périmètre** : D2 (asdict → to_soap_dict), D5 (dédup `_organisation_id_dict`), Q4 (Config int casting), H9 (nomenclature Enums).

**Diff** : `ddcbeef..f5640d9` (post-sprint-1 → post-phase-2.6, avant merge `1f59240`).

```
34 files changed, 2518 insertions(+), 252 deletions(-)
```

**Commits** (6 phases + 1 chore) :
- `0d59f62` chore(sprint-2): install phase prompts and update plan
- `9ee420e` feat(sprint-2): phase 2.1 — create _helpers module (D2 + D5 foundations)
- `6d5f9ce` refactor(sprint-2): phase 2.2 — deduplicate _organisation_id_dict (D5)
- `b628a99` fix(sprint-2): phase 2.3 — replace asdict() with to_soap_dict() in EPROM docs (D2)
- `887c6ea` refactor(sprint-2): phase 2.4 — replace asdict() in SEPS write services (D2)
- `213656f` fix(sprint-2): phase 2.5 — Config.ETAB_ID/IMPL_ID return int (Q4)
- `f5640d9` feat(sprint-2): phase 2.6 — typed nomenclature Enums (H9)

**Tests ajoutés** (hors phase prompts) :
- `tests/unit/test_helpers.py` (+169) — D2 + D5 unit
- `tests/unit/test_nomenclatures.py` (+87) — H9
- `tests/unit/test_seps_write_unit.py` (+181) — D2 SEPS
- `tests/regression/test_config.py` (+85) — Q4
- `tests/regression/test_soap_payload_shape.py` (+163) — D2 non-régression

**Points notables de S2** :
- `_helpers.py` (module privé, 107 lignes) centralise `to_soap_dict()` (récursif, `exclude_none=True`) et `organisation_request_id()`. Remplace 4 copies de `_organisation_id_dict` + `dataclasses.asdict()` dans 5 services.
- H9 : `nomenclatures.py` **promu au top-level** (`pyetnic/nomenclatures.py`, 132 lignes) — 6 classes `(str, Enum)` ; legacy `TYPES_INTERVENTION_EXTERIEURE` préservé. Constante exportée depuis `pyetnic.eprom` et `pyetnic.seps`. **Ajout au `PUBLIC_API_SURFACE.md`.**
- Q4 : `_SIMPLE_ENV_MAP` dans `config.py` étendu avec caster optionnel — `ETAB_ID` et `IMPL_ID` rendus `int | None` ; **`int()` redondant retiré** des tests.
- Aucun test de régression S0/S1 modifié sauf signatures (`Config.ETAB_ID` déjà `int`).

**À remplir (je te laisse finaliser)** — la section "Sprint 2 retrospective" de `plan.md:203` est encore en template `TBD`. À compléter avec :
- What went well
- What took longer
- Surprises / discoveries
- Total local suite (lancer `pytest tests/regression tests/unit -q` — sur mon env `pytest` n'est pas dans le PATH, donc à faire côté toi)
- CI runtime (dernière run GH Actions)
- Notes pour Sprint 3

---

## 3. État courant par défaut Sprint 3

Défauts ciblés par le plan : **H2, H5, H8, Q5, Q6, Q7, Q8, H11**.

### H2 — `CLAUDE.md` à 413 lignes (hygiène doc)

**Statut** : **partiellement résolu** pendant S0 mais pas fini.
- `CLAUDE.md` racine : **66 lignes** (OK, pointe vers `docs/`).
- `.claude/CLAUDE.md` : **413 lignes** — contient toujours tout le détail workflow ETNIC, implId, Doc1/2/3, conventions, XSD checklist, etc.
- `docs/SPEC.md` : 225 lignes — existe mais ne contient probablement pas tout ce qui est dans `.claude/CLAUDE.md`.

**Question** : l'intention initiale (audit) était de splitter → SPEC.md pour les règles métier, CLAUDE.md pour les instructions Claude Code. Le split a été partiellement fait. **Reste à** : dégraisser `.claude/CLAUDE.md` en migrant les sections restantes vers `docs/SPEC.md` ou `docs/ARCHITECTURE.md` (référencé dans le CLAUDE.md racine mais **n'existe pas encore**, cf `ls docs/` → `AUDIT.md BACKWARDS_COMPAT.md phases PUBLIC_API_SURFACE.md SPEC.md`).

### H5 — `requirements.txt` en doublon + commentaires morts

**Statut** : **non résolu**. Contenu actuel :

```
# Dépendances principales
urllib3
zeep
python-dotenv
requests
openpyxl
cryptography
xmlsec            ← en main deps

# #cgi-tools  # Support pour remplacer le module cgi déprécié

# # Dépendances de développement
# pytest==7.4.0
# pytest-cov==4.1.0
# flake8==6.1.0
# black
# isort==5.12.0
# mypy==1.5.1
...
```

**Divergences avec `pyproject.toml`** :
- `pyproject.toml` deps principales : `zeep`, `python-dotenv`, `requests`, `openpyxl`, `cryptography` — **pas `urllib3`, pas `xmlsec`**.
- `xmlsec` est correctement en `optional-dependencies.seps` dans pyproject → doit disparaître du requirements.txt main.
- `openpyxl` est dans pyproject main deps mais **non utilisé dans le code** (cf CLAUDE.md — export Excel non implémenté). À remettre en question.

**Action probable** : supprimer `requirements.txt` (pyproject suffit), ou le réduire à `-e .[seps]` si on tient à garder un fichier.

### H8 — `Codes_Pays.xls` embedded sans usage

**Statut** : **non résolu**. Le fichier `pyetnic/resources/Codes_Pays.xls` est toujours là. Aucun code ne l'utilise (grep vide). Bloat wheel.

**Action** : suppression pure et simple + vérifier que rien ne casse.

### Q5 — `_ssl_warnings_suppressed` global mutable

**Statut** : **non résolu**. Dans `pyetnic/soap_client.py` :

```python
# ligne 42
_ssl_warnings_suppressed = False

# ligne 162-166 (dans méthode)
global _ssl_warnings_suppressed
if not _ssl_warnings_suppressed and not Config.get_verify_ssl():
    # suppression urllib3 warnings ici
    _ssl_warnings_suppressed = True
```

**Problème** : non testable (pas de reset), non thread-safe.

**Piste** : encapsuler dans une classe ou un `ContextVar` (cohérent avec `RAISE_ON_ERROR` de S1), ou utiliser `threading.Lock` + flag de classe `SoapClientManager`.

### Q6 — `request_id` non loggé au succès

**Statut** : **non résolu**. Dans `soap_client.py` :

```python
# ligne 204-214
request_id = generate_request_id()
...
result = method(_soapheaders={"requestId": request_id}, **kwargs)
...
# ERREUR :
logger.error(f"{error_msg} (request_id: {request_id})")  # loggé
# SUCCÈS : ← rien loggé
```

**Action** : un `logger.info("request_id=%s service=%s method=%s ok", ...)` sur succès, ou au minimum en debug.

**Lien Q7** : profiter du fix pour basculer le `.error(f"..."` → `.error("...", ...)`.

### Q7 — f-strings dans `logger.debug/info/error`

**Statut** : **non résolu**. 20 occurrences répertoriées :

```
soap_client.py:168, 213
services/formations_liste.py:93, 96, 99
services/organisation.py:43, 86, 116, 143, 168
services/document1.py:44, 87, 103, 120
services/document2.py:47, 124, 142
services/document3.py:44, 92, 108
```

**Problème** : coût d'évaluation même quand le niveau log est plus haut. Pire sur `pformat(large_dict)`.

**Action** : substitution mécanique (cf exemple audit :
```python
logger.debug(f"Organisation : {pformat(org_data)}")
→ logger.debug("Organisation : %s", pformat(org_data))
```
**Attention** : `pformat()` reste évalué immédiatement car c'est un argument. Correction propre → `logger.isEnabledFor(logging.DEBUG)` guard OU `LazyStr` wrapper. À arbitrer : fix naïf (style fix) vs fix perf (guard). Claude web doit trancher.

### Q8 — zeep list|dict parsing incohérent

**Statut** : **partiellement résolu**. Garde `isinstance(dict)` présente dans :
- `services/inscriptions.py:181`
- `services/seps.py:190`

**MANQUE** dans les endroits listés par l'audit (zeep peut retourner un dict si 1 seul élément) :

```
document1.py:72  for p in doc_data['populationListe'].get('population', [])
document2.py:71  for line in ae.get('activiteEnseignementListe', {}).get('activiteEnseignement', [])
document2.py:101 for p in ie.get('periodeListe', {}).get('periode', [])
document2.py:105 for ie in ie_list.get('interventionExterieure', [])
document3.py:73  for e in a['enseignantListe'].get('enseignant', [])
document3.py:77  for a in doc_data['activiteListe'].get('activite', [])
formations_liste.py:95, 98 (formation, organisation)
```

**Action** : helper `_as_list(value)` dans `_helpers.py` + substitution à tous ces call sites + test de régression avec fixture mono-élément.

### H11 — pas de `py.typed` marker

**Statut** : **non résolu**. Le fichier `pyetnic/py.typed` n'existe pas. `pyproject.toml:45` contient `[tool.setuptools.package-data]` avec WSDL/XSD mais pas `py.typed`.

**Action** : créer fichier vide `pyetnic/py.typed` + ajouter `"py.typed"` à `package-data` + vérifier avec `python -m build` que le wheel contient bien le marker.

---

## 4. Autres défauts non couverts par S3 (mention)

Le plan Sprint 3 cible 8 défauts. Pour mémoire, **non programmés** :

- **D4** — couplage zeep `serialize_object(result, dict)` : reporté (decision Sprint 0).
- **D6** — split `OrganisationId` → `OrganisationKey` / `OrganisationResId` : reporté à 1.0.0 (breaking).
- **Q3** — `_EtnicBinarySignature.verify()` silent no-op : à documenter, pas traité.
- **Q9** — CI : **déjà fait en S0** (3.10→3.13 matrix).
- **Q10** — `log_config.py` : à vérifier s'il existe encore (grep à faire).
- **H4** — one-off scripts : **déjà fait en S0** (déplacés vers `examples/`).
- **H6** — classifier "Alpha" → "Beta" : sera traité au bump 0.1.0 (S4).
- **H7** — lazy singleton via PEP 562 : non programmé (impact faible).
- **H10** — versionning XSD / `pyetnic doctor` command : non programmé (nice-to-have).

**À arbitrer** avec Claude web : faut-il inclure **Q3** ou **H7** dans S3 s'il reste de la marge ?

---

## 5. Contraintes et patterns établis

Tout plan Sprint 3 doit respecter :

1. **Une phase = un défaut (ou un sous-défaut) = un commit Conventional**.
2. **Test de régression d'abord** (red → green) pour les changements comportementaux.
3. **Tests mock en `tests/regression/` ou `tests/unit/`**, intégration en `tests/integration/` (skipped sans `.env`).
4. **Pas de modification silencieuse de l'API publique** (contrat stable `docs/PUBLIC_API_SURFACE.md`).
5. **CI doit passer à chaque push** (3.10→3.13 matrix, `.github/workflows/tests.yml`).
6. **Segmentation en conversations Claude Code de 2 phases max** (pour rester sous limite contexte) — expliciter dans le plan.
7. **Messages commits en anglais**, discussions/plans en français (cf CLAUDE.md global).

---

## 6. Questions ouvertes pour la conversation Claude web

1. **Ordre des phases** : faut-il ranger H (hygiène simple) avant Q (qualité code) ou entremêler ? Argument "H d'abord" : gains triviaux, cleanup avant refactor. Argument "Q d'abord" : bénéfice utilisateur plus fort.
2. **H2 scope** : faut-il créer `docs/ARCHITECTURE.md` (référencé dans `CLAUDE.md` racine mais manquant) pendant S3, ou le reporter ?
3. **Q7 stratégie** : substitution mécanique simple vs introduction d'un helper `LazyPformat` ? Trade-off simplicité vs perf.
4. **Q8 helper** : `_as_list()` dans `_helpers.py` (privé) ou dans un nouveau `_parsing.py` dédié aux normalisations zeep ?
5. **H5** : supprimer `requirements.txt` complètement ou le garder comme pointeur `-e .[seps]` pour utilisateurs Python non familiers avec pyproject ?
6. **H8** : avant de supprimer `Codes_Pays.xls`, vérifier qu'il n'est pas référencé dans des scripts utilisateurs externes (intégrations Django de Fabien) ? Si risque → `DeprecationWarning` pendant 1 version.
7. **Q3/H7** dans S3 ou pas ? (voir section 4).
8. **Cadence** : S1 = 6 phases, S2 = 6 phases. S3 peut monter à 8-9 si on découpe Q8/Q7 finement. Est-ce soutenable sur 1 branche ou splitter en 2 sous-sprints ?
9. **Metrics targets** : combien de tests ajouter raisonnablement ? S2 en a ajouté ~45.

---

## 7. Fichiers à consulter (pour Claude web si accès fourni)

Si tu partages le repo à Claude web :
- `plan.md` — plan global (source de vérité)
- `docs/AUDIT.md` — audit initial (lecture obligatoire pour défaut IDs)
- `docs/PUBLIC_API_SURFACE.md` — contrat stabilité
- `docs/BACKWARDS_COMPAT.md` — règles compat
- `docs/phases/sprint-2-refactoring/` — prompts des phases S2 (modèles pour S3)
- `docs/phases/sprint-3-qualite/` — **vide** (`.gitkeep` seul) — c'est ce qu'il faut produire
- `CLAUDE.md` + `.claude/CLAUDE.md` — conventions projet
- `pyetnic/soap_client.py` — Q5, Q6 ciblés ici
- `pyetnic/services/_helpers.py` — endroit naturel pour `_as_list` (Q8)
- `pyproject.toml` — H5, H11

---

## 8. Livrable attendu de Claude web

Un plan Sprint 3 prêt à coller dans `plan.md`, suivant la structure des sections Sprint 1 et Sprint 2 :

- **Goal** (1 phrase)
- **Branch** : `refactor/sprint-3`
- **Audit defects addressed** : liste
- **Phases** : checklist `[ ]` ordonnée, 1 ligne + bullets contraintes + conversation tag
- **Conversation segmentation** : A / B / C… avec phases assignées
- **Design decisions** (section "Notes et décisions" à compléter)
- **Template retrospective** (à remplir en fin de sprint)

Plus : un prompt par phase à placer dans `docs/phases/sprint-3-qualite/phase-3.X-<name>.md`, suivant exactement le format des prompts S2 existants (cf `docs/phases/sprint-2-refactoring/phase-2.1-create-helpers.md` comme référence de style).
