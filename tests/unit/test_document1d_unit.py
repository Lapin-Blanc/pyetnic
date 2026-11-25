"""Document 1D (droits d'inscription): mock-only unit tests.

The responses mirror what TQ answered on 2026-11-24 (see spec 06).
"""

from __future__ import annotations

from dataclasses import replace

import pytest
from zeep import Client

from pyetnic.config import Config
from pyetnic.error_mode import strict_errors
from pyetnic.exceptions import (
    EtnicAlreadyApprovedError,
    EtnicConcurrencyError,
    EtnicDocumentNotAccessibleError,
    EtnicValidationError,
)
from pyetnic.services.document1d import Document1DService
from pyetnic.services.models import (
    Doc1DDroitInscriptionLineAppr,
    Doc1DDroitInscriptionLineSave,
    Doc1DDroitInscriptionListAppr,
    Doc1DDroitInscriptionListSave,
    FormationDocument1D,
    OrganisationId,
)
from pyetnic.soap_client import get_wsdl_path

ORG_ID = OrganisationId(anneeScolaire="2025-2026", etabId=1234, numAdmFormation=312, numOrganisation=1)


def _line(co="1", nb=3, mt=0.0, pop=False, admin=False) -> dict:
    return {
        "coAnnEtude": co,
        "nbEleves5ieme": nb,
        "mtDroitsInscription": mt,
        "mtDroitsInscriptionOccupationnel": 0.0,
        "swAppPopD1D": pop,
        "swAppD1D": admin,
        "tsMaj": "2026-11-24 23:13:02.452733",
        "teUserMaj": "USER",
    }


def _response(lines: list[dict] | dict) -> dict:
    return {
        "header": {"requestId": "r-1"},
        "body": {
            "success": True,
            "messages": None,
            "response": {
                "document1D": {
                    "id": {"anneeScolaire": "2025-2026", "etabId": 1234, "implId": 5678,
                           "numAdmFormation": 312, "numOrganisation": 1},
                    "droitInscriptionListe": {"droitInscription": lines},
                }
            },
        },
    }


def _refusal(code: str, description: str) -> dict:
    return {
        "header": {"requestId": "r-2"},
        "body": {
            "success": False,
            "messages": {"error": [{"code": code, "description": description, "zone": None}],
                         "warning": [], "info": []},
            "response": None,
        },
    }


@pytest.fixture
def service(monkeypatch):
    svc = Document1DService()
    calls: list[tuple[str, dict]] = []

    def answer(response):
        def fake(method, **kwargs):
            calls.append((method, kwargs))
            return response
        monkeypatch.setattr(svc.client_manager, "call_service", fake)

    svc.answer = answer
    svc.calls = calls
    return svc


def test_contract_loads_offline_with_the_three_operations():
    config = Config.SERVICES["DOCUMENT1D"]
    client = Client(get_wsdl_path("pyetnic.resources", config.wsdl_path))
    operations = set(client.wsdl.bindings[config.binding_name]._operations)
    assert operations == {"LireDocument1D", "ModifierDocument1D", "ApprouverDocument1D"}
    assert config.endpoint.endswith("/eprom/formation/document1D/v1")


def test_lire_parses_every_field(service):
    service.answer(_response([_line(pop=True, mt=12.5)]))

    doc = service.lire_document_1d(ORG_ID)

    assert isinstance(doc, FormationDocument1D)
    assert doc.id == replace(ORG_ID, implId=5678)  # the answer's id, implId included (#51)
    [line] = doc.droitInscriptionListe.droitInscription
    assert (line.coAnnEtude, line.nbEleves5ieme, line.mtDroitsInscription) == ("1", 3, 12.5)
    assert (line.swAppPopD1D, line.swAppD1D) == (True, False)
    assert line.mtDroitsInscriptionOccupationnel == 0.0
    assert line.tsMaj and line.teUserMaj
    method, kwargs = service.calls[0]
    assert method == "LireDocument1D"
    assert "implId" not in kwargs["id"]


def test_lire_single_line_returned_as_dict(service):
    """zeep returns a lone repeated element as a dict, not a one-element list."""
    service.answer(_response(_line()))
    assert len(service.lire_document_1d(ORG_ID).droitInscriptionListe.droitInscription) == 1


def test_modifier_sends_only_the_fields_given(service):
    service.answer(_response([_line()]))

    service.modifier_document_1d(ORG_ID, Doc1DDroitInscriptionListSave([
        Doc1DDroitInscriptionLineSave("1", nbEleves5ieme=3),
        Doc1DDroitInscriptionLineSave("2", mtDroitsInscription=12.5),
    ]))

    method, kwargs = service.calls[0]
    assert method == "ModifierDocument1D"
    assert kwargs["droitInscriptionListe"] == {"droitInscription": [
        {"coAnnEtude": "1", "nbEleves5ieme": 3},
        {"coAnnEtude": "2", "mtDroitsInscription": 12.5},
    ]}


def test_approuver_sends_the_population_as_read(service):
    read = Document1DService._parse_document1d_response(
        service, _response([_line(co="1", nb=3), _line(co="2", nb=7)]), ORG_ID)
    service.answer(_response([_line(nb=3, pop=True)]))

    approval = Doc1DDroitInscriptionListAppr.from_document(read)
    doc = service.approuver_document_1d(ORG_ID, approval)

    assert approval.droitInscription == [Doc1DDroitInscriptionLineAppr("1", 3), Doc1DDroitInscriptionLineAppr("2", 7)]
    method, kwargs = service.calls[0]
    assert method == "ApprouverDocument1D"
    assert kwargs["droitInscriptionListe"] == {"droitInscription": [
        {"coAnnEtude": "1", "nbEleves5ieme": 3}, {"coAnnEtude": "2", "nbEleves5ieme": 7}]}
    assert doc.droitInscriptionListe.droitInscription[0].swAppPopD1D is True


def test_from_document_without_lines_is_empty():
    assert Doc1DDroitInscriptionListAppr.from_document(FormationDocument1D(ORG_ID)).droitInscription == []


@pytest.mark.parametrize("code, description, expected", [
    ("20112", 'Mise à jour du champ "mtDroitsInscription" impossible.', EtnicDocumentNotAccessibleError),
    ("20104", "Les valeurs que vous tentez de valider ne sont pas celles enregistrées.", EtnicConcurrencyError),
    ("1545", "Document déjà approuvé !", EtnicAlreadyApprovedError),
    ("1530", "Mise à jour impossible; ce document est déjà approuvé par l'administration !",
     EtnicAlreadyApprovedError),
    ("2106", "Année d'étude invalide.", EtnicValidationError),
    ("20101", 'Le "Doc A" doit être approuvé pour pouvoir accéder au document suivant',
     EtnicDocumentNotAccessibleError),
])
def test_refusals_raise_typed_errors(service, code, description, expected):
    """The codes TQ and production answered on 2026-11-24, and 1530 from the manual."""
    service.answer(_refusal(code, description))
    with strict_errors(), pytest.raises(expected) as raised:
        service.modifier_document_1d(ORG_ID, Doc1DDroitInscriptionListSave([]))
    assert raised.value.code == code
    assert raised.value.request_id == "r-2"
