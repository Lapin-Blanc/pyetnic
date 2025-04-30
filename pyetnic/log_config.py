import logging

def configure_logging():
    print("Configuration du logging en cours...")
    # Configuration de base
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Configuration spécifique pour chaque module
    logging.getLogger('pyetnic.services.formations_liste').setLevel(logging.WARNING)
    logging.getLogger('pyetnic.services.organisation').setLevel(logging.WARNING)

    # Vous pouvez ajouter d'autres configurations spécifiques ici