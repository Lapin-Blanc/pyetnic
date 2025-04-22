"""
Script de test pour la bibliothèque pyetnic.
"""
import sys
import os

# Add the root directory of the project to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import json
from pprint import pprint

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import direct depuis le package principal
import pyetnic
from pyetnic.config import Config

def test_config():
    """Teste la configuration."""
    print("\n=== Test de la configuration ===")
    print(f"Version: {pyetnic.__version__}")
    print(f"Auteur: {pyetnic.__author__}")
    print(f"Environnement: {Config.ENV}")
    print(f"Année scolaire par défaut: {Config.ANNEE_SCOLAIRE}")
    print(f"Validation de la configuration: {'OK' if Config.validate() else 'NON OK'}")

def test_formations_liste():
    """Teste le service de liste des formations."""
    print("\n=== Test du service liste des formations ===")
    try:
        # Utilisation de l'API publique
        print("Test de lister_formations_organisables:")
        formations = pyetnic.lister_formations_organisables()
        
        # On affiche juste le nombre de formations pour éviter une sortie trop verbeuse
        if 'body' in formations and 'response' in formations['body']:
            formations_list = formations['body']['response'].get('formation', [])
            count = len(formations_list)
            print(f"Nombre de formations organisables: {count}")
            
            # Affichage des 3 premières formations si elles existent
            if count > 0:
                print("\nExemples de formations:")
                for i, formation in enumerate(formations_list[:3]):
                    print(f"{i+1}. {formation.get('libelleFormation')} (Code: {formation.get('codeFormation')})")
        
        # Test de lister_formations (avec organisations)
        print("\nTest de lister_formations:")
        formations_org = pyetnic.lister_formations()
        
        if 'body' in formations_org and 'response' in formations_org['body']:
            formations_with_org = formations_org['body']['response'].get('formation', [])
            count_with_org = len(formations_with_org)
            print(f"Nombre de formations avec organisations: {count_with_org}")
            
            # Affichage d'un exemple de formation avec organisation
            if count_with_org > 0 and 'organisation' in formations_with_org[0]:
                formation = formations_with_org[0]
                print(f"\nDétail d'une formation avec organisation:")
                print(f"Formation: {formation.get('libelleFormation')}")
                orgs = formation.get('organisation', [])
                if isinstance(orgs, list):
                    print(f"Nombre d'organisations: {len(orgs)}")
                    if len(orgs) > 0:
                        org = orgs[0]
                        print(f"  - Organisation #{org.get('numOrganisation')}")
                        print(f"    Date début: {org.get('dateDebutOrganisation')}")
                        print(f"    Date fin: {org.get('dateFinOrganisation')}")
    
    except Exception as e:
        print(f"Erreur lors du test: {e}")

def main():
    """Fonction principale."""
    print("=== Tests de la bibliothèque pyetnic ===")
    
    # Test de la configuration
    test_config()
    
    # Test du service de liste des formations
    test_formations_liste()
    
    print("\n=== Fin des tests ===")

if __name__ == "__main__":
    main()