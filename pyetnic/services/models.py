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
    statut: Optional[str] = None
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