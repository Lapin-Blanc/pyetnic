from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

@dataclass
class StatutDocument:
    statut: str
    dateStatut: date

@dataclass
class OrganisationId:
    anneeScolaire: str
    etabId: int
    numAdmFormation: int
    numOrganisation: int

@dataclass
class Organisation:
    dateDebutOrganisation: date
    dateFinOrganisation: date
    id: OrganisationId = field(default_factory=OrganisationId)
    nombreSemaineFormation: Optional[int] = None
    organisationPeriodesSupplOuEPT: Optional[bool] = None
    valorisationAcquis: Optional[bool] = None
    enPrison: Optional[bool] = None
    activiteFormation: Optional[str] = None
    conseillerPrevention: Optional[bool] = None
    partiellementDistance: Optional[bool] = None
    enseignementHybride: Optional[bool] = None
    numOrganisation2AnneesScolaires: Optional[int] = None
    typeInterventionExterieure: Optional[str] = None
    interventionExterieure50p: Optional[bool] = None
    statutDocumentOrganisation: Optional[StatutDocument] = None
    statutDocumentPopulationPeriodes: Optional[StatutDocument] = None
    statutDocumentDroitsInscription: Optional[StatutDocument] = None
    statutDocumentAttributions: Optional[StatutDocument] = None

@dataclass
class Formation:
    numAdmFormation: int
    libelleFormation: str
    codeFormation: str
    organisations: List[Organisation] = field(default_factory=list)

@dataclass
class FormationsListeResult:
    success: bool
    formations: List[Formation]
    messages: List[str] = field(default_factory=list)

    def __bool__(self):
        return self.success

    def __iter__(self):
        return iter(self.formations)

    def __len__(self):
        return len(self.formations)

@dataclass
class Doc2ActiviteEnseignementLine:
    """Ligne d'activité d'enseignement pour le document 2."""
    coNumBranche: int
    coCategorie: str
    teNomBranche: str
    coAnnEtude: str
    nbEleveC1: int
    nbPeriodeBranche: float
    nbPeriodePrevueAn1: float
    nbPeriodePrevueAn2: float
    nbPeriodeReelleAn1: float
    nbPeriodeReelleAn2: float
    coAdmReg: int = 0
    coOrgReg: int = 0
    coBraReg: int = 0
    coEtuReg: Optional[str] = None

@dataclass
class Doc2ActiviteEnseignementList:
    """Liste d'activités d'enseignement pour le document 2."""
    activiteEnseignement: List[Doc2ActiviteEnseignementLine] = field(default_factory=list)

@dataclass
class Doc2ActiviteEnseignementDetail:
    """Détail des activités d'enseignement pour le document 2."""
    activiteEnseignementListe: Optional[Doc2ActiviteEnseignementList] = None
    nbTotPeriodePrevueAn1: float = 0.0
    nbTotPeriodePrevueAn2: float = 0.0
    nbTotPeriodeReelleAn1: float = 0.0
    nbTotPeriodeReelleAn2: float = 0.0

@dataclass
class Doc2PeriodeExtLine:
    """Période pour intervention extérieure."""
    coCodePar: str
    teLibPeriode: str
    nbPerAn1: float
    nbPerAn2: float

@dataclass
class Doc2PeriodeExtList:
    """Liste de périodes pour intervention extérieure."""
    periode: List[Doc2PeriodeExtLine] = field(default_factory=list)

@dataclass
class Doc2InterventionExtLine:
    """Ligne d'intervention extérieure pour le document 2."""
    coNumIex: int
    coCatCol: str
    teTypeInterventionExt: str
    coObjFse: str
    teSousTypeInterventionExt: str
    coRefPro: str
    coCriCee: str
    periodeListe: Optional[Doc2PeriodeExtList] = None

@dataclass
class Doc2InterventionExtList:
    """Liste d'interventions extérieures pour le document 2."""
    interventionExterieure: List[Doc2InterventionExtLine] = field(default_factory=list)

@dataclass
class FormationDocument2:
    """Représente un document 2 (périodes de formation)."""
    id: OrganisationId
    activiteEnseignementDetail: Optional[Doc2ActiviteEnseignementDetail] = None
    interventionExterieureListe: Optional[Doc2InterventionExtList] = None
    swAppD2: bool = False
    tsMaj: Optional[str] = None
    teUserMaj: Optional[str] = None