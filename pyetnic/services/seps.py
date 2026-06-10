"""Service SEPS — Recherche d'étudiants."""

import re
import logging
from typing import List, Optional

from ..soap_client import SoapClientManager, SoapError
from ._helpers import _as_list
from .models import Etudiant, EtudiantDetails, SepsAdresse, SepsLocalite, SepsNaissance, SepsDeces

logger = logging.getLogger(__name__)

_NISS_RE = re.compile(r'[0-9]{6}-?[0-9]{3}-?[0-9]{2}')

# Codes SEPS signifiant « aucun résultat » : ils NE doivent PAS lever
# d'exception — le contrat « non trouvé » se traduit par None / [] côté
# appelant (lireEtudiant : 30110 fin de traitement, 30115 warning).
_NOT_FOUND_CODES = frozenset({"30110", "30115"})


class SepsEtnicError(Exception):
    """Erreur retournée par le serveur ETNIC SEPS (success=False).

    Tous les codes d'erreur SEPS héritent de cette classe, ce qui permet
    de les intercepter globalement si besoin :

        try:
            etudiants = pyetnic.seps.rechercher_etudiants(nom="Dupont")
        except SepsEtnicError as e:
            print(e.code, e.description)
    """

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description
        super().__init__(f"SEPS erreur {code}: {description}")


class SepsAuthError(SepsEtnicError):
    """Échec d'authentification SEPS (code 30550).

    Indique un problème avec le certificat PFX : expiré, non enregistré,
    ou mauvais mot de passe.
    """


class TropDeResultatsError(SepsEtnicError):
    """Le serveur ETNIC a retourné trop de résultats (code 30501).

    Affiner la recherche en ajoutant des critères supplémentaires
    (prenom, date_naissance, sexe…).
    """

    def __init__(self):
        super().__init__("30501", "Trop de résultats — affiner la recherche (prenom, date_naissance, sexe…)")


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

    def __init__(self, ancien_niss: str, nouveau_niss: str):
        self.ancien_niss = ancien_niss
        self.nouveau_niss = nouveau_niss
        super().__init__(
            "30401",
            f"NISS {ancien_niss!r} remplacé par {nouveau_niss!r} — "
            "relancer la recherche avec nouveau_niss",
        )


def _check_seps_errors(result, *, ancien_niss: Optional[str] = None) -> None:
    """Inspecte le bloc retour SEPS et lève une exception typée si success=False.

    Partagé par tous les services SEPS Étudiant (recherche, lecture,
    enregistrement, modification) pour éviter que les erreurs métier soient
    avalées silencieusement (un simple ``return None`` masquerait un certificat
    invalide, une mutation NISS, un doublon…).

    Les codes « aucun résultat » (``_NOT_FOUND_CODES``) sont ignorés : la
    méthode appelante renverra alors None / [] de façon intentionnelle.

    Args:
        result: La réponse SOAP désérialisée (dict avec clé ``body``).
        ancien_niss: Le NISS de la requête, propagé dans ``NissMutationError``.

    Raises:
        NissMutationError: code 30401.
        TropDeResultatsError: code 30501.
        SepsAuthError: code 30550.
        SepsEtnicError: tout autre code métier.
    """
    if not (result and result.get("body")):
        return
    body = result["body"]
    if body.get("success", True):
        return
    errors = (body.get("messages") or {}).get("error") or []
    for err in (errors if isinstance(errors, list) else [errors]):
        code = str(err.get("code"))
        if code in _NOT_FOUND_CODES:
            continue
        desc = err.get("description", "")
        if code == "30401":
            match = _NISS_RE.search(desc)
            raise NissMutationError(ancien_niss or "", match.group(0) if match else "")
        if code == "30501":
            raise TropDeResultatsError()
        if code == "30550":
            raise SepsAuthError(code, desc)
        raise SepsEtnicError(code, desc)


