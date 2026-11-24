"""SEPS models carry the fields of the live production contract (issue #22).

Read: an inscription as ``rechercherInscriptions`` returns it, with the
``audit`` block, fee amounts, ``regulier3`` and the sanction fields; a student
with ``bisCreated``. Write: the payload built from the models is accepted by the
embedded WSDL (zeep builds the SOAP message offline) in schema order.
Identifiers are fictitious.
"""

from __future__ import annotations

from lxml import etree
from zeep import Client

from pyetnic.services.inscriptions import InscriptionsService
from pyetnic.services.models import (
    InscriptionInputDataSave,
    InscriptionInputSave,
    SepsAdmission,
    SepsAudit,
    SepsDroitInscription,
    SepsSanction,
    SepsSpecificiteSave,
    SepsUESave,
)
from pyetnic.services.seps import RechercheEtudiantsService
from pyetnic.services._helpers import to_soap_dict
from pyetnic.soap_client import get_wsdl_path

AUDIT = {
    "dateCreation": "2026-09-30T15:57:43",
    "utilisateurCreation": "ECOLE",
    "dateModification": "2026-09-30T15:57:43",
    "utilisateurModification": "ECOLE",
}
INSCRIPTION = {
    "cfNum": "1234567-89",
    "anneeScolaire": 2026,
    "idEtab": 1234,
    "idImplantation": 5678,
    "dateInscription": "2026-09-25",
    "statut": "DE",
    "ue": {"noAdministratif": 100, "noOrganisation": 2, "fse": "N"},
    "specificite": {
        "regulier1": "O",
        "regulier3": "O",
        "regulier5": "N",
        "droitInscription": {"indicateurDroitInscription": "O", "montant": "40"},
        "droitInscriptionSpecifique": {"indicateurDroitInscriptionSpecifique": "N", "montant": None},
        "admission": {"codeAdmission": "AUCUN"},
        "sanction": {
            "codeSanction": "RE",
            "valorisationAcquisSanction": "C00",
            "pourcentageAttribue": "72",
            "codeSectionFlag": True,
            "codeSection": "754103S20D4",
            "point": "72",
            "ajournement1Session": "N",
        },
    },
    "audit": AUDIT,
}


def test_inscription_read_fields():
    inscription = InscriptionsService()._parse_inscription(INSCRIPTION)
    assert inscription.audit == SepsAudit(**AUDIT)
    spec = inscription.specificite
    assert (spec.regulier1, spec.regulier3, spec.regulier5) == ("O", "O", "N")
    assert spec.droitInscription.montant == "40"
    assert spec.droitInscriptionSpecifique.montant is None
    assert spec.admission.codeAdmission == "AUCUN"
    s = spec.sanction
    assert (s.pourcentageAttribue, s.codeSectionFlag, s.codeSection, s.point, s.ajournement1Session) == (
        "72", True, "754103S20D4", "72", "N"
    )


def test_inscription_without_new_fields_still_reads():
    old = {k: v for k, v in INSCRIPTION.items() if k != "audit"}
    old["specificite"] = {"regulier1": "O", "sanction": {"motifAbandon": "TPS"}}
    inscription = InscriptionsService()._parse_inscription(old)
    assert inscription.audit is None
    assert inscription.specificite.regulier3 is None
    assert inscription.specificite.sanction.codeSanction is None


def test_etudiant_bis_created():
    etudiant = RechercheEtudiantsService._parse_etudiant({"cfNum": "1234567-89", "bisCreated": "O"})
    assert etudiant.bisCreated == "O"
    assert RechercheEtudiantsService._parse_etudiant({"cfNum": "1234567-89"}).bisCreated is None


def _message(payload) -> bytes:
    wsdl = get_wsdl_path(
        "pyetnic.resources", "SEPS_Enregistrer_Inscription_2.1/SEPSEnregistrerInscriptionService_external_v1.wsdl"
    )
    client = Client(wsdl)
    envelope = client.create_message(client.service, "enregistrerInscription", inscriptionInputData=to_soap_dict(payload))
    return etree.tostring(envelope)


def test_write_payload_follows_the_live_schema():
    payload = InscriptionInputDataSave(
        cfNum="1234567-89",
        idEtab=1234,
        idImplantation=5678,
        codePostalLieuCours="1000",
        inscription=InscriptionInputSave(
            dateInscription="2026-09-25",
            statut="DE",
            anneeScolaire=2026,
            ue=SepsUESave(noAdministratif=100, noOrganisation=2),
            specificite=SepsSpecificiteSave(
                regulier1="O",
                regulier5="N",
                regulier3="O",
                droitInscription=SepsDroitInscription(indicateurDroitInscription="O", montant="40"),
                admission=SepsAdmission(codeAdmission="AUCUN"),
                sanction=SepsSanction(codeSectionFlag=True, codeSection="754103S20D4", point="72"),
            ),
            fse=False,
        ),
    )
    xml = _message(payload).decode()
    # regulier3 goes between regulier1 and regulier5, whatever the dataclass order
    assert xml.index("regulier1>") < xml.index("regulier3>") < xml.index("regulier5>")
    assert ">40</" in xml and "montant>" in xml
    assert "codeSection>754103S20D4<" in xml
    assert xml.index("specificite>") < xml.index("fse>false<")


def test_payload_without_new_fields_has_none_of_them():
    payload = InscriptionInputDataSave(
        cfNum="1234567-89",
        idEtab=1234,
        idImplantation=5678,
        codePostalLieuCours="1000",
        inscription=InscriptionInputSave(
            dateInscription="2026-09-25",
            statut="DE",
            ue=SepsUESave(noAdministratif=100, noOrganisation=2),
            specificite=SepsSpecificiteSave(regulier1="O", admission=SepsAdmission(codeAdmission="AUTRE", valorisationAcquis="C10")),
        ),
    )
    xml = _message(payload).decode()
    for absent in ("regulier3", "montant", "fse>", "audit"):
        assert absent not in xml
