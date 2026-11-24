"""SEPS refusals: one exception hierarchy and one response check for every SEPS service.

Every SEPS operation answers with ``success`` and ``messages`` (``error``,
``warning``, ``info``). A refusal is ``success=false``, **whether its code comes
as an error or as a warning**: production answered ``enregistrerInscription``
with ``success=false`` and only the warning ``30101`` (2026-11-10), which a check
of ``messages.error`` alone turned into a silent ``None``.

SEPS always raises on a refusal; there is no permissive mode as for EPROM. A read
that finds nothing returns an empty result instead, through the "nothing found"
codes each operation declares.

The hierarchy joins the EPROM one: ``SepsEtnicError`` derives from
:class:`~pyetnic.exceptions.EtnicBusinessError`, and the SEPS validation and
not-found errors also derive from :class:`~pyetnic.exceptions.EtnicValidationError`
and :class:`~pyetnic.exceptions.EtnicNotFoundError`. Classes follow the error
labels of the ETNIC user manuals (Enregistrer Étudiants 2.3, Enregistrer and
Recherche Inscriptions 2.4, June 2026).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Type

from ..exceptions import EtnicBusinessError, EtnicNotFoundError, EtnicValidationError, extract_error_info
from .models import SepsMessage

logger = logging.getLogger(__name__)

_NISS_RE = re.compile(r"(?<!\d)[0-9]{6}-?[0-9]{3}-?[0-9]{2}(?!\d)")
# A CF number, not a fragment of a dashed NISS. The manual's 30203 example lists
# numbers with a single check digit ("8502637-5"), hence {1,2}.
_CF_RE = re.compile(r"(?<![\d-])[0-9]{1,10}-[0-9]{1,2}(?![\d-])")
# The service version comes back as an info message ("2.4.6", "version").
_VERSION_CODE_RE = re.compile(r"^\d+\.\d+(\.\d+)*$")
# Codes reporting a success when ``success`` is nevertheless false (the manual's
# modifierEtudiant example answers success=false with info 200).
_SUCCESS_CODES = frozenset({"200", "201"})


class SepsEtnicError(EtnicBusinessError):
    """Erreur retournée par le serveur ETNIC SEPS (success=False).

    Tous les codes d'erreur SEPS héritent de cette classe, ce qui permet
    de les intercepter globalement si besoin :

        try:
            etudiants = pyetnic.seps.rechercher_etudiants(nom="Dupont")
        except SepsEtnicError as e:
            print(e.code, e.description)

    ``except EtnicBusinessError`` intercepte aussi les erreurs SEPS.
    """

    def __init__(self, code: Optional[str], description: str, *, request_id: Optional[str] = None):
        super().__init__(
            f"SEPS erreur {code}: {description}",
            code=code,
            description=description,
            request_id=request_id,
        )


class SepsAuthError(SepsEtnicError):
    """Échec d'authentification SEPS (code 30550).

    Indique un problème avec le certificat PFX : expiré, non enregistré,
    ou mauvais mot de passe.
    """


class TropDeResultatsError(SepsEtnicError):
    """Le serveur ETNIC a retourné trop de résultats (codes 30501, 30503).

    Affiner la recherche en ajoutant des critères supplémentaires
    (prenom, date_naissance, sexe…).
    """

    def __init__(
        self,
        code: str = "30501",
        description: str = "Trop de résultats : affiner la recherche (prenom, date_naissance, sexe…)",
        *,
        request_id: Optional[str] = None,
    ):
        super().__init__(code, description, request_id=request_id)


class NissMutationError(SepsEtnicError):
    """Le NISS fourni a été remplacé par un nouveau NISS (code ETNIC 30401).

    Se produit quand un numéro BIS a été remplacé par un vrai numéro de
    Registre National, ou lors d'autres fusions de dossiers à la BCSS.

    Relancer la recherche avec ``nouveau_niss`` :

        try:
            etudiants = pyetnic.seps.rechercher_etudiants(niss="...")
        except NissMutationError as e:
            etudiants = pyetnic.seps.rechercher_etudiants(niss=e.nouveau_niss)
    """

    def __init__(self, ancien_niss: str, nouveau_niss: str, *, request_id: Optional[str] = None):
        self.ancien_niss = ancien_niss
        self.nouveau_niss = nouveau_niss
        super().__init__(
            "30401",
            f"NISS {ancien_niss!r} remplacé par {nouveau_niss!r} : "
            "relancer la recherche avec nouveau_niss",
            request_id=request_id,
        )


class SepsValidationError(SepsEtnicError, EtnicValidationError):
    """Requête refusée pour son contenu (codes BAD_REQUEST du manuel).

    Champ manquant ou invalide, combinaison interdite, règle métier
    (élève de moins de 15 ans, ``regulier1`` verrouillé après le 1/10…).
    """


class SepsNotFoundError(SepsEtnicError, EtnicNotFoundError):
    """Ce que la requête désigne n'existe pas (codes NOT_FOUND du manuel).

    Une lecture qui ne trouve rien rend un résultat vide et ne lève pas :
    cette erreur concerne les écritures, ou une lecture sur un code qu'elle
    ne déclare pas comme « aucun résultat ».
    """


class SepsUeInconnueError(SepsNotFoundError):
    """SEPS ne connaît pas l'UE (codes 30100, 30101).

    Observé en production quand l'inscription suit de quelques minutes la
    déclaration de l'organisation dans EPROM : SEPS reçoit les organisations
    avec un délai. Ce n'est pas un refus lié au statut du Doc A.
    """


class SepsEtudiantInconnuError(SepsNotFoundError):
    """Aucun étudiant pour ce CF (30011) ou pour ce NISS au Registre national (30120)."""


class SepsConflictError(SepsEtnicError):
    """La requête entre en conflit avec une donnée existante (codes CONFLICT du manuel)."""


class SepsInscriptionExisteError(SepsConflictError):
    """L'étudiant est déjà inscrit à cette UE (code 30200)."""