class RechercheEtudiantsService:
    """Client pour le service SEPS RechercheEtudiants v1.

    Authentification par certificat X509 (PFX configuré dans .env via
    SEPS_PFX_PATH et SEPS_PFX_PASSWORD).

    Remarque : le service SEPS n'est disponible qu'en production (ws.etnic.be).
    Le certificat prod n'est pas enregistré dans l'annuaire TQ.
    """

    def __init__(self):
        self.client_manager = SoapClientManager("SEPS_RECHERCHE_ETUDIANTS")

    # ------------------------------------------------------------------
    # Parsers internes
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_localite(d) -> Optional[SepsLocalite]:
        if not d:
            return None
        return SepsLocalite(
            code=d.get("code"),
            description=d.get("description"),
        )

    @staticmethod
    def _parse_adresse(d) -> Optional[SepsAdresse]:
        if not d:
            return None
        return SepsAdresse(
            rue=d.get("rue"),
            codePostal=d.get("codePostal"),
            codePays=d.get("codePays"),
            numero=d.get("numero"),
            boite=d.get("boite"),
            extension=d.get("extension"),
            localite=RechercheEtudiantsService._parse_localite(d.get("localite")),
            localiteExtension=d.get("localiteExtension"),
        )

    @staticmethod
    def _parse_naissance(d) -> Optional[SepsNaissance]:
        if not d:
            return None
        return SepsNaissance(
            date=d.get("date"),
            codePays=d.get("codePays"),
            localite=RechercheEtudiantsService._parse_localite(d.get("localite")),
        )

    @staticmethod
    def _parse_etudiant_details(d) -> Optional[EtudiantDetails]:
        if not d:
            return None
        deces_d = d.get("deces")
        autre_prenom_raw = d.get("autrePrenom")
        return EtudiantDetails(
            niss=d.get("niss"),
            nom=d.get("nom"),
            prenom=d.get("prenom"),
            autrePrenom=_as_list(autre_prenom_raw) or None,
            sexe=d.get("sexe"),
            naissance=RechercheEtudiantsService._parse_naissance(d.get("naissance")),
            deces=SepsDeces(date=deces_d.get("date")) if deces_d else None,
            adresse=RechercheEtudiantsService._parse_adresse(d.get("adresse")),
            codeNationalite=d.get("codeNationalite"),
        )

    @staticmethod
    def _parse_etudiant(et_dict) -> Optional[Etudiant]:
        if not et_dict:
            return None
        return Etudiant(
            cfNum=et_dict.get("cfNum"),
            rnDetails=RechercheEtudiantsService._parse_etudiant_details(et_dict.get("rnDetails")),
            cfwbDetails=RechercheEtudiantsService._parse_etudiant_details(et_dict.get("cfwbDetails")),
        )

    def _parse_lire_etudiant_response(self, result) -> Optional[Etudiant]:
        _check_seps_errors(result)
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
            and result["body"]["response"].get("etudiant")
        ):
            return None
        return self._parse_etudiant(result["body"]["response"]["etudiant"])

    def _parse_rechercher_etudiants_response(self, result, ancien_niss: Optional[str] = None) -> List[Etudiant]:
        _check_seps_errors(result, ancien_niss=ancien_niss)
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
        ):
            return []
        # zeep peut retourner un seul dict ou une liste selon le nombre de résultats
        etudiants_raw = _as_list(result["body"]["response"].get("etudiant"))
        return [self._parse_etudiant(e) for e in etudiants_raw if e]

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def lire_etudiant(self, cf_num: str, from_date: Optional[str] = None) -> Optional[Etudiant]:
        """Lit les données d'un étudiant par son numéro CF.

        Args:
            cf_num: Numéro CF de l'étudiant (format : [0-9]{1,10}-[0-9]{2})
            from_date: Date à partir de laquelle récupérer les données (optionnel, format YYYY-MM-DD)

        Returns:
            Etudiant ou None si non trouvé.
        """
        kwargs = {"cfNum": cf_num}
        if from_date is not None:
            kwargs["fromDate"] = from_date
        result = self.client_manager.call_service("lireEtudiant", **kwargs)
        return self._parse_lire_etudiant_response(result)

    def rechercher_etudiants(
        self,
        niss: Optional[str] = None,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        date_naissance: Optional[str] = None,
        sexe: Optional[str] = None,
        force_rn_flag: Optional[bool] = None,
    ) -> List[Etudiant]:
        """Recherche des étudiants par NISS ou par nom/prénom.

        Exactement un des deux groupes doit être fourni :
        - Par NISS : fournir ``niss``
        - Par identité : fournir ``nom`` (+ optionnellement ``prenom``,
          ``date_naissance``, ``sexe``, ``force_rn_flag``)

        Args:
            niss: Numéro de registre national (format : YYMMDD-XXX-YY)
            nom: Nom de famille (obligatoire si pas de niss)
            prenom: Prénom (optionnel)
            date_naissance: Date ou année de naissance (format YYYY ou YYYY-MM-DD)
            sexe: Sexe (M, F ou X)
            force_rn_flag: Forcer la recherche dans le registre national (optionnel)

        Returns:
            Liste d'étudiants correspondant aux critères.

        Raises:
            ValueError: Si ni niss ni nom n'est fourni.
        """
        if niss:
            kwargs = {"niss": niss}
        elif nom:
            kwargs = {"nom": nom}
            if prenom is not None:
                kwargs["prenom"] = prenom
            if date_naissance is not None:
                kwargs["dateNaissance"] = date_naissance
            if sexe is not None:
                kwargs["sexe"] = sexe
            if force_rn_flag is not None:
                kwargs["forceRnFlag"] = force_rn_flag
        else:
            raise ValueError("Vous devez fournir soit niss, soit nom")

        result = self.client_manager.call_service("rechercherEtudiants", **kwargs)
        return self._parse_rechercher_etudiants_response(result, ancien_niss=niss)
