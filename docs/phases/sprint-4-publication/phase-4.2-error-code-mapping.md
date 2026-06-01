# Phase 4.2 — Error-code mapping enrichment (correctness)

## Context

`map_etnic_error_code_to_class` (`pyetnic/exceptions.py:116`) is an `if`-chain routing **only 2
codes** (`20102` → `EtnicDocumentNotAccessibleError`, `00009` → `EtnicNotFoundError`); everything
else falls through to the base `EtnicBusinessError`. `EtnicValidationError` **already exists**
(`exceptions.py:103`) but is **never routed**.

`specs/00_REGISTRE.md` §4 catalogues ~60 codes across the EPROM services. The 2026-06-01 probe
showed a concrete symptom: code `30004` was raised as a generic `EtnicBusinessError` with the
message `"Organisation response was empty or success=False"` — the real ETNIC description
("Le type d'intervention extérieure est incorrect") was **masked**.

Note: `signal_business_error` (`exceptions.py:170`) already extracts `code`/`description`/
`request_id` via `extract_error_info` and already auto-builds a message — but callers pass an
explicit generic `message=` that **overrides** the useful one. That is the masking cause.

## Objective

1. Route the full code catalogue to the right exception class.
2. Add the two missing classes: `EtnicAlreadyApprovedError`, `EtnicConcurrencyError`.
3. Stop masking the real ETNIC message (`str(exc)` must carry code + description).
4. (Fold-in) Investigate the Common_v2 `requestId`-as-XML-attribute latent bug.

All changes are **additive** (new classes subclass `EtnicBusinessError`), so existing
`except EtnicBusinessError` / `except EtnicError` code keeps working. **Default mode is
unchanged** (`RAISE_ON_ERROR == False` still returns `None`).

## Tasks

### 1. Add two exception classes (`exceptions.py`)

```python
class EtnicAlreadyApprovedError(EtnicBusinessError):
    """The document is already approved by the administration.

    Raised when an edit/approve operation targets a document ETNIC has
    already locked as approved (codes 1530, 1545).
    """


class EtnicConcurrencyError(EtnicBusinessError):
    """The record was modified by another user since it was read.

    Optimistic-concurrency violation (code 00011) — re-read and retry.
    """
```

### 2. Replace the `if`-chain with a table

Discrete codes (string keys, leading zeros preserved):

| Class | Codes |
|---|---|
| `EtnicNotFoundError` | `00009` |
| `EtnicDocumentNotAccessibleError` | `20102`, `30003`, `30006` |
| `EtnicAlreadyApprovedError` | `1530`, `1545` |
| `EtnicConcurrencyError` | `00011` |
| `EtnicValidationError` | `30001`, `30002`, `30004`, `30005`, `30007`, `30008`, `30009`, `20005`, `20006`, `20007`, `20010`, `20011`, `20012`, `20013`, `20016`, `20019`, `20023`, `20024`, `20025`, `20026`, `20027`, `20028`, `20029`, `20030`, `20031`, `20034`, `20037`, `20038`, `1113`, `1114`, `2106`, `2118` |
| `EtnicBusinessError` (base / default) | `00025` (security), `00999` (SQL) — left unmapped, not client-fixable |

Numeric ranges (all → `EtnicValidationError`): `4004`-`4012`, `1527`-`1528`, `1598`-`1604`,
`20015`-`20036`, `30016`-`30017`.

Note: the same code number can mean different things per service (e.g. `20016` in Organisation vs
the `20015`-`20036` range in Document 2), but they map to the **same class** (`EtnicValidationError`),
so no service disambiguation is needed.

Suggested implementation:

