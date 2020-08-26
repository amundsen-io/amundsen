# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages


__version__ = '3.2.0'


requirements = [
    "neo4j-driver>=1.7.2,<4.0",
    "pytz>=2018.4",
    "statsd>=3.2.1",
    "retrying>=1.3.3",
    "requests>=2.23.0,<3.0",
    "elasticsearch>=6.2.0,<7.0",
    "pyhocon>=0.3.42",
    "unidecode",
]

kafka = ['confluent-kafka==1.0.0']

cassandra = ['cassandra-driver==3.20.1']

glue = ['boto3==1.10.1']

snowflake = [
    'snowflake-connector-python',
    'snowflake-sqlalchemy'
]

athena = ['PyAthena[SQLAlchemy]>=1.0.0']

# Python API client for google
# License: Apache Software License
# Upstream url: https://github.com/googleapis/google-api-python-client
bigquery = [
    'google-api-python-client>=1.6.0, <2.0.0dev',
    'google-auth-httplib2>=0.0.1'
    'google-auth>=1.0.0, <2.0.0dev'
]

jsonpath = ['jsonpath_rw==1.4.0']

db2 = [
    'ibm_db==3.0.1',
    'ibm-db-sa-py3==0.3.1-1'
]

druid = [
    'pydruid'
]

all_deps = requirements + kafka + cassandra + glue + snowflake + athena + bigquery + jsonpath + db2 + druid

setup(
    name='amundsen-databuilder',
    version=__version__,
    description='Amundsen Data builder',
    url='https://www.github.com/amundsen-io/amundsendatabuilder',
    maintainer='Amundsen TSC',
    maintainer_email='amundsen-tsc@lists.lfai.foundation',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=requirements,
    python_requires='>=3.6,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*',
    extras_require={
        ':python_version=="2.7"': ['typing>=3.6'],  # allow typehinting PY2
        'all': all_deps,
        'kafka': kafka,  # To use with Kafka source extractor
        'cassandra': cassandra,
        'glue': glue,
        'snowflake': snowflake,
        'athena': athena,
        'bigquery': bigquery,
        'jsonpath': jsonpath,
        'db2': db2,
        'druid': druid,
    },
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
