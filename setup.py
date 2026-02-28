from pathlib import Path

from setuptools import setup, find_namespace_packages

README = Path(__file__).with_name('README.md').read_text(encoding='utf-8')

setup(
    name='pyetnic',
    version='0.0.5',
    packages=find_namespace_packages(include=['pyetnic*'], exclude=['tests*']),
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    package_data={
        'pyetnic': [
            'resources/*.wsdl',
            'resources/xsd/*.xsd',
        ],
    },
    install_requires=[
        'zeep',
        'python-dotenv',
        'requests',
        'openpyxl',
    ],
    author='Fabien Toune',
    author_email='fabien.toune@eica.be',
    license='MIT',
    description='Access to ETNIC web services through Python',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Lapin-Blanc/pyetnic',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'pyetnic=pyetnic.cli:main',  # Command line interface entry point
        ],
    },
)
