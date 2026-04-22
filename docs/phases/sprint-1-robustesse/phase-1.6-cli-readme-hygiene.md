# Phase 1.6 — De-hardcode CLI and update README (H3 + H1)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — sections **H3** and **H1**
- `plan.md`

Last phase of Sprint 1. Pure cosmetic / hygiene fixes.

## Objective

Two things:

1. **H3**: Remove the hardcoded school identifiers (`DEFAULT_ETABID=3052`, `DEFAULT_IMPLID=6050`) from `pyetnic/cli.py`. These are private to the author's school and have no business in a published library template.

2. **H1**: Update `README.md` so that all code examples reflect the actual `pyetnic.eprom.*` and `pyetnic.seps.*` namespaces, instead of the obsolete flat `pyetnic.lire_organisation(...)` style.

## Tasks

### 1. De-hardcode `cli.py` (H3)

Open `pyetnic/cli.py` and locate the `init_config` function. Find the lines:

```python
DEFAULT_ETABID=3052
DEFAULT_IMPLID=6050
DEFAULT_SCHOOLYEAR=2023-2024
```

Replace with:

```python
# Identifiants par défaut (à remplir avec les valeurs de votre établissement)
DEFAULT_ETABID=
DEFAULT_IMPLID=
DEFAULT_SCHOOLYEAR=
```

Also update the surrounding comment block to make it clear these are placeholders:

```python
# Parametres par defaut
# Renseignez ici les identifiants de votre etablissement.
# DEFAULT_ETABID est l'identifiant numerique fourni par ETNIC.
# DEFAULT_IMPLID est l'identifiant d'implantation (optionnel pour certains services).
# DEFAULT_SCHOOLYEAR au format AAAA-AAAA (ex: 2024-2025).
DEFAULT_ETABID=
DEFAULT_IMPLID=
DEFAULT_SCHOOLYEAR=
```

The DEFAULT_SCHOOLYEAR was already a placeholder year (2023-2024 hardcoded) — better to leave it empty too and make the user fill in the current year.

### 2. Update README (H1)

Open `README.md`. Walk through every code example. The current examples use a flat namespace like:

```python
import pyetnic
result = pyetnic.lister_formations_organisables(annee_scolaire="2024-2025")
```

Update to:

```python
import pyetnic
result = pyetnic.eprom.lister_formations_organisables(annee_scolaire="2024-2025")
```

Or with explicit imports:

```python
from pyetnic.eprom import lister_formations_organisables
result = lister_formations_organisables(annee_scolaire="2024-2025")
```

Sections to update in `README.md`:

- **Formations**: both examples
- **Organisation**: all imports and calls
- **Document 1 / 2 / 3**: all imports and calls (`from pyetnic.services.models import` → `from pyetnic.eprom import`)

Add a new section near the top, right after "Configuration", explaining the namespace structure:

```markdown
## Namespaces

pyetnic exposes two public namespaces:

- **`pyetnic.eprom`** — services for EPROM (Enseignement de Promotion Sociale): formations, organisations, documents 1/2/3.
  Authentication: WSSE UsernameToken (dev or prod credentials).

- **`pyetnic.seps`** — services for SEPS (registre étudiants CFWB).
  Authentication: X509 certificate (PFX). Production only.
  Requires `pip install pyetnic[seps]`.

All public functions, models, and exceptions can be imported directly from these namespaces:

```python
from pyetnic.eprom import lire_organisation, OrganisationId, EtnicBusinessError
from pyetnic.seps import lire_etudiant, NissMutationError
```

The legacy flat namespace (`pyetnic.lire_organisation`) is no longer documented and should not be used in new code.
```

Also document the new strict error mode introduced in Sprint 1, in a new section:

```markdown
## Error handling

By default, EPROM service functions return `None` (or `FormationsListeResult(success=False)`)
on server-side errors, for backwards compatibility.

For new code, prefer **strict mode**, which raises typed exceptions:

```python
from pyetnic import strict_errors, EtnicBusinessError, EtnicDocumentNotAccessibleError
from pyetnic.eprom import lire_document_3

with strict_errors():
    try:
        doc3 = lire_document_3(org_id)
    except EtnicDocumentNotAccessibleError as e:
        print(f"Doc 3 not accessible yet: {e}")
    except EtnicBusinessError as e:
        print(f"ETNIC error {e.code}: {e.description}")
```

Strict mode can also be enabled globally:

```python
from pyetnic import Config
Config.RAISE_ON_ERROR = True
```

The flag is stored in a `ContextVar`, so it's safe in multi-threaded and asyncio contexts.

The default behavior (return `None`) will change to "raise" in version 0.2.0.
SEPS services already raise typed exceptions and are not affected by this flag.
```

### 3. Verify the README still renders

Open `README.md` in a markdown previewer (or just `cat README.md | less`) and check that:

- All code blocks have proper language tags (` ```python `, not just ` ``` `)
- No broken links
- No leftover references to the flat namespace
- Tables are properly formatted

### 4. Verify CI still green

```bash
pytest tests/regression/ tests/unit/ -v
git push
```

This phase doesn't add tests, but it shouldn't break any either.

## Constraints

- **Don't add hardcoded credentials of any kind** to `cli.py` (that would be the same defect, just different values).
- **Don't reformat the README beyond what's necessary** to update the namespaces and add the new sections. Surgical edits only.
- **Don't update example files** (`examples/extrait_profs.py` etc.) in this phase. They'll be reviewed in Sprint 3 if needed.

## Validation

- [ ] `pyetnic/cli.py`: no hardcoded etab/impl IDs, only empty placeholders
- [ ] `README.md`: all code examples use `pyetnic.eprom` / `pyetnic.seps` namespaces
- [ ] `README.md`: new "Namespaces" section added
- [ ] `README.md`: new "Error handling" section added documenting strict mode
- [ ] `README.md`: still renders correctly (no broken markdown)
- [ ] All tests still green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 1.6 as complete. Commit message:

```
docs(sprint-1): phase 1.6 — de-hardcode CLI and update README (H3 + H1)

- Remove DEFAULT_ETABID=3052 and DEFAULT_IMPLID=6050 from cli.py
  (private to author's school)
- Update README code examples to use pyetnic.eprom / pyetnic.seps namespaces
- Add "Namespaces" section explaining the public API structure
- Add "Error handling" section documenting strict mode and its
  upcoming default change in 0.2.0

Closes audit defects H1 and H3. Concludes Sprint 1.
```

After this phase, **open a new conversation in Atelier Analyse** for the Sprint 1 retrospective and Sprint 1 → Sprint 2 transition (PR, merge, branch creation). The retrospective procedure is the same as Sprint 0 (see phase 0.5).
