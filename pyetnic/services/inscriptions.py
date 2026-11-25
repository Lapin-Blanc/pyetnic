"""Services SEPS — Inscriptions (recherche et enregistrement)."""

import logging
from typing import List, Optional

from ..soap_client import SoapClientManager
from ._helpers import _as_list, merge_given, to_soap_dict
from .models import (
    Inscription, SepsUE, SepsLieuCours, SepsSpecificite,
    SepsDroitInscription, SepsExempteDroitInscription,
    SepsDroitInscriptionSpecifique, SepsExempteDroitInscriptionSpec,
    SepsAdmission, SepsSanction, SepsAudit,
    InscriptionInputDataSave,
    InscriptionResult,
    SepsSpecificiteSave,
)
from .seps_errors import SepsNotFoundError, check_seps_response, primary_code, seps_messages, seps_response

logger = logging.getLogger(__name__)

# rechercherInscriptions answers "no inscription found" with these codes
# (30103 as a warning in production): an empty list, not an error.
_RECHERCHE_NOT_FOUND_CODES = frozenset({"30102", "30103"})


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
            montant=_str(data.get("montant")),
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
            montant=_str(data.get("montant")),
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
            codeSanction=_str(data.get("codeSanction")),
            valorisationAcquisSanction=_str(data.get("valorisationAcquisSanction")),
            motifAbandon=_str(data.get("motifAbandon")),
            statutFinFormation=_str(data.get("statutFinFormation")),
            pourcentageAttribue=_str(data.get("pourcentageAttribue")),
            codeSectionFlag=data.get("codeSectionFlag"),
            codeSection=_str(data.get("codeSection")),
            point=_str(data.get("point")),
            ajournement1Session=_str(data.get("ajournement1Session")),
        )

    @staticmethod
    def _parse_audit(data: Optional[dict]) -> Optional[SepsAudit]:
        if not data:
            return None
        return SepsAudit(
            dateCreation=_str(data.get("dateCreation")),
            utilisateurCreation=_str(data.get("utilisateurCreation")),
            dateModification=_str(data.get("dateModification")),
            utilisateurModification=_str(data.get("utilisateurModification")),
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
            regulier3=_str(data.get("regulier3")),
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
            audit=self._parse_audit(data.get("audit")),
        )

    def _parse_inscription_response(self, result) -> InscriptionResult:
        check_seps_response(result)
        messages = seps_messages(result)
        inscription = seps_response(result, "inscription")
        return InscriptionResult(
            code=primary_code(messages),
            messages=messages,
            inscription=self._parse_inscription(inscription) if inscription else None,
        )

    def _parse_recherche_response(self, result) -> List[Inscription]:
        if check_seps_response(result, not_found=_RECHERCHE_NOT_FOUND_CODES):
            return []
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
        ):
            return []
        # zeep peut retourner un seul dict ou une liste selon le nombre de résultats
        inscriptions_raw = _as_list(result["body"]["response"].get("inscription"))
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
            Liste d'inscriptions correspondant aux critères ; vide quand le
            serveur répond « aucune inscription » (30102, 30103).

        Raises:
            SepsEtnicError: une sous-classe choisie par le code, pour tout refus
                (``success=false``), que le code arrive en erreur ou en
                avertissement (``SepsUeInconnueError`` pour 30101, par exemple).
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
    ) -> InscriptionResult:
        """Enregistre une nouvelle inscription.

        Args:
            inscription_input_data: Données de l'inscription à enregistrer.

        Returns:
            Le résultat : ``inscription`` telle que le serveur la renvoie,
            ``code`` et ``messages`` (``plus_de_4_ue`` pour 30051).

        Raises:
            SepsEtnicError: une sous-classe choisie par le code, pour tout refus
                (``success=false``), que le code arrive en erreur ou en
                avertissement (``SepsUeInconnueError`` pour 30101, par exemple).
        """
        kwargs = {}
        if inscription_input_data is not None:
            kwargs["inscriptionInputData"] = to_soap_dict(inscription_input_data)

        result = self._enregistrer.call_service("enregistrerInscription", **kwargs)
        return self._parse_inscription_response(result)

    def modifier_inscription(
        self,
        inscription_input_data: Optional[InscriptionInputDataSave] = None,
    ) -> InscriptionResult:
        """Modify an existing inscription.

        An optional field left out is **erased** by the server, and a field
        required at creation stays required: send the complete inscription, as
        read, with the changes applied (``InscriptionInputDataSave.from_inscription``),
        or use :func:`mettre_a_jour_inscription`, which does it.

        Args:
            inscription_input_data: Données de l'inscription à modifier.

        Returns:
            Le résultat : ``inscription`` mise à jour, ``code`` et ``messages``.

        Raises:
            SepsEtnicError: une sous-classe choisie par le code, pour tout refus
                (``success=false``), que le code arrive en erreur ou en
                avertissement (``SepsUeInconnueError`` pour 30101, par exemple).
        """
        kwargs = {}
        if inscription_input_data is not None:
            kwargs["inscriptionInputData"] = to_soap_dict(inscription_input_data)

        result = self._enregistrer.call_service("modifierInscription", **kwargs)
        return self._parse_inscription_response(result)

    def mettre_a_jour_inscription(
        self,
        cf_num: str,
        annee_scolaire: int,
        etab_id: int,
        no_administratif: int,
        no_organisation: int,
        *,
        specificite: Optional[SepsSpecificiteSave] = None,
        date_inscription: Optional[str] = None,
        statut: Optional[str] = None,
        code_postal_lieu_cours: Optional[str] = None,
        id_implantation: Optional[int] = None,
        fse: Optional[bool] = None,
    ) -> InscriptionResult:
        """Modify an inscription, keeping every field not given.

        Finds the inscription of the student in the UE with
        :func:`rechercher_inscriptions`, applies the changes given (in
        ``specificite``, the fields that are not ``None``; a nested
        ``droitInscription``, ``admission`` or ``sanction`` given replaces the
        one read as a whole), and sends the complete inscription with
        :func:`modifier_inscription`.

        .. warning::
           ``rechercherInscriptions`` never returns ``regulier3`` nor
           ``sanction.ajournement1Session`` (production, 2026-11-25): the merge
           cannot keep them. Give them in ``specificite`` when the inscription
           has them, or the server erases them.

        The server accepts an unchanged inscription without any message (no
        30443, production, 2026-11-25): an empty change still writes.

        Raises:
            SepsNotFoundError: no inscription of this student in this UE.
            ValueError: several inscriptions match.
        """
        found = [
            inscription
            for inscription in self.rechercher_inscriptions(
                annee_scolaire=annee_scolaire, etab_id=etab_id, cf_num=cf_num,
                no_administratif=no_administratif, no_organisation=no_organisation,
            )
            if inscription.cfNum == cf_num and inscription.ue is not None
            and (inscription.ue.noAdministratif, inscription.ue.noOrganisation) == (no_administratif, no_organisation)
        ]
        if not found:
            raise SepsNotFoundError(
                None, f"no inscription of {cf_num} in UE {no_administratif}/{no_organisation} ({annee_scolaire})"
            )
        if len(found) > 1:
            raise ValueError(f"{len(found)} inscriptions of {cf_num} match UE {no_administratif}/{no_organisation}")

        data = InscriptionInputDataSave.from_inscription(found[0])
        inscription = data.inscription
        if specificite is not None:
            inscription.specificite = merge_given(inscription.specificite or SepsSpecificiteSave(), specificite)
        if date_inscription is not None:
            inscription.dateInscription = date_inscription
        if statut is not None:
            inscription.statut = statut
        if fse is not None:
            inscription.fse = fse
        if code_postal_lieu_cours is not None:
            data.codePostalLieuCours = code_postal_lieu_cours
        if id_implantation is not None:
            data.idImplantation = id_implantation
        return self.modifier_inscription(data)
