import os
from setuptools import setup, find_packages


__version__ = '1.4.2'


requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='amundsen-databuilder',
    version=__version__,
    description='Amundsen Data builder',
    url='https://www.github.com/lyft/amundsendatabuilder',
    maintainer='Lyft',
    maintainer_email='dev@lyft.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=requirements,
    extras_require={
        ':python_version=="2.7"': ['typing>=3.6'],  # allow typehinting PY2
        'kafka': ['confluent-kafka==1.0.0'],  # To use with Kafka source extractor
    },
)
