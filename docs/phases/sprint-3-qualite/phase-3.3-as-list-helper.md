# Phase 3.3 — _as_list() helper and parser migration (Q8)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **Q8**
- `plan.md`
- `pyetnic/services/_helpers.py` — where the new helper will live
- `pyetnic/services/seps.py` — line ~190, existing `isinstance(dict)` guard (reference implementation)

zeep has a well-known behavior: when a WSDL element allows multiple occurrences (`maxOccurs="unbounded"`) but the server returns exactly one, zeep deserializes it as a single dict instead of a list containing one dict. The `rechercher_etudiants` parser already handles this correctly:

```python
if isinstance(etudiants_raw, dict):
    etudiants_raw = [etudiants_raw]
```

But this guard is missing in all EPROM document parsers, where a formation with a single organisation, a document with a single population line, or an activité with a single enseignant would silently break the `for item in ...` loop (iterating over dict keys instead of list items).

## Objective

1. Create an `_as_list()` helper in `_helpers.py`
2. Apply it to all parser sites that iterate over zeep collection results
3. Add regression tests with single-element fixtures to prove the fix

## Tasks

### 1. Add `_as_list()` to `pyetnic/services/_helpers.py`

```python
def _as_list(value: Any) -> list:
    """Normalize a zeep collection result to always be a list.

    zeep deserializes unbounded XML elements as a list when there are
    multiple results, but as a single dict when there's exactly one.
    This helper normalizes both cases to a list.

    Args:
        value: The raw value from zeep's serialized output. Can be:
            - None → returns []
            - a dict (single element) → returns [dict]
            - a list → returns as-is

    Returns:
        A list, always.

    Examples:
        # Multiple results → already a list, returned as-is
        _as_list([{'name': 'A'}, {'name': 'B'}])  # → [{'name': 'A'}, {'name': 'B'}]

        # Single result → zeep returned a dict, wrapped in list
        _as_list({'name': 'A'})  # → [{'name': 'A'}]

        # No results → empty list
        _as_list(None)  # → []
    """
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    return list(value)
```

### 2. Identify all call sites

The following sites iterate over zeep collection results and need the `_as_list` guard:

**`pyetnic/services/document1.py`**:
```python
# line ~72
for p in doc_data['populationListe'].get('population', [])
# → for p in _as_list(doc_data['populationListe'].get('population'))
```

**`pyetnic/services/document2.py`**:
```python
# line ~71 — activités d'enseignement
for line in ae.get('activiteEnseignementListe', {}).get('activiteEnseignement', [])
# → for line in _as_list(ae.get('activiteEnseignementListe', {}).get('activiteEnseignement'))

# line ~101 — périodes d'intervention
for p in ie.get('periodeListe', {}).get('periode', [])
# → for p in _as_list(ie.get('periodeListe', {}).get('periode'))

# line ~105 — interventions extérieures
for ie in ie_list.get('interventionExterieure', [])
# → for ie in _as_list(ie_list.get('interventionExterieure'))
```

**`pyetnic/services/document3.py`**:
```python
# line ~73 — enseignants d'une activité
for e in a['enseignantListe'].get('enseignant', [])
# → for e in _as_list(a['enseignantListe'].get('enseignant'))

# line ~77 — activités
for a in doc_data['activiteListe'].get('activite', [])
# → for a in _as_list(doc_data['activiteListe'].get('activite'))
```

**`pyetnic/services/formations_liste.py`**:
```python
# line ~95 — formations
for f in result['body']['response'].get('formation', [])
# → for f in _as_list(result['body']['response'].get('formation'))

# line ~98 — organisations d'une formation
for org_data in f.get('organisation', [])
# → for org_data in _as_list(f.get('organisation'))
```

**`pyetnic/services/seps.py`** (already has a guard at line ~190):
```python
if isinstance(etudiants_raw, dict):
    etudiants_raw = [etudiants_raw]
```
Replace with the helper:
```python
etudiants_raw = _as_list(etudiants_raw)
```

