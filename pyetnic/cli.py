# pyetnic/cli.py
import argparse

def generate_env_skeleton():
    contenu_env = """    
ENV=dev

# Identifiants pour le développement
DEV_USERNAME=
DEV_PASSWORD=

# Identifiants pour la production
PROD_USERNAME=
PROD_PASSWORD=

# Endpoints pour chaque service en développement
LISTE_FORMATIONS_DEV_ENDPOINT=https://services-web.tq.etnic.be:11443/eprom/formations/liste/v2
ORGANISATION_DEV_ENDPOINT=https://services-web.tq.etnic.be:11443/eprom/organisation/v6
DOCUMENT1_DEV_ENDPOINT=https://services-web.tq.etnic.be:11443/eprom/document1/v1
DOCUMENT2_DEV_ENDPOINT=https://services-web.tq.etnic.be:11443/eprom/document2/v1

# Endpoints pour chaque service en production
LISTE_FORMATIONS_PROD_ENDPOINT=https://services-web.etnic.be:11443/eprom/formations/liste/v2
ORGANISATION_PROD_ENDPOINT=https://services-web.etnic.be:11443/eprom/organisation/v6
DOCUMENT1_PROD_ENDPOINT=https://services-web.etnic.be:11443/eprom/document1/v1
DOCUMENT2_PROD_ENDPOINT=https://services-web.etnic.be:11443/eprom/document2/v1

DEFAULT_ETABID=3052
DEFAULT_IMPLID=6050
DEFAULT_SCHOOLYEAR=2023-2024
    """


    with open(".env.example", "w") as f:
        f.write(contenu_env)

def main():
    parser = argparse.ArgumentParser(description="Outils CLI pour pyetnic.")
    parser.add_argument('command', choices=['generer_env'], help="La commande à exécuter.")
    
    args = parser.parse_args()

    if args.command == 'generer_env':
        generate_env_skeleton()

if __name__ == '__main__':
    main()
