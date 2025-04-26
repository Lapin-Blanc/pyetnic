from pyetnic.services import lister_formations

result = lister_formations()

if result:
    print(f"Nombre de formations trouvées : {len(result)}")
    for formation in result:
        print(f"Formation: {formation.numAdmFormation} - {formation.libelleFormation} (Code: {formation.codeFormation})")
        if formation.organisations:
            print("  Organisations:")
            for org in formation.organisations:
                print(f"    - orga {org.numOrganisation} du {org.dateDebutOrganisation} au {org.dateFinOrganisation}")
else:
    print("Erreur lors de la récupération des formations:")
    for message in result.messages:
        print(f"  - {message}")