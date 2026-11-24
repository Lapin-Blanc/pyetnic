"""Every dataclass that mirrors an XSD type follows it: element names and simple types.

A new element in a refreshed contract, or a model typed differently from its
element (audit D7: Doc 3 counters declared ``xs:int`` typed ``float``), fails
here. The differences that are deliberate are listed with their reason.
"""

from __future__ import annotations

import dataclasses
import datetime
import typing
from functools import lru_cache

import pytest
from zeep import Client

import pyetnic.services.models as m
from pyetnic.config import Config
from pyetnic.soap_client import get_wsdl_path

# (Config.SERVICES key, XSD type name) -> dataclass
PAIRS: dict[tuple[str, str], type] = {
    ("ORGANISATION", "FormationOrganisationCT"): m.Organisation,
    ("LISTE_FORMATIONS", "OrganisationApercuCT"): m.OrganisationApercu,
    ("DOCUMENT1", "PopDocument1AnneeEtudeLineCT"): m.Doc1PopulationLine,
    ("DOCUMENT1", "PopDocument1AnneeEtudeLineSaveCT"): m.Doc1PopulationLineSave,
    ("DOCUMENT1D", "Doc1DDroitInscriptionLineCT"): m.Doc1DDroitInscriptionLine,
    ("DOCUMENT1D", "Doc1DDroitInscriptionSaveLineCT"): m.Doc1DDroitInscriptionLineSave,
    ("DOCUMENT1D", "Doc1DDroitInscriptionApprLineCT"): m.Doc1DDroitInscriptionLineAppr,
    ("DOCUMENT2", "Doc2ActiviteEnseignementLineCT"): m.Doc2ActiviteEnseignementLine,
    ("DOCUMENT2", "Doc2ActiviteEnseignementLineSaveCT"): m.Doc2ActiviteEnseignementLineSave,
    ("DOCUMENT2", "Doc2ActiviteEnseignementDetailCT"): m.Doc2ActiviteEnseignementDetail,
    ("DOCUMENT2", "Doc2PeriodeExtLineCT"): m.Doc2PeriodeExtLine,
    ("DOCUMENT2", "Doc2PeriodeExtLineSaveCT"): m.Doc2PeriodeExtLineSave,
    ("DOCUMENT2", "Doc2InterventionExtLineCT"): m.Doc2InterventionExtLine,
    ("DOCUMENT2", "Doc2InterventionExtLineSaveCT"): m.Doc2InterventionExtLineSave,
    ("DOCUMENT3", "Doc3ActiviteDetailCT"): m.Doc3ActiviteDetail,
    ("DOCUMENT3", "Doc3EnseignantDetailCT"): m.Doc3EnseignantDetail,
    ("DOCUMENT3", "Doc3EnseignantDetailSaveCT"): m.Doc3EnseignantDetailSave,
    ("DOCUMENT3", "Doc3ActiviteDetailSaveCT"): m.Doc3ActiviteDetailSave,
    ("SEPS_RECHERCHE_ETUDIANTS", "LocaliteType"): m.SepsLocalite,
    ("SEPS_RECHERCHE_ETUDIANTS", "AdresseType"): m.SepsAdresse,
    ("SEPS_RECHERCHE_ETUDIANTS", "NaissanceType"): m.SepsNaissance,
    ("SEPS_RECHERCHE_ETUDIANTS", "DecesType"): m.SepsDeces,
    ("SEPS_RECHERCHE_ETUDIANTS", "EtudiantDetailsType"): m.EtudiantDetails,
    ("SEPS_RECHERCHE_ETUDIANTS", "EtudiantType"): m.Etudiant,
    ("SEPS_ENREGISTRER_ETUDIANT", "EtudiantDetailsType"): m.EtudiantDetailsSave,
    ("SEPS_ENREGISTRER_ETUDIANT", "NaissanceType"): m.SepsNaissanceSave,
    ("SEPS_ENREGISTRER_ETUDIANT", "AdresseType"): m.SepsAdresseSave,
    ("SEPS_ENREGISTRER_INSCRIPTION", "DroitInscriptionType"): m.SepsDroitInscription,
    ("SEPS_ENREGISTRER_INSCRIPTION", "ExempteDroitInscriptionType"): m.SepsExempteDroitInscription,
    ("SEPS_ENREGISTRER_INSCRIPTION", "DroitInscriptionSpecifiqueType"): m.SepsDroitInscriptionSpecifique,
    ("SEPS_ENREGISTRER_INSCRIPTION", "AdmissionType"): m.SepsAdmission,
    ("SEPS_ENREGISTRER_INSCRIPTION", "SanctionType"): m.SepsSanction,
    ("SEPS_ENREGISTRER_INSCRIPTION", "LieuCoursType"): m.SepsLieuCours,
    ("SEPS_RECHERCHE_INSCRIPTIONS", "InscriptionType"): m.Inscription,
    ("SEPS_RECHERCHE_INSCRIPTIONS", "AuditType"): m.SepsAudit,
    ("SEPS_ENREGISTRER_INSCRIPTION", "UEInputType"): m.SepsUESave,
    ("SEPS_ENREGISTRER_INSCRIPTION", "SpecificiteDataType"): m.SepsSpecificiteSave,
    ("SEPS_ENREGISTRER_INSCRIPTION", "InscriptionInputType"): m.InscriptionInputSave,
    ("SEPS_ENREGISTRER_INSCRIPTION", "InscriptionInputDataType"): m.InscriptionInputDataSave,
    ("SEPS_NOTIFICATIONS", "NotificationType"): m.SepsNotification,
}

