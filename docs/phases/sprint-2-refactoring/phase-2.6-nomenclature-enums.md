# Phase 2.6 — Nomenclature Enums (H9)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **H9**
- `docs/PUBLIC_API_SURFACE.md` — `TYPES_INTERVENTION_EXTERIEURE` is stable
- `docs/BACKWARDS_COMPAT.md`
- `plan.md`
- `pyetnic/services/nomenclatures.py` (current: ~17 lines, a single constant)

Sprint 1 retrospective note:

> H9 (`nomenclatures.py` → Enums) is contained and good candidate to bundle with the Sprint 2 "structural" theme, but be careful: the current string constant is part of the stable public surface of `pyetnic.eprom` — an Enum replacement must accept legacy strings at the boundary or wait for 0.2.0.

## Objective

Introduce typed Enum classes for the most commonly used ETNIC nomenclature codes. Start with a limited, high-value set:

1. **`TypeInterventionExterieure`** — replaces the existing `TYPES_INTERVENTION_EXTERIEURE` string constant (stable API, requires backwards compat)
2. **`CodeAdmission`** — used in `SepsAdmission.codeAdmission`
3. **`CodeSanction`** — used in `SepsSanction.codeSanction`
4. **`MotifAbandon`** — used in `SepsSanction.motifAbandon`

These are introduced as **pure additions** alongside the existing string-based fields. No existing field type is changed. The Enums serve as documentation and IDE autocompletion — callers can use either the Enum value or the raw string.

## Tasks

### 1. Create `pyetnic/nomenclatures.py` (expand existing)

The current `nomenclatures.py` likely contains just `TYPES_INTERVENTION_EXTERIEURE`. Expand it:

```python
"""ETNIC nomenclature codes as typed Enums.

These Enums document the valid values for various ETNIC code fields.
They can be used for autocompletion and validation, but are NOT enforced
at the dataclass level — the raw string value is always accepted.

Usage:
    from pyetnic.nomenclatures import TypeInterventionExterieure
    
    # Using the Enum (recommended for new code):
    org.typeInterventionExterieure = TypeInterventionExterieure.CONVENTION.value
    
    # Using the raw string (still works, always will):
    org.typeInterventionExterieure = "CONV"
"""

from enum import Enum


class TypeInterventionExterieure(str, Enum):
    """Types d'intervention extérieure pour une organisation.
    
    Used in Organisation.typeInterventionExterieure.
    """
    CONVENTION = "CONV"
    PARTENARIAT = "PART"
    COLLABORATION = "COLL"
    # Add more values as discovered from ETNIC documentation


class CodeAdmission(str, Enum):
    """Codes d'admission pour une inscription SEPS.
    
    Used in SepsAdmission.codeAdmission.
    """
    REUSSITE = "REUSSITE"
    TITRE_BELGE = "TITREBEL"
    TITRE_ETRANGER = "TITREETR"
    AUTRE = "AUTRE"


class CodeSanction(str, Enum):
    """Codes de sanction de formation.
    
    Used in SepsSanction.codeSanction.
    """
    REUSSITE = "RE"
    ABANDON = "AB"
    EN_COURS = "EH"  # "En Horaire" — still following the UE


class MotifAbandon(str, Enum):
    """Motifs d'abandon.
    
    Used in SepsSanction.motifAbandon when codeSanction == "AB".
    """
    TEMPS = "TPS"
    PROFESSIONNEL = "PRO"
    FAMILIAL = "FAM"
    SANTE = "SAN"
    ATTENTES = "ATT"
    MEMOIRE = "MEM"
    FORMATION_JEUNES = "FMJ"
    NUMERIQUE = "NUM"
    AUTRE = "AUT"
    INCONNU = "INC"


class DureeInoccupation(str, Enum):
    """Durée d'inoccupation.
    
    Used in SepsSpecificite.dureeInoccupation.
    """
    ZERO = "C00"
    SIX_MOIS = "C06"
    DOUZE_MOIS = "C12"
    VINGT_QUATRE_MOIS = "C24"


class SituationMenage(str, Enum):
    """Situation de ménage.
    
    Used in SepsSpecificite.situationMenage.
    """
    ISOLE = "ISOL"
    SANS_EMPLOI = "SSEM"
    UN_EMPLOI = "A1EM"
    INCONNU = "X"


# ---------------------------------------------------------------------------
# Backwards compatibility: preserve the legacy constant
# ---------------------------------------------------------------------------

# The old TYPES_INTERVENTION_EXTERIEURE was a dict or list.
# Keep it as a derived constant so existing imports work.
# This will be deprecated in 0.2.0 and removed in 1.0.0.

TYPES_INTERVENTION_EXTERIEURE = {member.value: member.name for member in TypeInterventionExterieure}
```

**Important**: check what the current `TYPES_INTERVENTION_EXTERIEURE` actually looks like (dict? list? tuple?) and make the backwards-compatible constant match the same type and shape. Read the current `nomenclatures.py` before writing.

The `str, Enum` base class is deliberate: it makes each member directly comparable with raw strings (`TypeInterventionExterieure.CONVENTION == "CONV"` is `True`), which means existing code that compares against string values keeps working.

### 2. Update exports

In `pyetnic/eprom/__init__.py`, add the new Enums to the imports and `__all__`:

```python
from ..nomenclatures import (
    TypeInterventionExterieure,
    CodeAdmission,
    CodeSanction,
    MotifAbandon,
    DureeInoccupation,
    SituationMenage,
    TYPES_INTERVENTION_EXTERIEURE,  # legacy, already exported
)
```