class SepsEtudiantExisteError(SepsConflictError):
    """L'étudiant existe déjà dans SEPS (code 30201).

    Attributes:
        cf_num: Le numéro CF de l'étudiant existant, lu dans la description
            (``None`` si le serveur ne l'y met pas).
    """

    def __init__(self, code: str, description: str, *, request_id: Optional[str] = None):
        cfs = _CF_RE.findall(description or "")
        self.cf_num: Optional[str] = cfs[0] if cfs else None
        super().__init__(code, description, request_id=request_id)


class SepsDoublonsError(SepsConflictError):
    """Doublons possibles : plusieurs fiches correspondent (codes 30202, 30203, 30204).

    Attributes:
        cf_nums: Les numéros CF lus dans la description (30202, 30203).
        niss: Les NISS lus dans la description (30204, recherche au
            Registre national).
    """

    def __init__(self, code: str, description: str, *, request_id: Optional[str] = None):
        self.niss: List[str] = _NISS_RE.findall(description or "")
        self.cf_nums: List[str] = _CF_RE.findall(_NISS_RE.sub(" ", description or ""))
        super().__init__(code, description, request_id=request_id)


class SepsAucuneModificationError(SepsEtnicError):
    """Le serveur n'a rien modifié : les données envoyées sont déjà enregistrées (code 30443)."""


def _codes(*items: Any) -> frozenset:
    codes: set = set()
    for item in items:
        if isinstance(item, range):
            codes.update(str(c) for c in item)
        else:
            codes.add(str(item))
    return frozenset(codes)


_VALIDATION_CODES = _codes(
    30010, range(30012, 30038), range(30039, 30043), 30049, 30050, 30052, range(30060, 30081)
)

_CODE_CLASSES: Dict[str, Type[SepsEtnicError]] = {
    "30550": SepsAuthError,
    "30100": SepsUeInconnueError,
    "30101": SepsUeInconnueError,
    "30011": SepsEtudiantInconnuError,
    "30120": SepsEtudiantInconnuError,
    "30102": SepsNotFoundError,
    "30103": SepsNotFoundError,
    "30105": SepsNotFoundError,
    "30110": SepsNotFoundError,
    "30115": SepsNotFoundError,
    "30200": SepsInscriptionExisteError,
    "30201": SepsEtudiantExisteError,
    "30202": SepsDoublonsError,
    "30203": SepsDoublonsError,
    "30204": SepsDoublonsError,
    "30443": SepsAucuneModificationError,
}