**`pyetnic/services/inscriptions.py`** (already has a guard at line ~181):
Same pattern — replace inline isinstance check with `_as_list()`.

### 3. Apply the migration

For each file:

1. Add the import:
   ```python
   from ._helpers import _as_list
   ```

2. Replace the iteration pattern. The key change: remove the `, []` default from `.get()` calls — `_as_list` handles `None` already.

   ```python
   # Before:
   for p in doc_data['populationListe'].get('population', [])
   
   # After:
   for p in _as_list(doc_data['populationListe'].get('population'))
   ```

   Note: `.get('population')` without a default returns `None`, and `_as_list(None)` returns `[]`. This is equivalent to the old `, []` default but also handles the single-dict case.

### 4. Add unit tests for `_as_list`

Add to `tests/unit/test_helpers.py`:

```python
from pyetnic.services._helpers import _as_list


class TestAsList:

    def test_none_returns_empty_list(self):
        assert _as_list(None) == []

    def test_dict_returns_single_element_list(self):
        d = {'name': 'A', 'value': 1}
        result = _as_list(d)
        assert result == [d]
        assert isinstance(result, list)

    def test_list_returned_as_is(self):
        items = [{'name': 'A'}, {'name': 'B'}]
        assert _as_list(items) == items

    def test_empty_list_returned_as_is(self):
        assert _as_list([]) == []

    def test_single_element_list_stays_list(self):
        """A list with one element must NOT be unwrapped."""
        items = [{'name': 'A'}]
        assert _as_list(items) == [{'name': 'A'}]
```

### 5. Add regression tests with single-element fixtures

This is the critical addition: test the actual parser functions with SOAP responses that contain exactly **one** element where multiple are possible. These tests would have failed before the `_as_list` migration.

Add to `tests/regression/test_single_element_parsing.py`:

```python
"""Regression tests for single-element SOAP responses (Q8 fix).

zeep returns a single dict instead of a list when there's exactly one
XML element with maxOccurs="unbounded". These tests verify that the
parsers handle this correctly after the _as_list() migration.
"""

import pytest
from datetime import date
from pyetnic.eprom import (
    lire_document_1, lire_document_3,
    lister_formations,
    OrganisationId, FormationDocument1, FormationDocument3,
)


def test_document1_single_population_line(mock_soap_call):
    """A document with exactly one population line should parse correctly."""
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                'document1': {
                    'populationListe': {
                        # zeep returns a DICT, not a list, for a single element
                        'population': {
                            'coAnnEtude': 1,
                            'nbEleveA': 12,
                            'nbEleveEhr': 0, 'nbEleveFse': 0, 'nbElevePi': 0,
                            'nbEleveB': 0, 'nbEleveTot2a5': 12, 'nbEleveDem': 0,
                            'nbEleveMin': 0, 'nbEleveExm': 0, 'nbElevePl': 0,
                            'nbEleveTot6et8': 0, 'nbEleveTotFse': 0, 'nbEleveTotPi': 0,
                            'nbEleveTotHom': 5, 'nbEleveTotFem': 7,
                            'swAppPopD1': False, 'swAppD1': False,
                        }
                    }
                }
            }
        }
    }
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    result = lire_document_1(org_id)
    assert result is not None
    assert len(result.populationListe.population) == 1
    assert result.populationListe.population[0].coAnnEtude == 1


def test_document3_single_activite_single_enseignant(mock_soap_call):
    """A document with one activité containing one enseignant."""
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                'document3': {
                    'activiteListe': {
                        # Single activité as dict (not list)
                        'activite': {
                            'coNumBranche': 1,
                            'coCategorie': 'A',
                            'teNomBranche': 'Mathématiques',
                            'noAnneeEtude': '1',
                            'nbPeriodesDoc8': 40.0,
                            'nbPeriodesPrevuesDoc2': 40.0,
                            'nbPeriodesReellesDoc2': 38.0,
                            'enseignantListe': {
                                # Single enseignant as dict
                                'enseignant': {
                                    'coNumAttribution': 1,
                                    'noMatEns': '12345678901',
                                    'teNomEns': 'DUPONT',
                                    'tePrenomEns': 'Jean',
                                    'nbPeriodesAttribuees': 40.0,
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    result = lire_document_3(org_id)
    assert result is not None
    assert len(result.activiteListe.activite) == 1
    activite = result.activiteListe.activite[0]
    assert activite.coNumBranche == 1
    assert len(activite.enseignantListe.enseignant) == 1
    assert activite.enseignantListe.enseignant[0].teNomEns == 'DUPONT'


def test_lister_formations_single_formation_single_org(mock_soap_call):
    """A response with one formation containing one organisation."""
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                # Single formation as dict
                'formation': {
                    'numAdmFormation': 455,
                    'libelleFormation': 'Informatique',
                    'codeFormation': 'INF',
                    # Single organisation as dict
                    'organisation': {
                        'numOrganisation': 1,
                        'implId': 6050,
                        'dateDebutOrganisation': date(2024, 9, 2),
                        'dateFinOrganisation': date(2025, 6, 27),
                        'statutDocumentOrganisation': None,
                        'statutDocumentPopulationPeriodes': None,
                        'statutDocumentDroitsInscription': None,
                        'statutDocumentAttributions': None,
                    }
                }
            }
        }
    }
    result = lister_formations(annee_scolaire="2024-2025")
    assert result.success
    assert len(result.formations) == 1
    assert result.formations[0].numAdmFormation == 455
    assert len(result.formations[0].organisations) == 1
```

