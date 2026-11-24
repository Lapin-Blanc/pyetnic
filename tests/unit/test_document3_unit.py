# test_document3_unit.py — mock-only unit tests for Document3Service.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.error_mode import permissive_errors
from pyetnic.exceptions import EtnicBusinessError
from pyetnic.services.document3 import Document3Service
from pyetnic.services.models import (
    Doc3ActiviteDetail,
    Doc3ActiviteDetailSave,
    Doc3ActiviteListeSave,
    Doc3EnseignantDetail,
    Doc3EnseignantDetailSave,
    Doc3EnseignantListSave,
    FormationDocument3,
    OrganisationId,
)

logger = logging.getLogger(__name__)


def _mock_doc3_response(num_adm: int = 328, num_org: int = 1, activites: list | None = None):
    acts = activites or [
        {
            "coNumBranche": 10,
            "coCategorie": "A",
            "teNomBranche": "Mathématiques",
            "noAnneeEtude": "1",
            "nbPeriodesDoc8": 4,
            "nbPeriodesPrevuesDoc2": 4,
            "nbPeriodesReellesDoc2": 4,
            "enseignantListe": {
                "enseignant": [
                    {
                        "coNumAttribution": 1,
                        "noMatEns": "123456",
                        "teNomEns": "Dupont",
                        "tePrenomEns": "Jean",
                        "teAbrEns": "DUP",
                        "teEnseignant": "Dupont Jean",
                        "coDispo": "D",
                        "teStatut": "DEF",
                        "nbPeriodesAttribuees": 4.0,
                        "tsMaj": None,
                        "teUserMaj": None,
                    }
                ]
            },
        }
    ]
    return {
        "body": {
            "success": True,
            "response": {
                "document3": {
                    "id": {
                        "anneeScolaire": Config.ANNEE_SCOLAIRE or "2023-2024",
                        "etabId": Config.ETAB_ID or 1234,
                        "numAdmFormation": num_adm,
                        "numOrganisation": num_org,
                    },
                    "activiteListe": {"activite": acts},
                }
            },
        }
    }


@pytest.fixture
def service():
    return Document3Service()


def test_lire_document3_mock(service, monkeypatch):
    """Vérifie le parsing de la réponse LireDocument3."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc3_response(328, 1),
    )

    doc = service.lire_document_3(org_id)

    assert isinstance(doc, FormationDocument3)
    assert doc.id == org_id
    assert doc.activiteListe is not None
    activites = doc.activiteListe.activite
    assert len(activites) == 1
    act = activites[0]
    assert isinstance(act, Doc3ActiviteDetail)
    assert act.coNumBranche == 10
    assert act.teNomBranche == "Mathématiques"
    assert act.enseignantListe is not None
    assert len(act.enseignantListe.enseignant) == 1
    ens = act.enseignantListe.enseignant[0]
    assert isinstance(ens, Doc3EnseignantDetail)
    assert ens.coNumAttribution == 1
    assert ens.noMatEns == "123456"
    assert ens.teNomEns == "Dupont"
    assert ens.nbPeriodesAttribuees == 4.0


def test_lire_document3_mock_reponse_vide(service, monkeypatch):
    """Vérifie que lire_document_3 retourne None si la réponse est vide."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": True, "response": {}}},
    )

    with pytest.raises(EtnicBusinessError):
        service.lire_document_3(org_id)
    with pytest.warns(DeprecationWarning), permissive_errors():
        assert service.lire_document_3(org_id) is None


