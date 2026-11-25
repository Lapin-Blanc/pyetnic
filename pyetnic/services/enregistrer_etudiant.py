"""Service SEPS — Enregistrement et modification d'étudiants."""

import logging
from typing import Optional

from ..soap_client import SoapClientManager
from ._helpers import merge_given, to_soap_dict
from .models import EnregistrerEtudiantResult, EtudiantDetailsSave, ModifierEtudiantResult
from .seps import RechercheEtudiantsService
from .seps_errors import (
    SepsEtudiantInconnuError,
    check_seps_response,
    primary_code,
    seps_messages,
    seps_response,
)

logger = logging.getLogger(__name__)


class EnregistrerEtudiantService:
    """Client pour le service SEPS EnregistrerEtudiant v1.

    Authentification par certificat X509 (PFX configuré dans .env via
    SEPS_PFX_PATH et SEPS_PFX_PASSWORD).

    Remarque : le service SEPS n'est disponible qu'en production (ws.etnic.be).

    Opérations :
    - ``enregistrer_etudiant`` : crée un étudiant dans la base CFWB
    - ``modifier_etudiant`` : modifie les données d'un étudiant existant
    """

    def __init__(self):
        self.client_manager = SoapClientManager("SEPS_ENREGISTRER_ETUDIANT")
        self._parse_etudiant = RechercheEtudiantsService._parse_etudiant
        self._recherche = RechercheEtudiantsService()

    # ------------------------------------------------------------------
    # Parsers internes
    # ------------------------------------------------------------------

    def _parse_enregistrer_response(self, result) -> EnregistrerEtudiantResult:
        check_seps_response(result)
        messages = seps_messages(result)
        etudiant = seps_response(result, "etudiant")
        bis = etudiant.get("bisCreated") if etudiant else None
        return EnregistrerEtudiantResult(
            code=primary_code(messages),
            messages=messages,
            etudiant=self._parse_etudiant(etudiant) if etudiant else None,
            bis_cree={"O": True, "N": False}.get(bis),
        )

    def _parse_modifier_response(self, result) -> ModifierEtudiantResult:
        check_seps_response(result)
        messages = seps_messages(result)
        # modifierEtudiant names its element etudiantDetails (type EtudiantType).
        etudiant = seps_response(result, "etudiantDetails")
        return ModifierEtudiantResult(
            code=primary_code(messages),
            messages=messages,
            etudiant=self._parse_etudiant(etudiant) if etudiant else None,
        )

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def enregistrer_etudiant(
        self,
        mode_enregistrement: str,
        etudiant_details: Optional[EtudiantDetailsSave] = None,
        double_flag: Optional[bool] = None,
        create_bis_flag: Optional[bool] = None,
    ) -> EnregistrerEtudiantResult:
        """Enregistre un nouvel étudiant dans la base CFWB.

        Args:
            mode_enregistrement: ``"NISS"`` (recherche par NISS) ou ``"DETAILS"``
                (recherche par données d'identité), voir
                :class:`~pyetnic.nomenclatures.ModeEnregistrement`.
            etudiant_details: Données de l'étudiant à enregistrer.
            double_flag: Autoriser l'enregistrement en cas de doublon potentiel.
            create_bis_flag: Créer un numéro BIS si l'étudiant n'a pas de NISS.

        Returns:
            Le résultat : ``etudiant`` tel que le serveur le renvoie, ``code``
            (``cree`` pour 201, nouveau CF ; ``fusionne`` pour 200, rattaché à
            une fiche existante qui garde son CF), ``bis_cree`` et ``messages``.

        Raises:
            SepsEtnicError: une sous-classe choisie par le code, pour tout refus
                (``success=false``), que le code arrive en erreur ou en
                avertissement (``SepsEtudiantExisteError`` pour 30201, avec ``cf_num``).
        """
        kwargs = {"modeEnregistrement": mode_enregistrement}
        if etudiant_details is not None:
            kwargs["etudiantDetails"] = to_soap_dict(etudiant_details)
        if double_flag is not None:
            kwargs["doubleFlag"] = double_flag
        if create_bis_flag is not None:
            kwargs["createBisFlag"] = create_bis_flag

        result = self.client_manager.call_service("enregistrerEtudiant", **kwargs)
        return self._parse_enregistrer_response(result)

    def modifier_etudiant(
        self,
        cf_num: str,
        etudiant_details: Optional[EtudiantDetailsSave] = None,
    ) -> ModifierEtudiantResult:
        """Modify an existing student (the establishment's ``cfwbDetails`` version).

        An optional field left out is **erased** by the server, and a field
        required at creation stays required: send the complete record, as
        read, with the changes applied (``EtudiantDetailsSave.from_details``),
        or use :func:`mettre_a_jour_etudiant`, which does it.

        Args:
            cf_num: Numéro CF de l'étudiant (format : [0-9]{1,10}-[0-9]{2}).
            etudiant_details: Nouvelles données de l'étudiant.

        Returns:
            Le résultat : ``etudiant`` mis à jour, ``code`` et ``messages``.

        Raises:
            SepsEtnicError: une sous-classe choisie par le code, pour tout refus
                (``success=false``), que le code arrive en erreur ou en
                avertissement (``SepsAucuneModificationError`` pour 30443).
        """
        kwargs = {"cfNum": cf_num}
        if etudiant_details is not None:
            kwargs["etudiantDetails"] = to_soap_dict(etudiant_details)

        result = self.client_manager.call_service("modifierEtudiant", **kwargs)
        return self._parse_modifier_response(result)

    def mettre_a_jour_etudiant(
        self,
        cf_num: str,
        changements: EtudiantDetailsSave,
    ) -> ModifierEtudiantResult:
        """Modify a student, keeping every field not given.

        Reads the establishment's version (``cfwbDetails``) with
        :func:`lire_etudiant`, replaces the fields of ``changements`` that are
        not ``None`` (a nested ``adresse`` or ``naissance`` given replaces the
        one read as a whole), and sends the complete record with
        :func:`modifier_etudiant`. To erase a field, use
        :func:`modifier_etudiant` with ``EtudiantDetailsSave.from_details``.

        Raises:
            SepsEtudiantInconnuError: ``lire_etudiant`` finds no student.
            ValueError: the student has no establishment version to merge into.
            SepsAucuneModificationError: nothing changed (30443). The first
                write of an unchanged record was accepted (200), the next ones
                refused with 30443 (production, 2026-11-25).
        """
        etudiant = self._recherche.lire_etudiant(cf_num)
        if etudiant is None:
            raise SepsEtudiantInconnuError(None, f"lireEtudiant found no student {cf_num}")
        if etudiant.cfwbDetails is None:
            raise ValueError(
                f"student {cf_num} has no establishment version (cfwbDetails) to merge into: "
                "send the complete record with modifier_etudiant"
            )
        merged = merge_given(EtudiantDetailsSave.from_details(etudiant.cfwbDetails), changements)
        return self.modifier_etudiant(cf_num, merged)
