"""Unit tests for SEPS write services — construction API.

These are basic sanity checks. The SEPS write API is classified
'construction' per ``docs/PUBLIC_API_SURFACE.md`` and may change freely,
so the coverage here is intentionally light compared to the EPROM
regression suite.

Focus: verify that None-valued optional fields are stripped from the
SOAP payload (D2 fix via ``to_soap_dict``).
"""

import pytest

from pyetnic.config import Config
from pyetnic.services.enregistrer_etudiant import EnregistrerEtudiantService
from pyetnic.services.inscriptions import InscriptionsService
from pyetnic.services.models import (
    EtudiantDetailsSave,
    InscriptionInputDataSave,
    InscriptionInputSave,
    SepsNaissanceSave,
    SepsUESave,
)


@pytest.fixture(autouse=True)
def isolate():
    Config._reset()
    Config.ENV = "dev"
    Config.USERNAME = "test"
    Config.PASSWORD = "test"
    yield
    Config._reset()


class TestEnregistrerEtudiantPayload:
    def test_enregistrer_etudiant_payload_excludes_none(self, monkeypatch):
        """None-valued fields should be stripped from etudiantDetails."""
        service = EnregistrerEtudiantService()

        captured: dict = {}

        def fake_call(method_name, **kwargs):
            captured["method"] = method_name
            captured["kwargs"] = kwargs
            return {
                "body": {
                    "success": True,
                    "response": {"etudiant": {"cfNum": "123-01"}},
                },
            }

        monkeypatch.setattr(service.client_manager, "call_service", fake_call)

        details = EtudiantDetailsSave(
            niss="12345678901",
            nom="DUPONT",
            prenom="Jean",
        )
        service.enregistrer_etudiant(
            mode_enregistrement="DETAILS",
            etudiant_details=details,
        )

        assert captured["method"] == "enregistrerEtudiant"
        payload = captured["kwargs"]["etudiantDetails"]
        assert payload["niss"] == "12345678901"
        assert payload["nom"] == "DUPONT"
        assert payload["prenom"] == "Jean"
        for absent in ("sexe", "naissance", "deces", "adresse", "codeNationalite"):
            assert absent not in payload, f"expected {absent!r} to be stripped"

    def test_modifier_etudiant_payload_excludes_none(self, monkeypatch):
        service = EnregistrerEtudiantService()

        captured: dict = {}

        def fake_call(method_name, **kwargs):
            captured["method"] = method_name
            captured["kwargs"] = kwargs
            return {
                "body": {
                    "success": True,
                    "response": {"etudiantDetails": {"cfNum": "123-01"}},
                },
            }

        monkeypatch.setattr(service.client_manager, "call_service", fake_call)

        details = EtudiantDetailsSave(
            nom="DUPONT",
            naissance=SepsNaissanceSave(date="1990", codePays="150"),
        )
        service.modifier_etudiant(cf_num="123-01", etudiant_details=details)

        assert captured["method"] == "modifierEtudiant"
        payload = captured["kwargs"]["etudiantDetails"]
        assert payload["nom"] == "DUPONT"
        assert payload["naissance"] == {"date": "1990", "codePays": "150"}
        for absent in ("niss", "prenom", "sexe", "adresse", "deces"):
            assert absent not in payload


class TestInscriptionsPayload:
    def test_enregistrer_inscription_payload_excludes_none(self, monkeypatch):
        service = InscriptionsService()

        captured: dict = {}

        def fake_call(method_name, **kwargs):
            captured["method"] = method_name
            captured["kwargs"] = kwargs
            return {
                "body": {
                    "success": True,
                    "response": {"inscription": {"cfNum": "123-01"}},
                },
            }

        monkeypatch.setattr(service._enregistrer, "call_service", fake_call)

        data = InscriptionInputDataSave(
            cfNum="123-01",
            idEtab=3052,
            idImplantation=6050,
            codePostalLieuCours="1000",
            inscription=InscriptionInputSave(
                dateInscription="2024-09-01",
                statut="DE",
                ue=SepsUESave(noAdministratif=328, noOrganisation=1),
            ),
        )
        service.enregistrer_inscription(inscription_input_data=data)

        assert captured["method"] == "enregistrerInscription"
        payload = captured["kwargs"]["inscriptionInputData"]
        assert payload["cfNum"] == "123-01"
        assert payload["idEtab"] == 3052

        inscription = payload["inscription"]
        assert inscription["dateInscription"] == "2024-09-01"
        assert inscription["statut"] == "DE"
        assert inscription["ue"] == {"noAdministratif": 328, "noOrganisation": 1}
        for absent in ("anneeScolaire", "specificite"):
            assert absent not in inscription, f"expected {absent!r} to be stripped"

    def test_modifier_inscription_payload_excludes_none(self, monkeypatch):
        service = InscriptionsService()

        captured: dict = {}

        def fake_call(method_name, **kwargs):
            captured["method"] = method_name
            captured["kwargs"] = kwargs
            return {
                "body": {
                    "success": True,
                    "response": {"inscription": {"cfNum": "123-01"}},
                },
            }

        monkeypatch.setattr(service._enregistrer, "call_service", fake_call)

        data = InscriptionInputDataSave(
            cfNum="123-01",
            idEtab=3052,
            idImplantation=6050,
            codePostalLieuCours="1000",
            inscription=InscriptionInputSave(
                dateInscription="2024-09-01",
                statut="AN",
            ),
        )
        service.modifier_inscription(inscription_input_data=data)

        assert captured["method"] == "modifierInscription"
        payload = captured["kwargs"]["inscriptionInputData"]
        inscription = payload["inscription"]
        assert inscription["statut"] == "AN"
        assert "ue" not in inscription
        assert "specificite" not in inscription
