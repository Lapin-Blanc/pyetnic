"""Regression tests for SOAP payload serialization (D2 fix).

These tests pin the contract introduced in Sprint 2 phase 2.3:
``modifier_document_*`` payloads are serialized via
``to_soap_dict(exclude_none=True)`` rather than ``dataclasses.asdict()``.

Before the fix, ``asdict()`` would translate ``Optional[...] = None`` fields
into ``key: None`` pairs that zeep turns into empty XML elements (``<tag/>``).
ETNIC interprets these as "set this value to empty/zero" rather than
"leave unchanged", which is the D2 defect.

After the fix, those None-valued keys are absent from the payload.
"""

from pyetnic.eprom import (
    Doc1PopulationLineSave,
    Doc1PopulationListSave,
    Doc2ActiviteEnseignementLineSave,
    Doc2ActiviteEnseignementListSave,
    Doc2InterventionExtLineSave,
    Doc2InterventionExtListSave,
    Doc3ActiviteDetailSave,
    Doc3ActiviteListeSave,
    Doc3EnseignantDetailSave,
    Doc3EnseignantListSave,
    OrganisationId,
    modifier_document_1,
    modifier_document_2,
    modifier_document_3,
)

from .fixtures.eprom_responses import (
    CANONICAL_DOCUMENT1_RESPONSE,
    CANONICAL_DOCUMENT2_RESPONSE,
    CANONICAL_DOCUMENT3_RESPONSE,
)


def _org_id() -> OrganisationId:
    return OrganisationId(
        anneeScolaire="2024-2025",
        etabId=3052,
        numAdmFormation=328,
        numOrganisation=1,
    )


class TestModifierDocument1PayloadShape:
    def test_none_fields_absent_from_population_line(self, mock_soap_call):
        """Only fields with a value should appear in each population line."""
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_RESPONSE
        liste = Doc1PopulationListSave(
            population=[
                Doc1PopulationLineSave(
                    coAnnEtude=1,
                    nbEleveA=12,
                    nbEleveTotHom=5,
                    nbEleveTotFem=7,
                ),
            ],
        )
        modifier_document_1(_org_id(), population_liste=liste)

        payload = mock_soap_call.call_args.kwargs["populationListe"]
        line = payload["population"][0]

        assert line["coAnnEtude"] == 1
        assert line["nbEleveA"] == 12
        assert line["nbEleveTotHom"] == 5
        assert line["nbEleveTotFem"] == 7

        for absent in (
            "nbEleveEhr",
            "nbEleveB",
            "nbEleveDem",
            "nbEleveMin",
            "nbEleveExm",
            "nbElevePl",
        ):
            assert absent not in line, f"expected {absent!r} to be stripped"


class TestModifierDocument2PayloadShape:
    def test_none_fields_absent_from_activite_line(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        liste = Doc2ActiviteEnseignementListSave(
            activiteEnseignement=[
                Doc2ActiviteEnseignementLineSave(coNumBranche=10, nbEleveC1=20),
            ],
        )
        modifier_document_2(_org_id(), activite_enseignement_liste=liste)

        payload = mock_soap_call.call_args.kwargs["activiteEnseignementListe"]
        line = payload["activiteEnseignement"][0]

        assert line["coNumBranche"] == 10
        assert line["nbEleveC1"] == 20

        for absent in (
            "nbPeriodePrevueAn1",
            "nbPeriodePrevueAn2",
            "nbPeriodeReelleAn1",
            "nbPeriodeReelleAn2",
            "coAdmReg",
            "coOrgReg",
            "coBraReg",
            "coEtuReg",
        ):
            assert absent not in line, f"expected {absent!r} to be stripped"

    def test_none_fields_absent_from_intervention_line(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        liste = Doc2InterventionExtListSave(
            interventionExterieure=[Doc2InterventionExtLineSave(coCatCol="X")],
        )
        modifier_document_2(_org_id(), intervention_exterieure_liste=liste)

        payload = mock_soap_call.call_args.kwargs["interventionExterieureListe"]
        line = payload["interventionExterieure"][0]

        assert line["coCatCol"] == "X"
        for absent in (
            "coNumIex",
            "coObjFse",
            "coRefPro",
            "coCriCee",
            "periodeListe",
        ):
            assert absent not in line, f"expected {absent!r} to be stripped"


class TestModifierDocument3PayloadShape:
    def test_none_fields_absent_from_enseignant_line(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT3_RESPONSE
        liste = Doc3ActiviteListeSave(
            activite=[
                Doc3ActiviteDetailSave(
                    coNumBranche=10,
                    noAnneeEtude="1",
                    enseignantListe=Doc3EnseignantListSave(
                        enseignant=[
                            Doc3EnseignantDetailSave(
                                coNumAttribution=1,
                                noMatEns="123456",
                            ),
                        ],
                    ),
                ),
            ],
        )
        modifier_document_3(_org_id(), liste)

        payload = mock_soap_call.call_args.kwargs["activiteListe"]
        activite = payload["activite"][0]
        assert activite["coNumBranche"] == 10
        assert activite["noAnneeEtude"] == "1"

        enseignant = activite["enseignantListe"]["enseignant"][0]
        assert enseignant["coNumAttribution"] == 1
        assert enseignant["noMatEns"] == "123456"

        for absent in ("coDispo", "teStatut", "nbPeriodesAttribuees"):
            assert absent not in enseignant, f"expected {absent!r} to be stripped"
