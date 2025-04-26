from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import date

@dataclass
class Organisation:
    implId: int
    numOrganisation: int
    dateDebutOrganisation: date
    dateFinOrganisation: date
    statutDocumentOrganisation: Dict[str, Any]
    statutDocumentPopulationPeriodes: Optional[Dict[str, Any]]
    statutDocumentDroitsInscription: Optional[Dict[str, Any]]
    statutDocumentAttributions: Optional[Dict[str, Any]]

@dataclass
class Formation:
    numAdmFormation: int
    libelleFormation: str
    codeFormation: str
    organisations: List[Organisation]

class FormationsListeResult:
    def __init__(self, success: bool, formations: List[Formation], messages: Optional[List[str]] = None):
        self.success = success
        self.formations = formations
        self.messages = messages or []

    def __bool__(self):
        return self.success

    def __iter__(self):
        return iter(self.formations)

    def __len__(self):
        return len(self.formations)