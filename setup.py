"""The setup script."""

from setuptools import setup, find_packages
from requirements import *

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    author="Storm Development",
    author_email='playerstars@stormsec.com.br',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Portuguese',
        'Programming Language :: Python :: 3.7',
    ],
    description="Camada de interactors (ou os use cases, segundo o modelo do "
                "Uncle Bob) do projeto PlayerStars",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='playerstars_interactors',
    name='playerstars_interactors',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/stormsecurity/internos/playerstars/'
        'playerstars-interactors.git',
    version='1.0.1',
    zip_safe=False,
)
