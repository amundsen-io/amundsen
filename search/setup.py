from setuptools import setup, find_packages

__version__ = '1.0.3'


setup(
    name='amundsen-search',
    version=__version__,
    description='Search Service for Amundsen',
    url='https://github.com/lyft/amundsensearchlibrary.git',
    maintainer='Lyft',
    maintainer_email='dp-tools@lyft.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=[
        'Flask-RESTFul==0.3.6',
        'elasticsearch==6.2.0',
        'elasticsearch-dsl==6.1.0',
        'statsd==3.2.1'
    ],
    python_requires=">=3.6"
)
