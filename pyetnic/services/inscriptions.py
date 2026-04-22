"""Services SEPS — Inscriptions (recherche et enregistrement)."""

import logging
from typing import List, Optional

from ..soap_client import SoapClientManager
from ._helpers import to_soap_dict
from .models import (
    Inscription, SepsUE, SepsLieuCours, SepsSpecificite,
    SepsDroitInscription, SepsExempteDroitInscription,
    SepsDroitInscriptionSpecifique, SepsExempteDroitInscriptionSpec,
    SepsAdmission, SepsSanction,
    InscriptionInputDataSave,
)
from .seps import SepsEtnicError, SepsAuthError

logger = logging.getLogger(__name__)


def _str(v) -> Optional[str]:
    return str(v) if v is not None else None


class InscriptionsService:
    """Client pour les services SEPS Inscriptions (X509, prod uniquement).

    Regroupe deux services ETNIC :
    - ``SEPS_ENREGISTRER_INSCRIPTION`` : enregistrerInscription, modifierInscription
    - ``SEPS_RECHERCHE_INSCRIPTIONS``  : rechercherInscriptions
    """

    def __init__(self):
        self._enregistrer = SoapClientManager("SEPS_ENREGISTRER_INSCRIPTION")
        self._recherche = SoapClientManager("SEPS_RECHERCHE_INSCRIPTIONS")

    # ------------------------------------------------------------------
    # Parsers internes
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_droit_inscription(data: Optional[dict]) -> Optional[SepsDroitInscription]:
        if not data:
            return None
        exempte_raw = data.get("exempte")
        exempte = None
        if exempte_raw:
            exempte = SepsExempteDroitInscription(
                indicateurExempteDroitInscription=exempte_raw.get("indicateurExempteDroitInscription", ""),
                motifExemption=exempte_raw.get("motifExemption", ""),
            )
        return SepsDroitInscription(
            indicateurDroitInscription=data.get("indicateurDroitInscription", ""),
            exempte=exempte,
        )

    @staticmethod
    def _parse_droit_inscription_spec(data: Optional[dict]) -> Optional[SepsDroitInscriptionSpecifique]:
        if not data:
            return None
        exempte_raw = data.get("exempte")
        exempte = None
        if exempte_raw:
            exempte = SepsExempteDroitInscriptionSpec(
                indicateurExempteDroitInscriptionSpec=exempte_raw.get("indicateurExempteDroitInscriptionSpec", ""),
                motifExemptionSpec=exempte_raw.get("motifExemptionSpec", ""),
            )
        return SepsDroitInscriptionSpecifique(
            indicateurDroitInscriptionSpecifique=data.get("indicateurDroitInscriptionSpecifique", ""),
            exempte=exempte,
        )

    @staticmethod
    def _parse_admission(data: Optional[dict]) -> Optional[SepsAdmission]:
        if not data:
            return None
        return SepsAdmission(
            codeAdmission=data.get("codeAdmission", ""),
            typeEnseignement=_str(data.get("typeEnseignement")),
            titreDelivre=_str(data.get("titreDelivre")),
            equivalence=_str(data.get("equivalence")),
            valorisationAcquis=_str(data.get("valorisationAcquis")),
        )

    @staticmethod
    def _parse_sanction(data: Optional[dict]) -> Optional[SepsSanction]:
        if not data:
            return None
        return SepsSanction(
            codeSanction=data.get("codeSanction", ""),
            valorisationAcquisSanction=_str(data.get("valorisationAcquisSanction")),
            motifAbandon=_str(data.get("motifAbandon")),
            statutFinFormation=_str(data.get("statutFinFormation")),
        )

    def _parse_specificite(self, data: Optional[dict]) -> Optional[SepsSpecificite]:
        if not data:
            return None
        return SepsSpecificite(
            regulier1=_str(data.get("regulier1")),
            regulier5=_str(data.get("regulier5")),
            droitInscription=self._parse_droit_inscription(data.get("droitInscription")),
            droitInscriptionSpecifique=self._parse_droit_inscription_spec(data.get("droitInscriptionSpecifique")),
            dureeInoccupation=_str(data.get("dureeInoccupation")),
            situationMenage=_str(data.get("situationMenage")),
            enfantACharge=_str(data.get("enfantACharge")),
            difficulteHandicap=_str(data.get("difficulteHandicap")),
            difficulteAutre=_str(data.get("difficulteAutre")),
            admission=self._parse_admission(data.get("admission")),
            sanction=self._parse_sanction(data.get("sanction")),
        )

    def _parse_inscription(self, data: dict) -> Inscription:
        ue_raw = data.get("ue")
        ue = None
        if ue_raw:
            ue = SepsUE(
                noAdministratif=ue_raw.get("noAdministratif"),
                noOrganisation=ue_raw.get("noOrganisation"),
                label=_str(ue_raw.get("label")),
                code=_str(ue_raw.get("code")),
                codeNiveau=_str(ue_raw.get("codeNiveau")),
                nombreSemaine=ue_raw.get("nombreSemaine"),
                dateDebut=_str(ue_raw.get("dateDebut")),
                dateFin=_str(ue_raw.get("dateFin")),
                fse=_str(ue_raw.get("fse")),
                noOrganisationPrecedent=_str(ue_raw.get("noOrganisationPrecedent")),
                activiteDeFormation=_str(ue_raw.get("activiteDeFormation")),
            )
        lieu_raw = data.get("lieuCours")
        lieu = SepsLieuCours(
            codePostal=_str(lieu_raw.get("codePostal")) if lieu_raw else None,
            ville=_str(lieu_raw.get("ville")) if lieu_raw else None,
        ) if lieu_raw else None

        return Inscription(
            cfNum=data.get("cfNum", ""),
            anneeScolaire=data.get("anneeScolaire"),
            idEtab=data.get("idEtab"),
            idImplantation=data.get("idImplantation"),
            dateInscription=_str(data.get("dateInscription")),
            lieuCours=lieu,
            statut=_str(data.get("statut")),
            ue=ue,
            specificite=self._parse_specificite(data.get("specificite")),
        )

    def _check_errors(self, result) -> None:
        """Lève une exception SEPS si success=False."""
        if not (result and result.get("body")):
            return
        body = result["body"]
        if not body.get("success", True):
            errors = (body.get("messages") or {}).get("error") or []
            for err in (errors if isinstance(errors, list) else [errors]):
                code = str(err.get("code"))
                desc = err.get("description", "")
                if code == "30550":
                    raise SepsAuthError(code, desc)
                raise SepsEtnicError(code, desc)

    def _parse_inscription_response(self, result) -> Optional[Inscription]:
        self._check_errors(result)
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
            and result["body"]["response"].get("inscription")
        ):
            return None
        return self._parse_inscription(result["body"]["response"]["inscription"])

    def _parse_recherche_response(self, result) -> List[Inscription]:
        self._check_errors(result)
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
        ):
            return []
        inscriptions_raw = result["body"]["response"].get("inscription") or []
        if isinstance(inscriptions_raw, dict):
            inscriptions_raw = [inscriptions_raw]
        return [self._parse_inscription(i) for i in inscriptions_raw if i]

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def rechercher_inscriptions(
        self,
        annee_scolaire: Optional[int] = None,
        etab_id: Optional[int] = None,
        date_requete: Optional[str] = None,
        cf_num: Optional[str] = None,
        no_administratif: Optional[int] = None,
        no_organisation: Optional[int] = None,
    ) -> List[Inscription]:
        """Recherche des inscriptions selon les critères fournis.

        Args:
            annee_scolaire: Année scolaire (ex. 2024).
            etab_id: Identifiant de l'établissement.
            date_requete: Date de requête (format YYYY-MM-DD).
            cf_num: Numéro CF de l'étudiant.
            no_administratif: Numéro administratif de l'UE.
            no_organisation: Numéro d'organisation de l'UE.

        Returns:
            Liste d'inscriptions correspondant aux critères.
        """
        kwargs = {}
        if annee_scolaire is not None:
            kwargs["anneeScolaire"] = annee_scolaire
        if etab_id is not None:
            kwargs["etabId"] = etab_id
        if date_requete is not None:
            kwargs["dateRequete"] = date_requete
        if cf_num is not None:
            kwargs["cfNum"] = cf_num
        if no_administratif is not None:
            kwargs["noAdministratif"] = no_administratif
        if no_organisation is not None:
            kwargs["noOrganisation"] = no_organisation

        result = self._recherche.call_service("rechercherInscriptions", **kwargs)
        return self._parse_recherche_response(result)

    def enregistrer_inscription(
        self,
        inscription_input_data: Optional[InscriptionInputDataSave] = None,
    ) -> Optional[Inscription]:
        """Enregistre une nouvelle inscription.

        Args:
            inscription_input_data: Données de l'inscription à enregistrer.

        Returns:
            L'inscription créée, ou None si non disponible.
        """
        kwargs = {}
        if inscription_input_data is not None:
            kwargs["inscriptionInputData"] = to_soap_dict(inscription_input_data)

        result = self._enregistrer.call_service("enregistrerInscription", **kwargs)
        return self._parse_inscription_response(result)

    def modifier_inscription(
        self,
        inscription_input_data: Optional[InscriptionInputDataSave] = None,
    ) -> Optional[Inscription]:
        """Modifie une inscription existante.

        Args:
            inscription_input_data: Données de l'inscription à modifier.

        Returns:
            L'inscription mise à jour, ou None si non disponible.
        """
        kwargs = {}
        if inscription_input_data is not None:
            kwargs["inscriptionInputData"] = to_soap_dict(inscription_input_data)

        result = self._enregistrer.call_service("modifierInscription", **kwargs)
        return self._parse_inscription_response(result)
