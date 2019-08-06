import os

from setuptools import setup, find_packages

__version__ = '1.1.7'

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='amundsen-search',
    version=__version__,
    description='Search Service for Amundsen',
    url='https://github.com/lyft/amundsensearchlibrary.git',
    maintainer='Lyft',
    maintainer_email='dp-tools@lyft.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=requirements,
    python_requires=">=3.6"
)
