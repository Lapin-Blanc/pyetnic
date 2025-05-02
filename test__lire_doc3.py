from pyetnic.services import lire_document_3, models
from pprint import pprint

# Pour lire un document3
organisation_id = models.OrganisationId(
    anneeScolaire="2024-2025",
    etabId=3052,
    numAdmFormation=499,
    numOrganisation=1
)
document3 = lire_document_3(organisation_id)
pprint(document3)