### 6. Verify

```bash
pytest tests/unit/test_helpers.py -v          # new _as_list tests
pytest tests/regression/test_single_element_parsing.py -v  # new Q8 regression tests
pytest tests/regression/ tests/unit/ -v       # full suite
```

All green. The single-element tests would have FAILED before the migration (they exercise the exact zeep dict-instead-of-list bug).

## Constraints

- **Do NOT change the public API** — all changes are in internal parsers.
- **Preserve existing multi-element behavior** — `_as_list([a, b])` returns `[a, b]` unchanged.
- **Keep the existing `isinstance` guards** in `seps.py` and `inscriptions.py` until they're replaced by `_as_list` — don't delete the guard without replacing it in the same commit.
- **Add `_as_list` to `_helpers.py`**, not a new file.

## Validation

- [ ] `_as_list` exists in `pyetnic/services/_helpers.py`
- [ ] `grep -rn "isinstance.*dict" pyetnic/services/seps.py pyetnic/services/inscriptions.py` shows `_as_list` usage instead of inline checks
- [ ] `grep -rn ", \[\])" pyetnic/services/document*.py pyetnic/services/formations_liste.py` returns zero (no more `, []` defaults on collection getters — `_as_list` handles None)
- [ ] `tests/unit/test_helpers.py` has 5 new `TestAsList` tests
- [ ] `tests/regression/test_single_element_parsing.py` has 3+ tests with single-element fixtures
- [ ] All existing tests still green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 3.3 as complete. Commit message:

```
fix(sprint-3): phase 3.3 — normalize zeep list|dict with _as_list() (Q8)

- Add _as_list() helper to _helpers.py: normalizes None → [],
  dict → [dict], list → list (handles zeep single-element quirk)
- Migrate 10 parser sites across document1, document2, document3,
  formations_liste, seps, inscriptions
- Replace inline isinstance guards in seps.py and inscriptions.py
- Add 5 unit tests for _as_list() and 3 regression tests with
  single-element SOAP fixtures

Closes audit defect Q8.
```

Next phase: **Phase 3.4 — soap_client cleanup (Q5 + Q6 + Q3)**.
