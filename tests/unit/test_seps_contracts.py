"""The embedded SEPS contracts load offline and carry the live production fields.

The contracts come from the live services (``tools/refresh_seps_contracts.py``),
not from the SOA catalogue, whose "2.1" archives lag behind production.
"""

from __future__ import annotations

import pytest
from zeep import Client

from pyetnic.soap_client import get_wsdl_path

INSCRIPTION_NS = "http://enseignement.cfwb.be/types/seps/inscription/v1"
ETUDIANT_NS = "http://enseignement.cfwb.be/types/seps/etudiant/v1"

WSDLS = {
    "enregistrer_etudiant": "SEPS_Enregistrer_Etudiant_2.1/SEPSEnregistrerEtudiantService_external_v1.wsdl",
    "recherche_etudiants": "SEPS_Recherche_Etudiants_2.1/SEPSRechercheEtudiantsService_external_v1.wsdl",
    "enregistrer_inscription": "SEPS_Enregistrer_Inscription_2.1/SEPSEnregistrerInscriptionService_external_v1.wsdl",
    "recherche_inscriptions": "SEPS_Recherche_Inscriptions_2.1/SEPSRechercheInscriptionsService_external_v1.wsdl",
    "notifications": "SEPS_Notifications_1.0.8/SEPSNotificationsService_external_v1.wsdl",
}


def _client(name: str) -> Client:
    return Client(get_wsdl_path("pyetnic.resources", WSDLS[name]))


def _elements(client: Client, namespace: str, type_name: str) -> list[str]:
    return [name for name, _ in client.get_type(f"{{{namespace}}}{type_name}").elements]


@pytest.mark.parametrize("name", sorted(WSDLS))
def test_contract_loads_offline(name):
    """Every import resolves to a local file: no network is needed."""
    assert _client(name).wsdl.services


@pytest.mark.parametrize("name", ["enregistrer_etudiant", "recherche_etudiants"])
def test_etudiant_reports_bis_creation(name):
    assert "bisCreated" in _elements(_client(name), ETUDIANT_NS, "EtudiantType")


@pytest.mark.parametrize("name", ["enregistrer_inscription", "recherche_inscriptions"])
def test_inscription_carries_audit_and_new_fields(name):
    client = _client(name)
    assert _elements(client, INSCRIPTION_NS, "InscriptionType")[-1] == "audit"
    assert "montant" in _elements(client, INSCRIPTION_NS, "DroitInscriptionType")
    assert "fse" in _elements(client, INSCRIPTION_NS, "InscriptionInputType")
    sanction = _elements(client, INSCRIPTION_NS, "SanctionType")
    assert {"pourcentageAttribue", "codeSectionFlag", "codeSection", "point"} <= set(sanction)


def test_enregistrer_inscription_has_regulier3_between_1_and_5():
    """Production's enregistrerInscription is at manual level 2.4 (sequence order matters)."""
    specificite = _elements(_client("enregistrer_inscription"), INSCRIPTION_NS, "SpecificiteDataType")
    assert specificite[:3] == ["regulier1", "regulier3", "regulier5"]
    assert "ajournement1Session" in _elements(_client("enregistrer_inscription"), INSCRIPTION_NS, "SanctionType")


def test_recherche_inscriptions_lags_without_regulier3():
    """Production's rechercheInscriptions serves an older inscription_v1 (seen 2026-11-24).

    When a refresh makes this fail, ETNIC has caught up: delete the test.
    """
    specificite = _elements(_client("recherche_inscriptions"), INSCRIPTION_NS, "SpecificiteDataType")
    assert "regulier3" not in specificite
