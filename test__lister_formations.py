import pprint
from pyetnic.services import lister_formations, lire_organisation
from pyetnic.services.models import OrganisationId
from pyetnic.config import Config


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
                orga = lire_organisation(org_id)
                print(f"    - orga {orga.id.numOrganisation} du {orga.dateDebutOrganisation} au {orga.dateFinOrganisation}")
                
else:
    print("Erreur lors de la récupération des formations:")
    for message in result.messages:
        print(f"  - {message}")