def _message_list(messages: Any, kind: str) -> List[Dict[str, Any]]:
    entries = (messages or {}).get(kind) if isinstance(messages, dict) else None
    if not entries:
        return []
    return [e for e in (entries if isinstance(entries, list) else [entries]) if isinstance(e, dict)]


def _is_version(message: Dict[str, Any]) -> bool:
    return bool(_VERSION_CODE_RE.match(str(message.get("code") or "")))


def seps_messages(result: Any) -> List[SepsMessage]:
    """Every message of a SEPS answer, errors first, the service version excluded."""
    if not (isinstance(result, dict) and isinstance(result.get("body"), dict)):
        return []
    messages = result["body"].get("messages")
    found: List[SepsMessage] = []
    for niveau in ("error", "warning", "info"):
        for message in _message_list(messages, niveau):
            if _is_version(message):
                continue
            code = message.get("code")
            found.append(SepsMessage(niveau, str(code) if code is not None else None, message.get("description")))
    return found


def primary_code(messages: List[SepsMessage]) -> Optional[str]:
    """The code that sums up an accepted write: 201 / 200 if present, else the first info, else the first code."""
    for message in messages:
        if message.code in _SUCCESS_CODES:
            return message.code
    for message in messages:
        if message.niveau == "info" and message.code:
            return message.code
    return next((m.code for m in messages if m.code), None)


def seps_response(result: Any, key: str) -> Optional[Dict[str, Any]]:
    """``body.response.<key>`` of a SEPS answer, or ``None``."""
    body = result.get("body") if isinstance(result, dict) else None
    response = body.get("response") if isinstance(body, dict) else None
    value = response.get(key) if isinstance(response, dict) else None
    return value or None


def seps_error(
    code: Optional[str],
    description: str,
    *,
    request_id: Optional[str] = None,
    ancien_niss: Optional[str] = None,
) -> SepsEtnicError:
    """The typed exception for one SEPS code (not raised)."""
    if code == "30401":
        match = _NISS_RE.search(description or "")
        return NissMutationError(ancien_niss or "", match.group(0) if match else "", request_id=request_id)
    if code in ("30501", "30503"):
        return TropDeResultatsError(code, description, request_id=request_id)
    cls = _CODE_CLASSES.get(code or "")
    if cls is None:
        cls = SepsValidationError if code in _VALIDATION_CODES else SepsEtnicError
    return cls(code, description, request_id=request_id)


def check_seps_response(
    result: Any,
    *,
    not_found: frozenset = frozenset(),
    ancien_niss: Optional[str] = None,
) -> bool:
    """Inspect a SEPS answer: raise on a refusal, tell the caller when nothing was found.

    Args:
        result: The deserialized SOAP answer (dict with a ``body`` key).
        not_found: The codes that mean "nothing found" for this operation: the
            caller then returns ``None`` / ``[]`` instead of raising.
        ancien_niss: The NISS of the request, carried by ``NissMutationError``.

    Returns:
        ``True`` when the server answered one of the ``not_found`` codes,
        ``False`` otherwise (success).

    Raises:
        SepsEtnicError: a subclass chosen by the code, for any refusal
            (``success=false``) carried by an error or a warning message.
    """
    if not (isinstance(result, dict) and isinstance(result.get("body"), dict)):
        return False
    body = result["body"]
    messages = body.get("messages")
    errors = _message_list(messages, "error")
    warnings = [m for m in _message_list(messages, "warning") if not _is_version(m)]
    infos = [m for m in _message_list(messages, "info") if not _is_version(m)]

    if body.get("success", True):
        for message in errors + warnings:
            logger.warning("SEPS: %s %s", message.get("code"), message.get("description"))
        return False

    refusals = errors + warnings
    blocking = [m for m in refusals if str(m.get("code")) not in not_found]
    if refusals and not blocking:
        return True
    if not refusals and any(str(m.get("code")) in _SUCCESS_CODES for m in infos):
        return False

    _, _, request_id = extract_error_info(result)
    first = (blocking or infos or [{}])[0]
    code = str(first["code"]) if first.get("code") is not None else None
    description = first.get("description") or "success=false sans message"
    raise seps_error(code, description, request_id=request_id, ancien_niss=ancien_niss)
