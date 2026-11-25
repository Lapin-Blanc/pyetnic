"""SEPS writers that keep the fields left out: read, merge, write (#47).

``modifierEtudiant`` and ``modifierInscription`` erase every optional field
left out (manuals 2.3 and 2.4, §3.3.2.1). The conversions send back the record
as read; the merge writers apply only the changes given. Identifiers are
fictitious; the NISS is not a valid one.
"""

from __future__ import annotations

import dataclasses

import pytest

from pyetnic.services._helpers import merge_given, to_soap_dict
from pyetnic.services.enregistrer_etudiant import EnregistrerEtudiantService
from pyetnic.services.inscriptions import InscriptionsService
from pyetnic.services.models import (
    EtudiantDetails,
    EtudiantDetailsSave,
    InscriptionInputDataSave,
    SepsAdresseSave,
    SepsDroitInscription,
    SepsSpecificite,
    SepsSpecificiteSave,
)
from pyetnic.services.seps_errors import SepsEtudiantInconnuError, SepsNotFoundError

CF = "1234567-89"

CFWB = {
    "niss": "00000000000",
    "nom": "Exemple",
    "prenom": "Alex",
    "autrePrenom": ["Sam", "Lou"],
    "sexe": "X",
    "naissance": {"date": "2001-02-03", "codePays": "00150", "localite": {"code": "25072", "description": None}},
    "deces": None,
    "adresse": {"rue": "Rue de l'Exemple", "codePostal": "5060", "codePays": "00150", "numero": "1",
                "boite": "B", "extension": None, "localite": {"code": None, "description": "Ville"},
                "localiteExtension": None},
    "codeNationalite": "00150",
}

INSCRIPTION = {
    "cfNum": CF,
    "anneeScolaire": 2026,
    "idEtab": 1234,
    "idImplantation": 5678,
    "dateInscription": "2026-09-14",
    "lieuCours": {"codePostal": "5060", "ville": "Ville"},
    "statut": "DE",
    "ue": {"noAdministratif": 537, "noOrganisation": 1, "label": "UE", "fse": "N"},
    "specificite": {
        "regulier1": "O", "regulier5": "N",
        "droitInscription": {"indicateurDroitInscription": "O"},
        "droitInscriptionSpecifique": {"indicateurDroitInscriptionSpecifique": "N",
                                       "exempte": {"indicateurExempteDroitInscriptionSpec": "O",
                                                   "motifExemptionSpec": "C01"}},
        "admission": {"codeAdmission": "AUTRE", "valorisationAcquis": "C10"},
    },
    "audit": {"dateCreation": "2026-09-30T15:57:43", "utilisateurCreation": "U",
              "dateModification": None, "utilisateurModification": None},
}


def _ok(element: str, value) -> dict:
    return {"body": {"success": True, "messages": {"error": [], "warning": [], "info": []},
                     "response": {element: value}}}


class _Recorder:
    def __init__(self, answers: dict):
        self.answers, self.calls = answers, []

    def __call__(self, method, **kwargs):
        self.calls.append((method, kwargs))
        return self.answers[method]


# ---------------------------------------------------------------------------
# Conversions
# ---------------------------------------------------------------------------

def test_every_student_field_has_its_save_counterpart():
    assert [f.name for f in dataclasses.fields(EtudiantDetails)] == [f.name for f in dataclasses.fields(EtudiantDetailsSave)]


def test_every_specificity_field_has_its_save_counterpart():
    assert {f.name for f in dataclasses.fields(SepsSpecificite)} == {f.name for f in dataclasses.fields(SepsSpecificiteSave)}


def test_student_as_read_goes_back_whole():
    details = EnregistrerEtudiantService()._parse_etudiant({"cfNum": CF, "cfwbDetails": CFWB}).cfwbDetails
    sent = to_soap_dict(EtudiantDetailsSave.from_details(details))
    assert sent["autrePrenom"] == ["Sam", "Lou"]
    assert sent["naissance"] == {"date": "2001-02-03", "codePays": "00150", "localite": {"code": "25072"}}
    assert sent["adresse"]["boite"] == "B" and sent["adresse"]["localite"] == {"description": "Ville"}
    assert {k for k, v in CFWB.items() if v is not None} == set(sent)


def test_inscription_as_read_goes_back_whole():
    inscription = InscriptionsService()._parse_inscription(INSCRIPTION)
    data = to_soap_dict(InscriptionInputDataSave.from_inscription(inscription))
    assert (data["cfNum"], data["idEtab"], data["idImplantation"], data["codePostalLieuCours"]) == (CF, 1234, 5678, "5060")
    sent = data["inscription"]
    assert (sent["dateInscription"], sent["statut"], sent["anneeScolaire"]) == ("2026-09-14", "DE", 2026)
    assert sent["ue"] == {"noAdministratif": 537, "noOrganisation": 1}
    assert sent["specificite"] == {
        "regulier1": "O", "regulier5": "N",
        "droitInscription": {"indicateurDroitInscription": "O"},
        "droitInscriptionSpecifique": {"indicateurDroitInscriptionSpecifique": "N",
                                       "exempte": {"indicateurExempteDroitInscriptionSpec": "O",
                                                   "motifExemptionSpec": "C01"}},
        "admission": {"codeAdmission": "AUTRE", "valorisationAcquis": "C10"},
    }
    assert "regulier3" not in sent["specificite"], "the search never returns it"


