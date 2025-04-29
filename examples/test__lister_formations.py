import pprint
from pyetnic.services import lister_formations, lire_organisation
from pyetnic.services.models import Organisation, OrganisationId
from pyetnic.config import Config
from dataclasses import fields

Config.ANNEE_SCOLAIRE = "2024-2025"

result = lister_formations(annee_scolaire=Config.ANNEE_SCOLAIRE, etab_id=Config.ETAB_ID, impl_id=Config.IMPL_ID)

if result:
    print(f"Nombre de formations trouvées : {len(result)}")
    for formation in result:
        print(f"Formation: {formation.numAdmFormation} - {formation.libelleFormation} (Code: {formation.codeFormation})")
        if formation.organisations:
            print("  Organisations:")
            for org in formation.organisations:
                org_id = OrganisationId(anneeScolaire=Config.ANNEE_SCOLAIRE,
                                        etabId=Config.ETAB_ID, 
                                        numAdmFormation=formation.numAdmFormation, 
                                        numOrganisation=org.id.numOrganisation,) 
                orga_full = lire_organisation(org_id)
                for field in fields(Organisation):
                    setattr(org, field.name, getattr(orga_full, field.name))
                print(f"    - orga {org.id.numOrganisation} du {org.dateDebutOrganisation} au {org.dateFinOrganisation}")
                
else:
    print("Erreur lors de la récupération des formations:")
    for message in result.messages:
        print(f"  - {message}")