# -*- coding: utf-8 -*-
# pyetnic/cli.py
import argparse
import os

def init_config(output_file='.env'):
    contenu_env = """# Environnement : dev (services-web.tq.etnic.be) ou prod (services-web.etnic.be)
ENV=dev

# Identifiants pour le développement
DEV_USERNAME=
DEV_PASSWORD=

# Identifiants pour la production
PROD_USERNAME=
PROD_PASSWORD=

# Paramètres par défaut
DEFAULT_ETABID=3052
DEFAULT_IMPLID=6050
DEFAULT_SCHOOLYEAR=2023-2024
"""

    if os.path.exists(output_file):
        overwrite = input(f"{output_file} existe déjà. Voulez-vous l'écraser ? (y/n): ")
        if overwrite.lower() != 'y':
            print("Opération annulée.")
            return

    with open(output_file, "w") as f:
        f.write(contenu_env)
    
    print(f"Fichier de configuration créé : {output_file}")
    print("N'oubliez pas de remplir les valeurs manquantes dans le fichier.")

def main():
    parser = argparse.ArgumentParser(description="Outils CLI pour pyetnic.")
    parser.add_argument('command', choices=['init-config'], help="La commande à exécuter.")
    parser.add_argument('--output', default='.env', help="Nom du fichier de sortie pour la configuration.")
    
    args = parser.parse_args()

    if args.command == 'init-config':
        init_config(args.output)

if __name__ == '__main__':
    main()