Also export from `pyetnic/seps/__init__.py` the SEPS-relevant ones (CodeAdmission, CodeSanction, MotifAbandon, DureeInoccupation, SituationMenage).

### 3. Update `PUBLIC_API_SURFACE.md`

Add a new section for nomenclatures:

```markdown
### Stable — Nomenclatures

| Symbol | Notes |
|---|---|
| `TYPES_INTERVENTION_EXTERIEURE` | **Legacy** dict constant, deprecated in favor of `TypeInterventionExterieure` Enum. Will be removed in 1.0.0. |
| `TypeInterventionExterieure` | Enum — intervention types for organisations |
| `CodeAdmission` | Enum — admission codes |
| `CodeSanction` | Enum — sanction codes |
| `MotifAbandon` | Enum — abandon reasons |
| `DureeInoccupation` | Enum — inoccupation duration codes |
| `SituationMenage` | Enum — household situation codes |
```

### 4. Write tests

Create `tests/unit/test_nomenclatures.py`:

```python
"""Unit tests for nomenclature Enums."""

import pytest

from pyetnic.nomenclatures import (
    TypeInterventionExterieure,
    CodeAdmission,
    CodeSanction,
    MotifAbandon,
    DureeInoccupation,
    SituationMenage,
    TYPES_INTERVENTION_EXTERIEURE,
)


class TestTypeInterventionExterieure:

    def test_enum_values_are_strings(self):
        assert TypeInterventionExterieure.CONVENTION == "CONV"
        assert isinstance(TypeInterventionExterieure.CONVENTION, str)

    def test_string_comparison(self):
        """str(Enum) comparisons must work for backwards compat."""
        assert TypeInterventionExterieure.CONVENTION == "CONV"
        assert "CONV" == TypeInterventionExterieure.CONVENTION


class TestCodeAdmission:

    def test_all_documented_values(self):
        values = {m.value for m in CodeAdmission}
        assert "REUSSITE" in values
        assert "TITREBEL" in values
        assert "TITREETR" in values
        assert "AUTRE" in values


class TestCodeSanction:

    def test_all_documented_values(self):
        values = {m.value for m in CodeSanction}
        assert "RE" in values
        assert "AB" in values
        assert "EH" in values


class TestMotifAbandon:

    def test_all_documented_values(self):
        values = {m.value for m in MotifAbandon}
        expected = {"TPS", "PRO", "FAM", "SAN", "ATT", "MEM", "FMJ", "NUM", "AUT", "INC"}
        assert values == expected


class TestLegacyConstant:

    def test_types_intervention_exterieure_backwards_compat(self):
        """The legacy constant must still exist and be iterable."""
        assert TYPES_INTERVENTION_EXTERIEURE is not None
        assert len(TYPES_INTERVENTION_EXTERIEURE) > 0

    def test_legacy_values_match_enum(self):
        """Every Enum value must appear in the legacy constant."""
        for member in TypeInterventionExterieure:
            assert member.value in TYPES_INTERVENTION_EXTERIEURE
```

### 5. Verify

```bash
pytest tests/regression/ tests/unit/ -v
```

All green. The existing regression tests don't directly test nomenclature values (they test function calls and return shapes), so they should be unaffected.

**Check specifically**: if any regression test imports `TYPES_INTERVENTION_EXTERIEURE` and compares it to a specific shape, make sure the backwards-compatible constant matches.

## Constraints

- **Do NOT change any dataclass field type** to use Enums. The fields remain `Optional[str]`. Enums are provided as documentation and convenience, not as type enforcement. Changing field types to Enums would be a breaking change (callers pass strings today).
- **Preserve `TYPES_INTERVENTION_EXTERIEURE`** as a working backwards-compatible constant.
- **Use `str, Enum`** as the base class so that Enum members compare equal to raw strings.
- **Only include codes you are confident about.** If you're unsure whether a code is valid, leave it out — it's easy to add later, hard to remove. Check `docs/SPEC.md` and `pyetnic/services/models.py` docstrings for documented codes.

## Validation

- [ ] `pyetnic/nomenclatures.py` contains 6 Enum classes + the legacy constant
- [ ] `from pyetnic.eprom import TypeInterventionExterieure` works
- [ ] `TypeInterventionExterieure.CONVENTION == "CONV"` is True
- [ ] `TYPES_INTERVENTION_EXTERIEURE` still works as before
- [ ] `tests/unit/test_nomenclatures.py` exists with 7+ tests
- [ ] `pytest tests/regression/ tests/unit/ -v` — all green
- [ ] `PUBLIC_API_SURFACE.md` updated
- [ ] CI green

## Next

Update `plan.md`: mark Phase 2.6 as complete. Commit message:

```
feat(sprint-2): phase 2.6 — typed nomenclature Enums (H9)

- Expand pyetnic/nomenclatures.py with 6 str-based Enums:
  TypeInterventionExterieure, CodeAdmission, CodeSanction,
  MotifAbandon, DureeInoccupation, SituationMenage
- Preserve TYPES_INTERVENTION_EXTERIEURE legacy constant (deprecated)
- Enums use (str, Enum) for transparent string comparison
- Dataclass field types unchanged (still Optional[str]) — Enums are
  documentation and IDE convenience, not enforcement
- Export from pyetnic.eprom and pyetnic.seps
- Update PUBLIC_API_SURFACE.md
- Add 7 unit tests

Closes audit defect H9. Concludes Sprint 2.
```

After this phase, **open a new conversation in Atelier Analyse** for the Sprint 2 retrospective and Sprint 2 → Sprint 3 transition. Same process as Sprint 0 → Sprint 1: PR, merge, branch creation, retrospective in `plan.md`.
