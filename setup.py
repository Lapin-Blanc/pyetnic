from setuptools import setup, find_packages

setup(
    name='pyetnic',
    version='0.0.3',
    packages=find_packages(),  # Détecte automatiquement tous les packages à inclure
    include_package_data=True,  # Inclut les données non-code spécifiées dans MANIFEST.in
    package_data={
        'pyetnic': [
            'resources/*',
        ],
    },
    install_requires=[
        # Liste des dépendances nécessaires à installer
        'zeep',
        'python-dotenv',
    ],
    author='Fabien Toune',
    author_email='fabien.toune@eica.be',
    description='Access to ETNIC web services through Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Lapin-Blanc/pyetnic',
)
