import argparse
import os


def init_config(output_file=".env"):
    contenu_env = """# Environnement : dev (services-web.tq.etnic.be) ou prod (services-web.etnic.be)
ENV=dev

# Identifiants pour le developpement
DEV_USERNAME=
DEV_PASSWORD=

# Identifiants pour la production
PROD_USERNAME=
PROD_PASSWORD=

# Parametres par defaut
# Renseignez ici les identifiants de votre etablissement.
# DEFAULT_ETABID est l'identifiant numerique fourni par ETNIC.
# DEFAULT_IMPLID est l'identifiant d'implantation (optionnel pour certains services).
# DEFAULT_SCHOOLYEAR au format AAAA-AAAA (ex: 2024-2025).
DEFAULT_ETABID=
DEFAULT_IMPLID=
DEFAULT_SCHOOLYEAR=

# Certificat X509 pour les services SEPS (chemin relatif au repertoire courant)
# Le fichier PFX est fourni par ETNIC (IAM-PROD).
# Remarque : le service SEPS n'est disponible qu'en production (ws.etnic.be).
SEPS_PFX_PATH=
SEPS_PFX_PASSWORD=
"""

    if os.path.exists(output_file):
        overwrite = input(f"{output_file} existe deja. Voulez-vous l'ecraser ? (y/n): ")
        if overwrite.lower() != "y":
            print("Operation annulee.")
            return

    # Force UTF-8 so dotenv can always parse generated files reliably.
    with open(output_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu_env)

    print(f"Fichier de configuration cree : {output_file}")
    print("N'oubliez pas de remplir les valeurs manquantes dans le fichier.")


def main():
    parser = argparse.ArgumentParser(description="Outils CLI pour pyetnic.")
    parser.add_argument("command", choices=["init-config"], help="La commande a executer.")
    parser.add_argument("--output", default=".env", help="Nom du fichier de sortie pour la configuration.")

    args = parser.parse_args()

    if args.command == "init-config":
        init_config(args.output)


if __name__ == "__main__":
    main()