def test_lire_document3_activite_sans_enseignants(service, monkeypatch):
    """Vérifie que lire_document_3 gère correctement une activité sans enseignants."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1,
    )
    activite_sans_ens = {
        "coNumBranche": 20, "coCategorie": "B", "teNomBranche": "Français",
        "noAnneeEtude": "2", "nbPeriodesDoc8": 2, "nbPeriodesPrevuesDoc2": 2,
        "nbPeriodesReellesDoc2": 2, "enseignantListe": None,
    }
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc3_response(328, 1, [activite_sans_ens]),
    )

    doc = service.lire_document_3(org_id)
    assert doc is not None
    assert doc.activiteListe.activite[0].enseignantListe is None


def test_modifier_document3_mock(service, monkeypatch):
    """Vérifie que modifier_document_3 retourne le document mis à jour."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1,
    )
    activite_modifiee = [
        {
            "coNumBranche": 10, "coCategorie": "A", "teNomBranche": "Mathématiques",
            "noAnneeEtude": "1", "nbPeriodesDoc8": 4, "nbPeriodesPrevuesDoc2": 4,
            "nbPeriodesReellesDoc2": 4,
            "enseignantListe": {
                "enseignant": [
                    {
                        "coNumAttribution": 1, "noMatEns": "123456",
                        "teNomEns": "Dupont", "tePrenomEns": "Jean",
                        "teAbrEns": "DUP", "teEnseignant": "Dupont Jean",
                        "coDispo": "D", "teStatut": "DEF",
                        "nbPeriodesAttribuees": 6.0,
                        "tsMaj": None, "teUserMaj": None,
                    }
                ]
            },
        }
    ]
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc3_response(328, 1, activite_modifiee),
    )

    liste_save = Doc3ActiviteListeSave(
        activite=[
            Doc3ActiviteDetailSave(
                coNumBranche=10,
                noAnneeEtude="1",
                enseignantListe=Doc3EnseignantListSave(
                    enseignant=[
                        Doc3EnseignantDetailSave(
                            coNumAttribution=1,
                            noMatEns="123456",
                            coDispo="D",
                            teStatut="DEF",
                            nbPeriodesAttribuees=6.0,
                        )
                    ]
                ),
            )
        ]
    )
    doc = service.modifier_document_3(org_id, liste_save)

    assert isinstance(doc, FormationDocument3)
    assert doc.id == org_id
    ens = doc.activiteListe.activite[0].enseignantListe.enseignant[0]
    assert ens.nbPeriodesAttribuees == 6.0
    assert ens.coNumAttribution == 1


# ---------------------------------------------------------------------------
# ajouter_attributions_document_3: read, merge, write the touched branches
# ---------------------------------------------------------------------------

def _branche(num, annee, enseignants):
    return {
        "coNumBranche": num, "coCategorie": "A", "teNomBranche": f"Branche {num}", "noAnneeEtude": annee,
        "nbPeriodesDoc8": 40, "nbPeriodesPrevuesDoc2": 40, "nbPeriodesReellesDoc2": 40,
        "enseignantListe": {"enseignant": enseignants},
    }


def _enseignant(num, mat, periodes, statut="DEF", dispo=None):
    return {"coNumAttribution": num, "noMatEns": mat, "teNomEns": None, "tePrenomEns": None, "teAbrEns": None,
            "teEnseignant": None, "coDispo": dispo, "teStatut": statut, "nbPeriodesAttribuees": periodes,
            "tsMaj": None, "teUserMaj": None}


def _new(mat, periodes):
    return Doc3EnseignantDetailSave(noMatEns=mat, teStatut="TEMP", nbPeriodesAttribuees=periodes)


ORG = OrganisationId(anneeScolaire="2025-2026", etabId=1234, numAdmFormation=328, numOrganisation=1)


@pytest.fixture
def recorded(service, monkeypatch):
    """Read answers the document given to it; the write is recorded and echoed."""
    calls = []

    def setup(activites):
        def fake(method, **kwargs):
            calls.append((method, kwargs))
            return _mock_doc3_response(activites=activites)
        monkeypatch.setattr(service.client_manager, "call_service", fake)
        return calls
    return setup