# Element names the model maps differently, on purpose.
RENAMED: dict[type, dict[str, set[str]]] = {
    # Organisation extends OrganisationApercu: the organisation's `statut` is read into
    # statutDocumentOrganisation, next to the three document statuses lister_formations gives.
    m.Organisation: {"xsd": {"statut"}, "model": {
        "statutDocumentOrganisation", "statutDocumentPopulationPeriodes",
        "statutDocumentDroitsInscription", "statutDocumentAttributions"}},
    # The aperçu groups the key elements in an OrganisationId.
    m.OrganisationApercu: {"xsd": {"anneeScolaire", "etabId", "implId", "numAdmFormation", "numOrganisation"},
                           "model": {"id"}},
}

# Simple types the model deliberately represents otherwise.
RETYPED = {
    (m.SepsNotification, "date"): "kept as the 'AAAA-MM-JJ' string (construction API, #23)",
}

# Elements optional in the contract that a write model requires, following the manual.
STRICTER = {
    (m.SepsAdresseSave, "rue"): "manual 2.3: required without NISS (spec 10)",
    (m.SepsAdresseSave, "codePays"): "manual 2.3: required without NISS (spec 10)",
}

PYTHON_TYPE = {
    "int": int, "integer": int, "long": int, "short": int,
    "float": float, "double": float, "decimal": float,
    "boolean": bool, "string": str, "date": datetime.date,
}


@lru_cache(maxsize=None)
def _client(key: str) -> Client:
    return Client(get_wsdl_path("pyetnic.resources", Config.SERVICES[key].wsdl_path))


def _xsd_elements(key: str, type_name: str) -> list:
    for xsd_type in _client(key).wsdl.types.types:
        if xsd_type.name == type_name:
            return list(xsd_type.elements)
    raise AssertionError(f"{type_name} not in the {key} contract")


def _unwrap(hint) -> tuple[object, bool]:
    args = typing.get_args(hint)
    if type(None) in args:
        return next(a for a in args if a is not type(None)), True
    return hint, False


@pytest.mark.parametrize("pair", list(PAIRS), ids=lambda p: f"{p[0]}:{p[1]}")
def test_model_follows_its_xsd_type(pair):
    cls = PAIRS[pair]
    elements = _xsd_elements(*pair)
    hints = typing.get_type_hints(cls)
    fields = {f.name for f in dataclasses.fields(cls)}
    renamed = RENAMED.get(cls, {"xsd": set(), "model": set()})

    xsd_names = {name for name, _ in elements}
    assert xsd_names - renamed["xsd"] - fields == set(), "elements without a field"
    assert fields - renamed["model"] - xsd_names == set(), "fields without an element"

    for name, element in elements:
        if name not in hints or (cls, name) in RETYPED:
            continue
        base, optional = _unwrap(hints[name])
        expected = PYTHON_TYPE.get(getattr(element.type, "name", None))
        if expected is not None and typing.get_origin(base) is not list:
            assert base is expected, f"{name}: xsd {element.type.name}, model {base}"
        if getattr(element, "min_occurs", 1) == 0 and (cls, name) not in STRICTER:
            assert optional, f"{name} is optional in the contract"
