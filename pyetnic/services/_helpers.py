"""Private helpers for EPROM/SEPS service implementations.

These are internal utilities, NOT part of the public API.
Do not import from outside pyetnic.services.

Contents:
- to_soap_dict: None-stripping serialization for SOAP payloads (D2)
- organisation_request_id: OrganisationReqIdCT dict builder (D5)
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from .models import OrganisationId


def _strip_none_recursive(d: dict) -> dict:
    """Recursively remove keys with None values from a nested dict.

    Also processes lists of dicts (common in SOAP payloads like
    population lists, activité lists, etc.).

    Returns a new dict — the input is not modified.
    """
    result = {}
    for key, value in d.items():
        if value is None:
            continue
        if isinstance(value, dict):
            stripped = _strip_none_recursive(value)
            if stripped:
                result[key] = stripped
        elif isinstance(value, list):
            result[key] = [
                _strip_none_recursive(item) if isinstance(item, dict) else item
                for item in value
                if item is not None
            ]
        else:
            result[key] = value
    return result


def to_soap_dict(obj: Any, *, exclude_none: bool = True) -> dict:
    """Convert a dataclass instance to a dict suitable for zeep SOAP calls.

    This replaces direct use of ``dataclasses.asdict()`` in service methods.
    The key difference: when ``exclude_none=True`` (default), fields with
    ``None`` values are recursively stripped from the output. This prevents
    zeep from injecting empty XML elements for absent optional fields,
    which can cause ETNIC to reject the request or misinterpret "empty tag"
    as "erase this value".

    Args:
        obj: A dataclass instance to serialize.
        exclude_none: If True (default), recursively remove None-valued keys.
            Set to False to get the same behavior as ``dataclasses.asdict()``.

    Returns:
        A plain dict suitable for passing as ``**kwargs`` to zeep service calls.

    Examples:
        # Before (D2 defect — sends None fields as empty XML):
        request_data['populationListe'] = asdict(population_liste)

        # After:
        request_data['populationListe'] = to_soap_dict(population_liste)
    """
    if not is_dataclass(obj) or isinstance(obj, type):
        raise TypeError(
            f"to_soap_dict expects a dataclass instance, got {type(obj).__name__}"
        )

    d = asdict(obj)
    if exclude_none:
        return _strip_none_recursive(d)
    return d


def organisation_request_id(org_id: OrganisationId) -> dict:
    """Build the request ID dict for Lire/Modifier/Supprimer operations.

    These WSDL operations use the ``OrganisationReqIdCT`` contract type,
    which contains exactly 4 fields. Critically, ``implId`` is NOT included
    — it exists on the response type but must NOT be sent in requests
    (except for CreerOrganisation, which uses a different contract type
    that includes implId).

    This function replaces the ``_organisation_id_dict`` static method that
    was copy-pasted across 4 service modules (D5).

    Args:
        org_id: An OrganisationId instance. The ``implId`` field, if present,
            is deliberately excluded from the output.

    Returns:
        A dict with exactly {anneeScolaire, etabId, numAdmFormation,
        numOrganisation} — suitable for the ``id=`` kwarg in SOAP calls.
    """
    return {
        'anneeScolaire': org_id.anneeScolaire,
        'etabId': org_id.etabId,
        'numAdmFormation': org_id.numAdmFormation,
        'numOrganisation': org_id.numOrganisation,
    }
