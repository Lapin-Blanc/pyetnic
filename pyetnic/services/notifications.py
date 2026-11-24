"""Service SEPS - Notifications (changements de signalétique des étudiants)."""

import datetime as dt
import logging
from typing import List, Union

from ..soap_client import SoapClientManager
from ._helpers import _as_list
from .models import SepsNotification
from .seps_errors import check_seps_response

logger = logging.getLogger(__name__)

# "No notification found for etabId and dateFrom" (manual 2.3, §3.1.1.5).
_NOT_FOUND_CODES = frozenset({"30105"})


def _str(value) -> Union[str, None]:
    return str(value) if value is not None else None


class NotificationsService:
    """Client pour le service SEPS Notifications v1 (``lireNotifications``).

    Authentification par certificat X509, comme les autres services SEPS : le
    catalogue des services annonce un profil UsernameToken, mais la production
    refuse les identifiants EPROM (SECU-1101) et accepte le certificat
    (observé le 2026-11-24).
    """

    def __init__(self) -> None:
        self.client_manager = SoapClientManager("SEPS_NOTIFICATIONS")

    @staticmethod
    def _parse_notification(data: dict) -> SepsNotification:
        return SepsNotification(
            id=data.get("id"),
            cfNum=_str(data.get("cfNum")),
            date=_str(data.get("date")),
            code=_str(data.get("code")),
            description=_str(data.get("description")),
        )

    def lire_notifications(
        self,
        etab_id: Union[int, str],
        date_debut: Union[str, dt.date],
    ) -> List[SepsNotification]:
        """Changements de signalétique des étudiants d'un établissement depuis une date.

        Le service notifie les modifications des étudiants inscrits dans
        l'établissement survenues depuis ``date_debut`` (comprise) : sexe (02),
        nom / prénom (04), adresse (05), nationalité (06), NISS (07), statut (08).
        Chaque notification se traite en relisant l'étudiant par son CF
        (``lire_etudiant``).

        Args:
            etab_id: Identifiant FASE de l'établissement.
            date_debut: Date pivot, comprise (``date`` ou ``"AAAA-MM-JJ"``).

        Returns:
            Les notifications, dans l'ordre du serveur ; vide quand il n'y en a
            aucune (30105).

        Raises:
            SepsEtnicError: une sous-classe choisie par le code, pour tout autre
                refus (``SepsValidationError`` pour un ``etab_id`` ou une date
                invalide, 30049 / 30050).
        """
        result = self.client_manager.call_service(
            "lireNotifications",
            etabId=str(etab_id),
            dateDebut=date_debut.isoformat() if isinstance(date_debut, dt.date) else date_debut,
        )
        if check_seps_response(result, not_found=_NOT_FOUND_CODES):
            return []
        body = result.get("body") if isinstance(result, dict) else None
        response = body.get("response") if isinstance(body, dict) else None
        raw = response.get("notification") if isinstance(response, dict) else None
        return [self._parse_notification(n) for n in _as_list(raw) if n]
