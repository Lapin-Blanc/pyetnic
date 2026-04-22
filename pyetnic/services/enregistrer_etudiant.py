"""Service SEPS — Enregistrement et modification d'étudiants."""

import logging
from typing import Optional

from ..soap_client import SoapClientManager
from ._helpers import to_soap_dict
from .models import Etudiant, EtudiantDetailsSave
from .seps import RechercheEtudiantsService

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

    # ------------------------------------------------------------------
    # Parsers internes
    # ------------------------------------------------------------------

    def _parse_enregistrer_response(self, result) -> Optional[Etudiant]:
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
            and result["body"]["response"].get("etudiant")
        ):
            return None
        return self._parse_etudiant(result["body"]["response"]["etudiant"])

    def _parse_modifier_response(self, result) -> Optional[Etudiant]:
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
            and result["body"]["response"].get("etudiantDetails")
        ):
            return None
        return self._parse_etudiant(result["body"]["response"]["etudiantDetails"])

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def enregistrer_etudiant(
        self,
        mode_enregistrement: str,
        etudiant_details: Optional[EtudiantDetailsSave] = None,
        double_flag: Optional[bool] = None,
        create_bis_flag: Optional[bool] = None,
    ) -> Optional[Etudiant]:
        """Enregistre un nouvel étudiant dans la base CFWB.

        Args:
            mode_enregistrement: ``"NISS"`` (recherche par NISS) ou ``"DETAILS"``
                (recherche par données d'identité).
            etudiant_details: Données de l'étudiant à enregistrer.
            double_flag: Autoriser l'enregistrement en cas de doublon potentiel.
            create_bis_flag: Créer un numéro BIS si l'étudiant n'a pas de NISS.

        Returns:
            L'étudiant créé/trouvé, ou None si non trouvé.
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
    ) -> Optional[Etudiant]:
        """Modifie les données d'un étudiant existant.

        Args:
            cf_num: Numéro CF de l'étudiant (format : [0-9]{1,10}-[0-9]{2}).
            etudiant_details: Nouvelles données de l'étudiant.

        Returns:
            L'étudiant mis à jour, ou None en cas d'échec.
        """
        kwargs = {"cfNum": cf_num}
        if etudiant_details is not None:
            kwargs["etudiantDetails"] = to_soap_dict(etudiant_details)

        result = self.client_manager.call_service("modifierEtudiant", **kwargs)
        return self._parse_modifier_response(result)
