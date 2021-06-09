# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import os

from setuptools import find_packages, setup

__version__ = '0.13.0'

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements-common.txt')
with open(requirements_path) as requirements_file:
    requirements_common = requirements_file.readlines()

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements-dev.txt')
with open(requirements_path) as requirements_file:
    requirements_dev = requirements_file.readlines()

# avoid circular references
requirements_common = [r for r in requirements_common if not r.startswith('amundsen-common')]

all_deps = requirements_common + requirements_dev

setup(
    name='amundsen-common',
    version=__version__,
    description='Common code library for Amundsen',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/amundsen-io/amundsen/tree/main/common',
    maintainer='Amundsen TSC',
    maintainer_email='amundsen-tsc@lists.lfai.foundation',
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements_common,
    extras_require={
        'all': all_deps,
        'dev': requirements_dev
    },
    python_requires=">=3.6",
    package_data={'amundsen_common': ['py.typed']},
)
