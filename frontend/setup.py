# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import subprocess

from setuptools import setup, find_packages

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, 'amundsen_application', 'static')


def is_npm_installed() -> bool:
    try:
        subprocess.check_call(['npm --version'], shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def build_js() -> None:
    if not is_npm_installed():
        logging.error('npm must be available')

    try:
        subprocess.check_call(['npm install'], cwd=PACKAGE_DIR, shell=True)
        subprocess.check_call(['npm run build'], cwd=PACKAGE_DIR, shell=True)
    except Exception as e:
        logging.warn('Installation of npm dependencies failed')
        logging.warn(str(e))


build_js()

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

__version__ = '3.4.0'


setup(
    name='amundsen-frontend',
    version=__version__,
    description='Web UI for Amundsen',
    url='https://www.github.com/lyft/amundsenfrontendlibrary',
    maintainer='Lyft',
    maintainer_email='amundsen-dev@lyft.com',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    dependency_links=[],
    setup_requires=['cython >= 0.29'],
    install_requires=requirements,
    extras_require={
        'oidc': ['flaskoidc==0.1.1'],
        'pyarrow': ['pyarrow==3.0.0'],
    },
    python_requires=">=3.6",
    entry_points="""
        [action_log.post_exec.plugin]
        logging_action_log=amundsen_application.log.action_log_callback:logging_action_log
    """,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
