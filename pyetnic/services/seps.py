"""Service SEPS — Recherche d'étudiants."""

import logging
from typing import List, Optional

from ..soap_client import SoapClientManager, SoapError
from .models import Etudiant, EtudiantDetails, SepsAdresse, SepsLocalite, SepsNaissance, SepsDeces

logger = logging.getLogger(__name__)


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
            autrePrenom=list(autre_prenom_raw) if autre_prenom_raw else None,
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
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
            and result["body"]["response"].get("etudiant")
        ):
            return None
        return self._parse_etudiant(result["body"]["response"]["etudiant"])

    def _parse_rechercher_etudiants_response(self, result) -> List[Etudiant]:
        if not (
            result
            and result.get("body")
            and result["body"].get("response")
        ):
            return []
        etudiants_raw = result["body"]["response"].get("etudiant") or []
        # zeep peut retourner un seul dict ou une liste selon le nombre de résultats
        if isinstance(etudiants_raw, dict):
            etudiants_raw = [etudiants_raw]
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
        return self._parse_rechercher_etudiants_response(result)
