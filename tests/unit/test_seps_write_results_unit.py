"""SEPS writes return the server's code and messages (issue #21).

Answers follow the ETNIC manuals' examples (Enregistrer Étudiants 2.3,
Enregistrer Inscriptions 2.4) and what production answered on 2026-11-24
(enregistrerEtudiant by NISS: info 201 "L'étudiant est sauvé" + version info).
Identifiers are fictitious.
"""

from __future__ import annotations

import pytest

from pyetnic.seps import (
    EnregistrerEtudiantResult,
    InscriptionResult,
    ModifierEtudiantResult,
    SepsEcritureResult,
    SepsMessage,
)
from pyetnic.services.enregistrer_etudiant import EnregistrerEtudiantService
from pyetnic.services.inscriptions import InscriptionsService
from pyetnic.services.models import (
    EtudiantDetailsSave,
    InscriptionInputDataSave,
    InscriptionInputSave,
    SepsUESave,
)
from pyetnic.services.seps_errors import primary_code, seps_messages

VERSION = {"code": "2.4.6", "description": "version"}
ETUDIANT = {"cfNum": "1234567-89", "rnDetails": {"nom": "DUPONT"}, "cfwbDetails": {"nom": "DUPONT"}}
INSCRIPTION = {
    "cfNum": "1234567-89",
    "anneeScolaire": 2026,
    "idEtab": 1234,
    "idImplantation": 5678,
    "dateInscription": "2026-09-25",
    "statut": "DE",
    "ue": {"noAdministratif": 100, "noOrganisation": 2},
}


def answer(*, info=(), warning=(), response=None, success=True):
    body = {"success": success, "messages": {"error": [], "warning": list(warning), "info": list(info)}}
    if response is not None:
        body["response"] = response
    return {"body": body}


def msg(code, description=""):
    return {"code": code, "description": description}


def enregistrer(monkeypatch, result):
    service = EnregistrerEtudiantService()
    monkeypatch.setattr(service.client_manager, "call_service", lambda *a, **k: result)
    return service.enregistrer_etudiant("NISS", etudiant_details=EtudiantDetailsSave(niss="00000000000"))


def inscrire(monkeypatch, result, operation="enregistrer_inscription"):
    service = InscriptionsService()
    monkeypatch.setattr(service._enregistrer, "call_service", lambda *a, **k: result)
    data = InscriptionInputDataSave(
        cfNum="1234567-89",
        idEtab=1234,
        idImplantation=5678,
        codePostalLieuCours="1000",
        inscription=InscriptionInputSave(
            dateInscription="2026-09-25", statut="DE", anneeScolaire=2026, ue=SepsUESave(noAdministratif=100, noOrganisation=2)
        ),
    )
    return getattr(service, operation)(inscription_input_data=data)


class TestEnregistrerEtudiant:
    def test_creation_by_niss_as_seen_in_production(self, monkeypatch):
        result = enregistrer(
            monkeypatch,
            answer(info=[msg("201", "L'étudiant est sauvé"), VERSION], response={"etudiant": ETUDIANT}),
        )
        assert isinstance(result, EnregistrerEtudiantResult)
        assert isinstance(result, SepsEcritureResult)
        assert (result.code, result.cree, result.fusionne) == ("201", True, False)
        assert result.etudiant.cfNum == "1234567-89"
        assert result.messages == [SepsMessage("info", "201", "L'étudiant est sauvé")]
        assert result.avertissements == []
        assert result.bis_cree is None

    def test_merge_with_an_existing_record(self, monkeypatch):
        result = enregistrer(monkeypatch, answer(info=[msg("200", "")], response={"etudiant": ETUDIANT}))
        assert (result.cree, result.fusionne) == (False, True)

    @pytest.mark.parametrize("flag, expected", [("O", True), ("N", False)])
    def test_bis_created(self, monkeypatch, flag, expected):
        etudiant = dict(ETUDIANT, bisCreated=flag)
        result = enregistrer(monkeypatch, answer(info=[msg("201", "")], response={"etudiant": etudiant}))
        assert result.bis_cree is expected

    def test_success_without_message_or_response(self, monkeypatch):
        result = enregistrer(monkeypatch, answer())
        assert (result.code, result.etudiant, result.messages) == (None, None, [])


def test_modifier_etudiant_reads_etudiant_details(monkeypatch):
    service = EnregistrerEtudiantService()
    monkeypatch.setattr(
        service.client_manager,
        "call_service",
        lambda *a, **k: answer(info=[msg("200", "The student changes have been applied.")], response={"etudiantDetails": ETUDIANT}),
    )
    result = service.modifier_etudiant(cf_num="1234567-89", etudiant_details=EtudiantDetailsSave(nom="DUPONT"))
    assert isinstance(result, ModifierEtudiantResult)
    assert (result.code, result.etudiant.cfNum) == ("200", "1234567-89")


class TestInscription:
    def test_creation(self, monkeypatch):
        result = inscrire(monkeypatch, answer(info=[msg("201", "Ok création")], response={"inscription": INSCRIPTION}))
        assert isinstance(result, InscriptionResult)
        assert result.code == "201"
        assert result.inscription.ue.noAdministratif == 100
        assert result.plus_de_4_ue is False

    def test_manual_example_without_message(self, monkeypatch):
        """The manual's successful enregistrerInscription carries no message at all."""
        result = inscrire(monkeypatch, answer(response={"inscription": INSCRIPTION}))
        assert (result.code, result.messages) == (None, [])
        assert result.inscription.cfNum == "1234567-89"

    @pytest.mark.parametrize("niveau", ["info", "warning"])
    def test_more_than_four_ue_is_reported_not_raised(self, monkeypatch, niveau):
        message = msg("30051", "Ok création mais inscrit dans plus de 4 Ues")
        result = inscrire(monkeypatch, answer(response={"inscription": INSCRIPTION}, **{niveau: [message]}))
        assert result.plus_de_4_ue is True
        assert result.avertissements == [SepsMessage(niveau, "30051", message["description"])]

    def test_modifier_inscription(self, monkeypatch):
        result = inscrire(
            monkeypatch, answer(info=[msg("200", "Ok modification")], response={"inscription": INSCRIPTION}), "modifier_inscription"
        )
        assert result.code == "200"
        assert result.inscription.statut == "DE"


class TestHelpers:
    def test_messages_keep_levels_in_order_and_drop_the_version(self):
        result = answer(info=[VERSION, msg("201", "a")], warning=[msg("30051", "b")])
        assert seps_messages(result) == [SepsMessage("warning", "30051", "b"), SepsMessage("info", "201", "a")]

    def test_primary_code_prefers_the_success_code(self):
        messages = [SepsMessage("warning", "30051", ""), SepsMessage("info", "201", "")]
        assert primary_code(messages) == "201"
        assert primary_code([SepsMessage("warning", "30051", "")]) == "30051"
        assert primary_code([]) is None

    def test_a_le_code(self):
        result = SepsEcritureResult("201", [SepsMessage("info", "201", ""), SepsMessage("warning", "30051", "")])
        assert result.a_le_code("30051") and not result.a_le_code("30443")
