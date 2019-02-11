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
    except Exception as e:
        return False


def build_js() -> None:
    if not is_npm_installed():
        logging.error('npm must be available')

    try:
        subprocess.check_call(['npm install --only=prod'], cwd=PACKAGE_DIR, shell=True)
    except Exception as e:
        logging.warn('Installation of npm dependencies failed')
        logging.warn(str(e))


build_js()

__version__ = '1.0.0'


setup(
    name='amundsen-frontend',
    version=__version__,
    description='Web UI for Amundsen',
    url='https://www.github.com/lyft/amundsenfrontendlibrary',
    maintainer='Lyft',
    maintainer_email='dev@lyft.com',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    dependency_links=[],
    install_requires=[
        # Packages in here should rarely be pinned. This is because these
        # packages (at the specified version) are required for project
        # consuming this library. By pinning to a specific version you are the
        # number of projects that can consume this or forcing them to
        # upgrade/downgrade any dependencies pinned here in their project.
        #
        # Generally packages listed here are pinned to a major version range.
        #
        # e.g.
        # Python FooBar package for foobaring
        # pyfoobar>=1.0, <2.0
        #
        # This will allow for any consuming projects to use this library as
        # long as they have a version of pyfoobar equal to or greater than 1.x
        # and less than 2.x installed.
    ],
    python_requires=">=3.6",
    entry_points="""
        [action_log.post_exec.plugin]
        logging_action_log=amundsen_application.log.action_log_callback:logging_action_log
    """,
)