def test_ajouter_keeps_the_existing_attributions_of_the_branch(service, recorded):
    calls = recorded([
        _branche(10, "1", [_enseignant(1, "111111", 10.0), _enseignant(2, "222222", 6.0, dispo="05")]),
        _branche(20, "1", [_enseignant(1, "333333", 8.0)]),
    ])

    service.ajouter_attributions_document_3(ORG, Doc3ActiviteListeSave([
        Doc3ActiviteDetailSave(10, "1", Doc3EnseignantListSave([_new("444444", 4.0)])),
    ]))

    assert [m for m, _ in calls] == ["LireDocument3", "ModifierDocument3"]
    sent = calls[1][1]["activiteListe"]["activite"]
    assert len(sent) == 1, "the untouched branch 20 is not sent"
    assert sent[0]["coNumBranche"] == 10 and sent[0]["noAnneeEtude"] == "1"
    assert sent[0]["enseignantListe"]["enseignant"] == [
        {"coNumAttribution": 1, "noMatEns": "111111", "teStatut": "DEF", "nbPeriodesAttribuees": 10.0},
        {"coNumAttribution": 2, "noMatEns": "222222", "coDispo": "05", "teStatut": "DEF", "nbPeriodesAttribuees": 6.0},
        {"noMatEns": "444444", "teStatut": "TEMP", "nbPeriodesAttribuees": 4.0},
    ]


def test_ajouter_drops_the_placeholder_of_a_never_written_branch(service, recorded):
    """A Doc 3 never written reads with one empty line per branch: it is not sent back."""
    calls = recorded([_branche(10, "1", [_enseignant(1, None, 0.0, statut=None)])])

    service.ajouter_attributions_document_3(ORG, Doc3ActiviteListeSave([
        Doc3ActiviteDetailSave(10, "1", Doc3EnseignantListSave([_new("444444", 4.0)])),
    ]))

    assert calls[1][1]["activiteListe"]["activite"][0]["enseignantListe"]["enseignant"] == [
        {"noMatEns": "444444", "teStatut": "TEMP", "nbPeriodesAttribuees": 4.0},
    ]


def test_ajouter_refuses_a_branch_the_document_does_not_have(service, recorded):
    calls = recorded([_branche(10, "1", [])])

    with pytest.raises(ValueError, match="coNumBranche=99"):
        service.ajouter_attributions_document_3(ORG, Doc3ActiviteListeSave([
            Doc3ActiviteDetailSave(99, "1", Doc3EnseignantListSave([_new("444444", 4.0)])),
        ]))
    assert [m for m, _ in calls] == ["LireDocument3"], "nothing is written"


def test_ajouter_matches_the_year_of_study_too(service, recorded):
    calls = recorded([_branche(10, "1", [_enseignant(1, "111111", 10.0)]), _branche(10, "2", [])])

    service.ajouter_attributions_document_3(ORG, Doc3ActiviteListeSave([
        Doc3ActiviteDetailSave(10, "2", Doc3EnseignantListSave([_new("444444", 4.0)])),
    ]))

    [branche] = calls[1][1]["activiteListe"]["activite"]
    assert branche["noAnneeEtude"] == "2"
    assert branche["enseignantListe"]["enseignant"] == [
        {"noMatEns": "444444", "teStatut": "TEMP", "nbPeriodesAttribuees": 4.0}]


def test_doc3_period_counters_follow_the_contract_types():
    """Audit D7: the XSD declares the three counters xs:int, the attribution xs:float."""
    import typing

    from zeep import Client

    from pyetnic.config import Config
    from pyetnic.soap_client import get_wsdl_path

    hints = typing.get_type_hints(Doc3ActiviteDetail)
    for name in ("nbPeriodesDoc8", "nbPeriodesPrevuesDoc2", "nbPeriodesReellesDoc2"):
        assert hints[name] == typing.Optional[int], name
    client = Client(get_wsdl_path("pyetnic.resources", Config.SERVICES["DOCUMENT3"].wsdl_path))
    ns = "http://enseignement.cfwb.be/types/formation/document3/v1"
    types = {name: el.type.name for name, el in client.get_type(f"{{{ns}}}Doc3ActiviteDetailCT").elements}
    assert {types[n] for n in ("nbPeriodesDoc8", "nbPeriodesPrevuesDoc2", "nbPeriodesReellesDoc2")} == {"int"}
    detail = {name: el.type.name for name, el in client.get_type(f"{{{ns}}}Doc3EnseignantDetailCT").elements}
    assert detail["nbPeriodesAttribuees"] == "float"
