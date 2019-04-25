from setuptools import setup, find_packages


__version__ = '1.0.11'


setup(
    name='amundsen-databuilder',
    version=__version__,
    description='Amundsen Data builder',
    url='https://www.github.com/lyft/amundsendatabuilder',
    maintainer='Lyft',
    maintainer_email='dev@lyft.com',
    packages=find_packages(exclude=['tests*']),
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
        'pyhocon==0.3.42',
        'pytest==3.6.0',
        'six',
        'neo4j-driver==1.6.0',
        'antlr4-python2-runtime==4.7.1',
        'statsd==3.2.1',
        'retrying==1.3.3'
    ],
    extras_require={
        ':python_version=="2.7"': ['typing>=3.6'],  # allow typehinting PY2
    },
)
