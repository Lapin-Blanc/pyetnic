from setuptools import setup, find_packages

setup(
    name='pyetnic',
    version='0.0.3',
    packages=find_packages(),  # Automatically find packages in the directory
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    package_data={
        'pyetnic': [
            'resources/*',  # Include all files in the resources directory
        ],
    },
    install_requires=[
        'zeep',
        'python-dotenv',
        # Add other dependencies here
    ],
    author='Fabien Toune',
    author_email='fabien.toune@eica.be',
    description='Access to ETNIC web services through Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Lapin-Blanc/pyetnic',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify the minimum Python version
    entry_points={
        'console_scripts': [
            'pyetnic=pyetnic.cli:main',  # Command line interface entry point
        ],
    },
)
