"""Namespace public pour les services EPROM (Enseignement de Promotion Sociale)."""

# Exceptions — hiérarchie typée (voir pyetnic.exceptions)
from ..exceptions import (
    EtnicError,
    EtnicTransportError,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    EtnicValidationError,
)
from ..error_mode import strict_errors
from ..soap_client import SoapError  # legacy alias for EtnicTransportError

# Fonctions de service — singletons gérés dans services/
from ..services import (
    lister_formations,
    lister_formations_organisables,
    lire_organisation,
    creer_organisation,
    modifier_organisation,
    supprimer_organisation,
    lire_document_1,
    modifier_document_1,
    approuver_document_1,
    lire_document_2,
    modifier_document_2,
    lire_document_3,
    modifier_document_3,
    TYPES_INTERVENTION_EXTERIEURE,
)

# Nomenclatures — typed Enums (H9)
from ..nomenclatures import (
    TypeInterventionExterieure,
    CodeAdmission,
    CodeSanction,
    MotifAbandon,
    DureeInoccupation,
    SituationMenage,
)

# Modèles — types communs
from ..services.models import (
    StatutDocument,
    OrganisationId,
    OrganisationApercu,
    Organisation,
    Formation,
    FormationsListeResult,
)

# Modèles — Document 1
from ..services.models import (
    Doc1PopulationLine,
    Doc1PopulationList,
    Doc1PopulationLineSave,
    Doc1PopulationListSave,
    FormationDocument1,
)

# Modèles — Document 2
from ..services.models import (
    Doc2ActiviteEnseignementLine,
    Doc2ActiviteEnseignementList,
    Doc2ActiviteEnseignementDetail,
    Doc2PeriodeExtLine,
    Doc2PeriodeExtList,
    Doc2InterventionExtLine,
    Doc2InterventionExtList,
    Doc2ActiviteEnseignementLineSave,
    Doc2ActiviteEnseignementListSave,
    Doc2PeriodeExtLineSave,
    Doc2PeriodeExtListSave,
    Doc2InterventionExtLineSave,
    Doc2InterventionExtListSave,
    FormationDocument2,
)

# Modèles — Document 3
from ..services.models import (
    Doc3EnseignantDetail,
    Doc3EnseignantList,
    Doc3ActiviteDetail,
    Doc3ActiviteListe,
    Doc3EnseignantDetailSave,
    Doc3EnseignantListSave,
    Doc3ActiviteDetailSave,
    Doc3ActiviteListeSave,
    FormationDocument3,
)

__all__ = [
    # Exceptions
    "EtnicError",
    "EtnicTransportError",
    "EtnicBusinessError",
    "EtnicDocumentNotAccessibleError",
    "EtnicNotFoundError",
    "EtnicValidationError",
    "SoapError",
    "strict_errors",
    # Fonctions
    "lister_formations",
    "lister_formations_organisables",
    "lire_organisation",
    "creer_organisation",
    "modifier_organisation",
    "supprimer_organisation",
    "lire_document_1",
    "modifier_document_1",
    "approuver_document_1",
    "lire_document_2",
    "modifier_document_2",
    "lire_document_3",
    "modifier_document_3",
    "TYPES_INTERVENTION_EXTERIEURE",
    # Nomenclatures
    "TypeInterventionExterieure",
    "CodeAdmission",
    "CodeSanction",
    "MotifAbandon",
    "DureeInoccupation",
    "SituationMenage",
    # Modèles communs
    "StatutDocument",
    "OrganisationId",
    "OrganisationApercu",
    "Organisation",
    "Formation",
    "FormationsListeResult",
    # Document 1
    "Doc1PopulationLine",
    "Doc1PopulationList",
    "Doc1PopulationLineSave",
    "Doc1PopulationListSave",
    "FormationDocument1",
    # Document 2
    "Doc2ActiviteEnseignementLine",
    "Doc2ActiviteEnseignementList",
    "Doc2ActiviteEnseignementDetail",
    "Doc2PeriodeExtLine",
    "Doc2PeriodeExtList",
    "Doc2InterventionExtLine",
    "Doc2InterventionExtList",
    "Doc2ActiviteEnseignementLineSave",
    "Doc2ActiviteEnseignementListSave",
    "Doc2PeriodeExtLineSave",
    "Doc2PeriodeExtListSave",
    "Doc2InterventionExtLineSave",
    "Doc2InterventionExtListSave",
    "FormationDocument2",
    # Document 3
    "Doc3EnseignantDetail",
    "Doc3EnseignantList",
    "Doc3ActiviteDetail",
    "Doc3ActiviteListe",
    "Doc3EnseignantDetailSave",
    "Doc3EnseignantListSave",
    "Doc3ActiviteDetailSave",
    "Doc3ActiviteListeSave",
    "FormationDocument3",
]
