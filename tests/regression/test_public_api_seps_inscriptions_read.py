"""Regression tests for ``pyetnic.seps.rechercher_inscriptions``, stable since #24.

Mock-based: the SOAP layer is patched (see ``conftest.mock_soap_call``).
Identifiers are fictitious.
"""

from __future__ import annotations

import pytest

import pyetnic.seps
from pyetnic.seps import Inscription, SepsAudit, SepsUE, SepsValidationError, rechercher_inscriptions

INSCRIPTION = {
    "cfNum": "1234567-89",
    "anneeScolaire": 2026,
    "idEtab": 1234,
    "idImplantation": 5678,
    "dateInscription": "2026-09-25",
    "statut": "DE",
    "ue": {"noAdministratif": 100, "noOrganisation": 2, "label": "UE", "code": "202600000000123400100000002"},
    "specificite": {"regulier1": "O", "regulier5": "O", "admission": {"codeAdmission": "AUTRE", "valorisationAcquis": "C10"}},
    "audit": {"dateCreation": "2026-09-30T15:57:43", "utilisateurCreation": "U", "dateModification": "2026-09-30T15:57:43", "utilisateurModification": "U"},
}


def answer(*, inscriptions=None, warning=(), error=(), success=True):
    body = {"success": success, "messages": {"error": list(error), "warning": list(warning), "info": []}}
    if inscriptions is not None:
        body["response"] = {"inscription": inscriptions}
    return {"body": body}


def test_stable_symbols_importable():
    for name in ("rechercher_inscriptions", "Inscription", "SepsUE", "SepsSpecificite", "SepsAdmission", "SepsSanction"):
        assert hasattr(pyetnic.seps, name)


def test_returns_parsed_inscriptions(mock_soap_call):
    mock_soap_call.return_value = answer(inscriptions=[INSCRIPTION])
    rows = rechercher_inscriptions(annee_scolaire=2026, etab_id=1234, no_administratif=100, no_organisation=2)
    assert len(rows) == 1
    assert isinstance(rows[0], Inscription)
    assert isinstance(rows[0].ue, SepsUE)
    assert rows[0].audit == SepsAudit("2026-09-30T15:57:43", "U", "2026-09-30T15:57:43", "U")


def test_single_inscription_dict(mock_soap_call):
    mock_soap_call.return_value = answer(inscriptions=INSCRIPTION)
    assert [r.cfNum for r in rechercher_inscriptions(cf_num="1234567-89")] == ["1234567-89"]


def test_request_keywords(mock_soap_call):
    mock_soap_call.return_value = answer(inscriptions=[])
    rechercher_inscriptions(annee_scolaire=2026, etab_id=1234, date_requete="2026-09-30", cf_num="1234567-89", no_administratif=100, no_organisation=2)
    _, kwargs = mock_soap_call.call_args
    assert kwargs == {"anneeScolaire": 2026, "etabId": 1234, "dateRequete": "2026-09-30", "cfNum": "1234567-89", "noAdministratif": 100, "noOrganisation": 2}


@pytest.mark.parametrize("code", ["30102", "30103"])
def test_nothing_found_is_empty(mock_soap_call, code):
    mock_soap_call.return_value = answer(success=False, warning=[{"code": code, "description": "No inscription found"}])
    assert rechercher_inscriptions(annee_scolaire=2026, etab_id=1234) == []


def test_bad_criteria_raise(mock_soap_call):
    mock_soap_call.return_value = answer(success=False, error=[{"code": "30036", "description": "Invalid input parameters combination"}])
    with pytest.raises(SepsValidationError):
        rechercher_inscriptions(etab_id=1234)
