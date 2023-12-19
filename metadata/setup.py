# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import os

from setuptools import find_packages, setup

__version__ = '3.12.3'

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements-common.txt')
with open(requirements_path) as requirements_file:
    requirements_common = requirements_file.readlines()

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements-dev.txt')
with open(requirements_path) as requirements_file:
    requirements_dev = requirements_file.readlines()

oidc = ['flaskoidc>=1.0.0']
atlas = ['apache-atlas==0.0.11']
rds = ['amundsen-rds==0.0.8',
       'mysqlclient>=1.3.6,<3']
gremlin = [
    'amundsen-gremlin>=0.0.9',
    'gremlinpython==3.4.3',
    'gremlinpython==3.4.3'
]
all_deps = requirements + requirements_common + requirements_dev + oidc + atlas + rds + gremlin

setup(
    name='amundsen-metadata',
    version=__version__,
    description='Metadata service for Amundsen',
    url='https://www.github.com/amundsen-io/amundsen/tree/main/metadata',
    maintainer='Amundsen TSC',
    maintainer_email='amundsen-tsc@lists.lfai.foundation',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements + requirements_common,
    extras_require={
        'all': all_deps,
        'dev': requirements_dev,
        'atlas': atlas,
        'oidc': oidc,
        'rds': rds,
        'gremlin': gremlin
    },
    python_requires=">=3.7",
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)