```python
_CODE_TO_CLASS: dict[str, Type[EtnicBusinessError]] = {
    "00009": EtnicNotFoundError,
    "20102": EtnicDocumentNotAccessibleError,
    "30003": EtnicDocumentNotAccessibleError,
    "30006": EtnicDocumentNotAccessibleError,
    "1530": EtnicAlreadyApprovedError,
    "1545": EtnicAlreadyApprovedError,
    "00011": EtnicConcurrencyError,
    # validation … (all of the above EtnicValidationError codes)
}

# (low, high, class) — inclusive, matched on int(code) when not in _CODE_TO_CLASS
_CODE_RANGES: list[tuple[int, int, Type[EtnicBusinessError]]] = [
    (4004, 4012, EtnicValidationError),
    (1527, 1528, EtnicValidationError),
    (1598, 1604, EtnicValidationError),
    (20015, 20036, EtnicValidationError),
    (30016, 30017, EtnicValidationError),
]


def map_etnic_error_code_to_class(code):
    if code is None:
        return EtnicBusinessError
    if code in _CODE_TO_CLASS:
        return _CODE_TO_CLASS[code]
    try:
        n = int(code)
    except (TypeError, ValueError):
        return EtnicBusinessError
    for low, high, cls in _CODE_RANGES:
        if low <= n <= high:
            return cls
    return EtnicBusinessError
```

### 3. Stop masking the real ETNIC message

Goal: `str(exc)` and the auto-built message surface code + ETNIC description.
- Improve the default message in `signal_business_error` to e.g. `f"ETNIC error {code}: {description}"`.
- Audit callers that pass a static generic `message=` (e.g. `organisation.py`
  `"Organisation response was empty or success=False"`). Prefer letting `signal_business_error`
  build the message from `result`, or pass a **contextual prefix** that does not hide code/description
  (the `description` attribute must always be populated when ETNIC provided one).

### 4. (Fold-in) Common_v2 `requestId` latent bug

`extract_error_info` reads `header["requestId"]`. The Organisation v7 (Common_v2) response may put
`requestId`/`transactionId` as **XML attributes**, so `request_id` could always be `None` there.
Confirm empirically (read the header shape from a real v7 error) and, if so, also read the
attribute form. If it needs more than a couple of lines, log it as backlog instead of widening 4.2.

### 5. Tests — red→green, one commit per group

For each class, add regression tests asserting the right exception type is raised in strict mode
for a representative code (use recorded fixtures or the dev server). Suggested commit slicing:
- `feat(sprint-4): phase 4.2a — add EtnicAlreadyApprovedError + EtnicConcurrencyError`
- `feat(sprint-4): phase 4.2b — table-driven map_etnic_error_code_to_class (full catalogue)`
- `fix(sprint-4): phase 4.2c — surface real ETNIC error message (unmask code/description)`
- (optional) `fix(sprint-4): phase 4.2d — read Common_v2 requestId attribute`

### 6. Empirical confirmation (optional, dev server)

Trigger a few codes live to confirm specs ↔ reality (same discipline that resolved `30004`):
`30007` (bad anneeScolaire), `20005` (bad numOrganisation), `30003` (status). Assert the mapped
class and that the description is surfaced.

## Constraints

- **Additive only** — new classes subclass `EtnicBusinessError`; no existing class moved/renamed.
- **Default mode unchanged** — `RAISE_ON_ERROR == False` still returns `None`.
- `00025`/`00999` stay on the base class (not client-side validation).
- Update `docs/PUBLIC_API_SURFACE.md` with the two new exported exception classes.

## Validation

- [ ] `EtnicAlreadyApprovedError` + `EtnicConcurrencyError` added, subclassing `EtnicBusinessError`
- [ ] `map_etnic_error_code_to_class` table-driven; full catalogue + ranges routed
- [ ] `30004` now raises `EtnicValidationError`; `str(exc)` contains `30004` + the ETNIC description
- [ ] Common_v2 `requestId` investigated (fixed or logged as backlog)
- [ ] Regression tests per group; default mode still returns `None`
- [ ] `docs/PUBLIC_API_SURFACE.md` updated; suite green