def test_merge_given_keeps_what_is_not_given():
    base = SepsAdresseSave(rue="Rue", codePostal="5060", codePays="00150", numero="1")
    assert merge_given(base, SepsAdresseSave(rue=None, codePostal="5000", codePays=None)) == \
        SepsAdresseSave(rue="Rue", codePostal="5000", codePays="00150", numero="1")


# ---------------------------------------------------------------------------
# mettre_a_jour_etudiant
# ---------------------------------------------------------------------------

@pytest.fixture
def etudiants(monkeypatch):
    service = EnregistrerEtudiantService()

    def wire(lire_answer):
        recorder = _Recorder({"lireEtudiant": lire_answer,
                              "modifierEtudiant": _ok("etudiantDetails", {"cfNum": CF, "cfwbDetails": CFWB})})
        monkeypatch.setattr(service._recherche.client_manager, "call_service", recorder)
        monkeypatch.setattr(service.client_manager, "call_service", recorder)
        return recorder
    service.wire = wire
    return service


def test_student_update_sends_the_whole_record_with_the_change(etudiants):
    calls = etudiants.wire(_ok("etudiant", {"cfNum": CF, "cfwbDetails": CFWB})).calls
    nouvelle = SepsAdresseSave(rue="Rue Neuve", codePostal="5000", codePays="00150", numero="2")

    etudiants.mettre_a_jour_etudiant(CF, EtudiantDetailsSave(adresse=nouvelle))

    assert [m for m, _ in calls] == ["lireEtudiant", "modifierEtudiant"]
    sent = calls[1][1]
    assert sent["cfNum"] == CF
    assert sent["etudiantDetails"]["adresse"] == {"rue": "Rue Neuve", "codePostal": "5000", "codePays": "00150", "numero": "2"}
    for kept in ("niss", "nom", "prenom", "autrePrenom", "sexe", "naissance", "codeNationalite"):
        assert kept in sent["etudiantDetails"], kept


def test_student_update_of_an_unknown_student_raises(etudiants):
    calls = etudiants.wire({"body": {"success": True, "response": None}}).calls
    with pytest.raises(SepsEtudiantInconnuError):
        etudiants.mettre_a_jour_etudiant(CF, EtudiantDetailsSave(nom="X"))
    assert [m for m, _ in calls] == ["lireEtudiant"]


def test_student_without_establishment_version_is_not_merged(etudiants):
    calls = etudiants.wire(_ok("etudiant", {"cfNum": CF, "rnDetails": CFWB, "cfwbDetails": None})).calls
    with pytest.raises(ValueError, match="cfwbDetails"):
        etudiants.mettre_a_jour_etudiant(CF, EtudiantDetailsSave(nom="X"))
    assert [m for m, _ in calls] == ["lireEtudiant"]


# ---------------------------------------------------------------------------
# mettre_a_jour_inscription
# ---------------------------------------------------------------------------

@pytest.fixture
def inscriptions(monkeypatch):
    service = InscriptionsService()

    def wire(found):
        recorder = _Recorder({"rechercherInscriptions": _ok("inscription", found),
                              "modifierInscription": _ok("inscription", INSCRIPTION)})
        monkeypatch.setattr(service._recherche, "call_service", recorder)
        monkeypatch.setattr(service._enregistrer, "call_service", recorder)
        return recorder
    service.wire = wire
    return service


def test_inscription_update_changes_only_what_is_given(inscriptions):
    calls = inscriptions.wire([INSCRIPTION]).calls
    droit = SepsDroitInscription(indicateurDroitInscription="O", montant="125")

    inscriptions.mettre_a_jour_inscription(CF, 2026, 1234, 537, 1, specificite=SepsSpecificiteSave(droitInscription=droit))

    assert [m for m, _ in calls] == ["rechercherInscriptions", "modifierInscription"]
    assert calls[0][1] == {"anneeScolaire": 2026, "etabId": 1234, "cfNum": CF, "noAdministratif": 537, "noOrganisation": 1}
    sent = calls[1][1]["inscriptionInputData"]
    assert sent["inscription"]["specificite"]["droitInscription"] == {"indicateurDroitInscription": "O", "montant": "125"}
    for kept in ("regulier1", "regulier5", "droitInscriptionSpecifique", "admission"):
        assert kept in sent["inscription"]["specificite"], kept
    assert sent["codePostalLieuCours"] == "5060" and sent["inscription"]["dateInscription"] == "2026-09-14"


def test_inscription_update_top_level_fields(inscriptions):
    calls = inscriptions.wire([INSCRIPTION]).calls
    inscriptions.mettre_a_jour_inscription(CF, 2026, 1234, 537, 1, statut="AN", code_postal_lieu_cours="5000")
    sent = calls[1][1]["inscriptionInputData"]
    assert sent["inscription"]["statut"] == "AN" and sent["codePostalLieuCours"] == "5000"
    assert sent["inscription"]["specificite"]["admission"] == {"codeAdmission": "AUTRE", "valorisationAcquis": "C10"}


def test_inscription_not_found_raises_before_any_write(inscriptions):
    calls = inscriptions.wire([dict(INSCRIPTION, ue={"noAdministratif": 537, "noOrganisation": 2})]).calls
    with pytest.raises(SepsNotFoundError):
        inscriptions.mettre_a_jour_inscription(CF, 2026, 1234, 537, 1, statut="AN")
    assert [m for m, _ in calls] == ["rechercherInscriptions"]
