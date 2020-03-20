import os

from setuptools import setup, find_packages

__version__ = '2.3.0'


requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='amundsen-metadata',
    version=__version__,
    description='Metadata service for Amundsen',
    url='https://www.github.com/lyft/amundsenmetadatalibrary',
    maintainer='Lyft',
    maintainer_email='dev@lyft.com',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    zip_safe=False,
    dependency_links=[],
    install_requires=requirements,
    extras_require={
        'oidc': ['flaskoidc==0.0.2']
    },
    python_requires=">=3.6"
)
