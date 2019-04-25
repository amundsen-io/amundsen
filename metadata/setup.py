from setuptools import setup, find_packages

__version__ = '1.0.5'


setup(
    name='amundsen-metadata',
    version=__version__,
    description='Metadata service package for Amundsen',
    url='https://www.github.com/lyft/amundsen',
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
        'Flask-RESTful>=0.3.6',
        'neo4j-driver==1.6.0',
        'beaker>=1.10.0',
        'statsd>=3.2.1',
        'atlasclient>=0.1.4'
    ]
)
