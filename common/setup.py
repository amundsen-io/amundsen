# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from setuptools import find_packages, setup

__version__ = '0.6.0'

setup(
    name='amundsen-common',
    version=__version__,
    description='Common code library for Amundsen',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/amundsen-io/amundsencommon',
    maintainer='Amundsen TSC',
    maintainer_email='amundsen-tsc@lists.lfai.foundation',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[
        ('git+https://www.github.com/hilearn/marshmallow-annotations.git@a7a2dc96932430369bd'
         'ef36555082df990ed9bef#egg=marshmallow-annotations')
    ],
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
        'flask>=1.0.2',
        'marshmallow>=2.15.3,<=3.6',
        'marshmallow-annotations'
    ],
    python_requires=">=3.6",
    package_data={'amundsen_common': ['py.typed']},
)
