# Amundsen Databuilder

[![PyPI version](https://badge.fury.io/py/amundsen-databuilder.svg)](https://badge.fury.io/py/amundsen-databuilder)
[![Build Status](https://api.travis-ci.com/lyft/amundsendatabuilder.svg?branch=master)](https://travis-ci.com/lyft/amundsendatabuilder)
[![Coverage Status](https://img.shields.io/codecov/c/github/lyft/amundsendatabuilder/master.svg)](https://codecov.io/github/lyft/amundsendatabuilder?branch=master)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/amundsen-databuilder.svg)](https://pypi.org/project/amundsen-databuilder/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://amundsenworkspace.slack.com/join/shared_invite/enQtNTk2ODQ1NDU1NDI0LTc3MzQyZmM0ZGFjNzg5MzY1MzJlZTg4YjQ4YTU0ZmMxYWU2MmVlMzhhY2MzMTc1MDg0MzRjNTA4MzRkMGE0Nzk)

Amundsen Databuilder is a data ingestion library, which is inspired by [Apache Gobblin](https://gobblin.apache.org/). It could be used in an orchestration framework(e.g. Apache Airflow) to build data from Amundsen. You could use the library either with an adhoc python script([example](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py)) or inside an Apache Airflow DAG([example](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/hive_sample_dag.py)).

For information about Amundsen and our other services, visit the [main repository](https://github.com/lyft/amundsen#amundsen) `README.md` . Please also see our instructions for a [quick start](https://github.com/lyft/amundsen/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker) setup  of Amundsen with dummy data, and an [overview of the architecture](https://github.com/lyft/amundsen/blob/master/docs/architecture.md#architecture).

## Requirements
- Python = 2.7.x or Python >= 3.6.x

## Doc
- https://lyft.github.io/amundsen/

## Concept
ETL job consists of extraction of records from the source, transform records, if necessary, and load records into the sink. Amundsen Databuilder is a ETL framework for Amundsen and there are corresponding components for ETL called Extractor, Transformer, and Loader that deals with record level operation. A component called task controls all these three components.
Job is the highest level component in Databuilder that controls task and publisher and is the one that client use to launch the ETL job.

In Databuilder, each components are highly modularized and each components are using namespace based config, HOCON config, which makes it highly reusable and pluggable. (e.g: transformer can be reused within extractor, or extractor can be reused within extractor)
(Note that concept on components are highly motivated by [Apache Gobblin](https://gobblin.apache.org/ "Apache Gobblin"))

![Databuilder components](docs/assets/AmundsenDataBuilder.png?raw=true "Title")


### [Extractor](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/extractor "Extractor")
Extractor extracts record from the source. This does not neccessarily mean that it only supports [pull pattern](https://blogs.sap.com/2013/12/09/to-push-or-pull-that-is-the-question/ "pull pattern") in ETL. For example, extracting record from messaging bus make it a push pattern in ETL.

### [Transformer](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/transformer "Transformer")
Transfomer takes record from either extractor or from transformer itself (via ChainedTransformer) to transform record.

### [Loader](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/loader "Loader")
A loader takes record from transformer or from extractor directly and load it to sink, or staging area. As loader is operated in record level, it's not capable of supporting atomicity.

### [Task](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/task "Task")
A task orchestrates extractor, transformer, and loader to perform record level operation.

### [Record](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/models "Record")
A record is represented by one of [models](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/models "models").

### [Publisher](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/publisher "Publisher")
A publisher is an optional component. It's common usage is to support atomicity in job level and/or to easily support bulk load into the sink.

### [Job](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/job "Job")
Job is the highest level component in Databuilder, and it orchestrates task, and publisher.

## [Model](docs/models.md)
Models are abstractions representing the domain.

## List of extractors
#### [DBAPIExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/db_api_extractor.py "DBAPIExtractor")
An extractor that uses [Python Database API](https://www.python.org/dev/peps/pep-0249/ "Python Database API") interface. DBAPI requires three information, connection object that conforms DBAPI spec, a SELECT SQL statement, and a [model class](https://github.com/lyft/amundsendatabuilder/tree/master/databuilder/models "model class") that correspond to the output of each row of SQL statement.

```python
job_config = ConfigFactory.from_dict({
		'extractor.dbapi{}'.format(DBAPIExtractor.CONNECTION_CONFIG_KEY): db_api_conn,
		'extractor.dbapi.{}'.format(DBAPIExtractor.SQL_CONFIG_KEY ): select_sql_stmt,
		'extractor.dbapi.model_class': 'package.module_name.class_name'
		})

job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=DBAPIExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [GenericExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/generic_extractor.py "GenericExtractor")
An extractor that takes list of dict from user through config.

#### [HiveTableLastUpdatedExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/hive_table_last_updated_extractor.py "HiveTableLastUpdatedExtractor")
An extractor that extracts last updated time from Hive metastore and underlying file system. Although, hive metastore has a parameter called "last_modified_time", but it cannot be used as it provides DDL timestamp not DML timestamp.
For this reason, HiveTableLastUpdatedExtractor is utilizing underlying file of Hive to fetch latest updated date. However, it is not efficient to poke all files in Hive, and it only pokes underlying storage for non-partitioned table. For partitioned table, it will fetch partition created timestamp, and it's close enough for last updated timestamp.

As getting metadata from files could be time consuming there're several features to increase performance.
1. Support of multithreading to parallelize metadata fetching. Although, cpython's multithreading is not true multithreading as it's bounded by single core, getting metadata of file is mostly IO bound operation. Note that number of threads should be less or equal to number of connections.
1. User can pass where clause to only include certain schema and also remove certain tables. For example, by adding something like `TBL_NAME NOT REGEXP '(tmp|temp)` would eliminate unncecessary computation.

```python
job_config = ConfigFactory.from_dict({
	'extractor.hive_table_last_updated.partitioned_table_where_clause_suffix': partitioned_table_where_clause,
	'extractor.hive_table_last_updated.non_partitioned_table_where_clause_suffix'): non_partitioned_table_where_clause,
	'extractor.hive_table_last_updated.extractor.sqlalchemy.{}'.format(
            SQLAlchemyExtractor.CONN_STRING): connection_string,
	'extractor.hive_table_last_updated.extractor.fs_worker_pool_size': pool_size,
	'extractor.hive_table_last_updated.filesystem.{}'.format(FileSystem.DASK_FILE_SYSTEM): s3fs.S3FileSystem(
		anon=False,
		config_kwargs={'max_pool_connections': pool_size})})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=HiveTableLastUpdatedExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [HiveTableMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/hive_table_metadata_extractor.py "HiveTableMetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from Hive metastore database.
```python
job_config = ConfigFactory.from_dict({
	'extractor.hive_table_metadata.{}'.format(HiveTableMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
	'extractor.hive_table_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string()})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=HiveTableMetadataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [CassandraExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/cassandra_extractor.py "CassandraExtractor")
An extractor that extracts table and column metadata including keyspace, table name, column name and column type from Apache Cassandra databases

```python
job_config = ConfigFactory.from_dict({
	'extractor.cassandra.{}'.format(CassandraExtractor.CLUSTER_KEY): cluster_identifier_string,
	'extractor.cassandra.{}'.format(CassandraExtractor.IPS_KEY): [127.0.0.1],
	'extractor.cassandra.{}'.format(CassandraExtractor.KWARGS_KEY): {},
	'extractor.cassandra.{}'.format(CassandraExtractor.FILTER_FUNCTION_KEY): my_filter_function,

})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=CassandraExtractor(),
		loader=AnyLoader()))
job.launch()
```

If using the function filter options here is the function description
```python
def filter(keytab, table):
  # return False if you don't want to add that table and True if you want to add
  return True
```

If needed to define more args on the cassandra cluster you can pass through kwargs args
```python
config = ConfigFactory.from_dict({
	'extractor.cassandra.{}'.format(CassandraExtractor.IPS_KEY): [127.0.0.1],
	'extractor.cassandra.{}'.format(CassandraExtractor.KWARGS_KEY): {'port': 9042}
})
# it will call the cluster constructor like this
Cluster([127.0.0.1], **kwargs)
```

#### [GlueExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/glue_extractor.py "GlueExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from AWS Glue metastore.

Before running make sure you have a working AWS profile configured and have access to search tables on Glue
```python
job_config = ConfigFactory.from_dict({
	'extractor.glue.{}'.format(GlueExtractor.CLUSTER_KEY): cluster_identifier_string,
	'extractor.glue.{}'.format(GlueExtractor.FILTER_KEY): []})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=GlueExtractor(),
		loader=AnyLoader()))
job.launch()
```

If using the filters option here is the input format
```
[
  {
    "Key": "string",
    "Value": "string",
    "Comparator": "EQUALS"|"GREATER_THAN"|"LESS_THAN"|"GREATER_THAN_EQUALS"|"LESS_THAN_EQUALS"
  }
  ...
]
```

#### [DruidMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/druid_metadata_extractor.py)
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a [Druid](https://druid.apache.org/) DB.

The `where_clause_suffix` could be defined, normally you would like to filter out the in `INFORMATION_SCHEMA`.

You could specify the following job config
```python
conn_string = "druid+https://{host}:{port}/druid/v2/sql/".format(
		host=druid_broker_host,
		port=443
)
job_config = ConfigFactory.from_dict({
	'extractor.druid_metadata.{}'.format(PostgresMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
  'extractor.druid_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): conn_string()})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=DruidMetadataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [PostgresMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/postgres_metadata_extractor.py "PostgresMetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a Postgres or Redshift database.

By default, the Postgres/Redshift database name is used as the cluster name. To override this, set `USE_CATALOG_AS_CLUSTER_NAME`
to `False`, and `CLUSTER_KEY` to what you wish to use as the cluster name.

The `where_clause_suffix` below should define which schemas you'd like to query (see [the sample dag](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/postgres_sample_dag.py) for an example).

The SQL query driving the extraction is defined [here](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/postgres_metadata_extractor.py)

```python
job_config = ConfigFactory.from_dict({
	'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
    'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME): True,
	'extractor.postgres_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string()})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=PostgresMetadataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [MSSQLMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/mssql_metadata_extractor.py "PostgresMetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a Microsoft SQL database.

By default, the Microsoft SQL Server Database name is used as the cluster name. To override this, set `USE_CATALOG_AS_CLUSTER_NAME`
to `False`, and `CLUSTER_KEY` to what you wish to use as the cluster name.

The `where_clause_suffix` below should define which schemas you'd like to query (`"('dbo','sys')"`).

The SQL query driving the extraction is defined [here](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/mssql_metadata_extractor.py)

This extractor is highly derived from [PostgresMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/postgres_metadata_extractor.py "PostgresMetadataExtractor").
```python
job_config = ConfigFactory.from_dict({
	'extractor.mssql_metadata.{}'.format(MSSQLMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
    'extractor.mssql_metadata.{}'.format(MSSQLMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME): True,
	'extractor.mssql_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string()})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=MSSQLMetadataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [MysqlMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/mysql_metadata_extractor.py "MysqlMetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a MYSQL database.

By default, the MYSQL database name is used as the cluster name. To override this, set `USE_CATALOG_AS_CLUSTER_NAME`
to `False`, and `CLUSTER_KEY` to what you wish to use as the cluster name.

The `where_clause_suffix` below should define which schemas you'd like to query.

The SQL query driving the extraction is defined [here](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/mysql_metadata_extractor.py)

```python
job_config = ConfigFactory.from_dict({
	'extractor.mysql_metadata.{}'.format(MysqlMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
  'extractor.mysql_metadata.{}'.format(MysqlMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME): True,
	'extractor.mysql_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string()})
job = DefaultJob(conf=job_config,
								 task=DefaultTask(extractor=MysqlMetadataExtractor(), loader=FsNeo4jCSVLoader()),
								 publisher=Neo4jCsvPublisher())
job.launch()


#### [Db2MetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/db2_metadata_extractor.py "Db2MetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a Unix, Windows or Linux Db2 database or BigSQL.

The `where_clause_suffix` below should define which schemas you'd like to query or those that you would not (see [the sample data loader](https://github.com/lyft/amundsendatabuilder/blob/master/example/sample_db2_data_loader.py) for an example).

The SQL query driving the extraction is defined [here](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/db2_metadata_extractor.py)

```python
job_config = ConfigFactory.from_dict({
	'extractor.db2_metadata.{}'.format(Db2MetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
	'extractor.db2_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string()})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=Db2MetadataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [SnowflakeMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/snowflake_metadata_extractor.py "SnowflakeMetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a Snowflake database.

By default, the Snowflake database name is used as the cluter name. To override this, set `USE_CATALOG_AS_CLUSTER_NAME`
to `False`, and `CLUSTER_KEY` to what you wish to use as the cluster name.

By default, the Snowflake database is set to `PROD`. To override this, set `DATABASE_KEY`
to `WhateverNameOfYourDb`.

The `where_clause_suffix` below should define which schemas you'd like to query (see [the sample dag](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_snowflake_data_loader.py) for an example).

The SQL query driving the extraction is defined [here](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/snowflake_metadata_extractor.py)

```python
job_config = ConfigFactory.from_dict({
	'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.DATABASE_KEY): 'YourDbName',
	'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY): where_clause_suffix,
    'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME): True,
	'extractor.postgres_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string()})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=SnowflakeMetadataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [BigQueryMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/bigquery_metadata_extractor.py "BigQuery Metdata Extractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a Bigquery database.

The API calls driving the extraction is defined [here](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/bigquery_metadata_extractor.py)

You will need to create a service account for reading metadata and grant it "BigQuery Metadata Viewer" access to all of your datasets. This can all be done via the bigquery ui.

Download the creditials file and store it securely. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment varible to the location of your credtials files and your code should have access to everything it needs.

You can configure bigquery like this. You can optionally set a label filter if you only want to pull tables with a certain label.
```python
    job_config = {
        'extractor.bigquery_table_metadata.{}'.format(
            BigQueryMetadataExtractor.PROJECT_ID_KEY
            ): gcloud_project
    }
    if label_filter:
        job_config[
            'extractor.bigquery_table_metadata.{}'
            .format(BigQueryMetadataExtractor.FILTER_KEY)
            ] = label_filter
    task = DefaultTask(extractor=BigQueryMetadataExtractor(),
                       loader=csv_loader,
                       transformer=NoopTransformer())
    job = DefaultJob(conf=ConfigFactory.from_dict(job_config),
                     task=task,
                     publisher=Neo4jCsvPublisher())
job.launch()
```

#### [Neo4jEsLastUpdatedExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/neo4j_es_last_updated_extractor.py "Neo4jEsLastUpdatedExtractor")
An extractor that basically get current timestamp and passes it GenericExtractor. This extractor is basically being used to create timestamp for "Amundsen was last indexed on ..." in Amundsen web page's footer.

#### [Neo4jExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/neo4j_extractor.py "Neo4jExtractor")
An extractor that extracts records from Neo4j based on provided [Cypher query](https://neo4j.com/developer/cypher/ "Cypher query"). One example is to extract data from Neo4j so that it can transform and publish to Elasticsearch.
```python
job_config = ConfigFactory.from_dict({
	'extractor.neo4j.{}'.format(Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY)': cypher_query,
	'extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY): neo4j_endpoint,
	'extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY): 'package.module.class_name',
	'extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_USER): neo4j_user,
	'extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_PW): neo4j_password})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=Neo4jExtractor(),
		loader=AnyLoader()))
job.launch()
```
#### [Neo4jSearchDataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/neo4j_search_data_extractor.py "Neo4jSearchDataExtractor")
An extractor that is extracting Neo4j utilizing Neo4jExtractor where CYPHER query is already embedded in it.
```python
job_config = ConfigFactory.from_dict({
	'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.GRAPH_URL_CONFIG_KEY): neo4j_endpoint,
	'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.MODEL_CLASS_CONFIG_KEY): 'databuilder.models.neo4j_data.Neo4jDataResult',
	'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_USER): neo4j_user,
	'extractor.search_data.extractor.neo4j.{}'.format(Neo4jExtractor.NEO4J_AUTH_PW): neo4j_password})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=Neo4jSearchDataExtractor(),
		loader=AnyLoader()))
job.launch()
```

#### [SQLAlchemyExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/sql_alchemy_extractor.py "SQLAlchemyExtractor")
An extractor utilizes [SQLAlchemy](https://www.sqlalchemy.org/ "SQLAlchemy") to extract record from any database that support SQL Alchemy.
```python
job_config = ConfigFactory.from_dict({
	'extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING): connection_string(),
	'extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.EXTRACT_SQL): sql,
	'extractor.sqlalchemy.model_class': 'package.module.class_name'})
job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=SQLAlchemyExtractor(),
		loader=AnyLoader()))
job.launch()
```

### [RestAPIExtractor](./databuilder/extractor/restapi/rest_api_extractor.py)
A extractor that utilizes [RestAPIQuery](#rest-api-query) to extract data. RestAPIQuery needs to be constructed ([example](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_extractor.py#L40)) and needs to be injected to RestAPIExtractor.

### Mode Dashboard Extractor
Here are extractors that extracts metadata information from Mode via Mode's REST API.

Prerequisite:

 1. You will need to [create API access token](https://mode.com/developer/api-reference/authentication/) that has admin privilege.
 2. You will need organization code. This is something you can easily get by looking at one of Mode report's URL. 	  
	 `https://app.mode.com/<organization code>/reports/report_token`

#### [ModeDashboardExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_extractor.py)
A Extractor that extracts core metadata on Mode dashboard. https://app.mode.com/

It extracts list of reports that consists of:
Dashboard group name (Space name)
Dashboard group id (Space token)
Dashboard group description (Space description)
Dashboard name (Report name)
Dashboard id (Report token)
Dashboard description (Report description)

Other information such as report run, owner, chart name, query name is in separate extractor.

It calls two APIs ([spaces API](https://mode.com/developer/api-reference/management/spaces/#listSpaces) and [reports API](https://mode.com/developer/api-reference/analytics/reports/#listReportsInSpace)) joining together.

You can create Databuilder job config like this. 
```python
task = DefaultTask(extractor=ModeDashboardExtractor(),
				   loader=FsNeo4jCSVLoader(), )

tmp_folder = '/var/tmp/amundsen/mode_dashboard_metadata'

node_files_folder = '{tmp_folder}/nodes'.format(tmp_folder=tmp_folder)
relationship_files_folder = '{tmp_folder}/relationships'.format(tmp_folder=tmp_folder)

job_config = ConfigFactory.from_dict({
	'extractor.mode_dashboard.{}'.format(ORGANIZATION): organization,
	'extractor.mode_dashboard.{}'.format(MODE_ACCESS_TOKEN): mode_token,
	'extractor.mode_dashboard.{}'.format(MODE_PASSWORD_TOKEN): mode_password,
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH): node_files_folder,
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH): relationship_files_folder,
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR): True,
	'task.progress_report_frequency': 100,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR): node_files_folder,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR): relationship_files_folder,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY): neo4j_endpoint,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER): neo4j_user,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD): neo4j_password,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_CREATE_ONLY_NODES): [DESCRIPTION_NODE_LABEL],
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.JOB_PUBLISH_TAG): job_publish_tag
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```


#### [ModeDashboardOwnerExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_owner_extractor.py)
An Extractor that extracts Dashboard owner. Mode itself does not have concept of owner and it will use creator as owner. Note that if user left the organization, it would skip the dashboard.

You can create Databuilder job config like this. (configuration related to loader and publisher is omitted as it is mostly the same. Please take a look at this [example](#ModeDashboardExtractor) for the configuration that holds loader and publisher.

```python
extractor = ModeDashboardOwnerExtractor()
task = DefaultTask(extractor=extractor,
				   loader=FsNeo4jCSVLoader(), )

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(extractor.get_scope(), MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(extractor.get_scope(), MODE_PASSWORD_TOKEN): mode_password,
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ModeDashboardLastSuccessfulExecutionExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_last_successful_executions_extractor.py)
A Extractor that extracts Mode dashboard's last successful run (execution) timestamp.

You can create Databuilder job config like this. (configuration related to loader and publisher is omitted as it is mostly the same. Please take a look at this [example](#ModeDashboardExtractor) for the configuration that holds loader and publisher.

```python
extractor = ModeDashboardLastSuccessfulExecutionExtractor()
task = DefaultTask(extractor=extractor,
                   loader=FsNeo4jCSVLoader(), )

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(extractor.get_scope(), MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(extractor.get_scope(), MODE_PASSWORD_TOKEN): mode_password,
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ModeDashboardExecutionsExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_executions_extractor.py)
A Extractor that extracts last run (execution) status and timestamp.

You can create Databuilder job config like this. (configuration related to loader and publisher is omitted as it is mostly the same. Please take a look at this [example](#ModeDashboardExtractor) for the configuration that holds loader and publisher.

```python
extractor = ModeDashboardExecutionsExtractor()
task = DefaultTask(extractor=extractor,
				   loader=FsNeo4jCSVLoader(), )

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(extractor.get_scope(), MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(extractor.get_scope(), MODE_PASSWORD_TOKEN): mode_password,
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ModeDashboardLastModifiedTimestampExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_last_modified_timestamp_extractor.py)
A Extractor that extracts Mode dashboard's last modified timestamp.

You can create Databuilder job config like this. (configuration related to loader and publisher is omitted as it is mostly the same. Please take a look at this [example](#ModeDashboardExtractor) for the configuration that holds loader and publisher.

```python
extractor = ModeDashboardLastModifiedTimestampExtractor()
task = DefaultTask(extractor=extractor, loader=FsNeo4jCSVLoader())

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(extractor.get_scope(), MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(extractor.get_scope(), MODE_PASSWORD_TOKEN): mode_password,
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ModeDashboardQueriesExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_queries_extractor.py)
A Extractor that extracts Mode's query information.

You can create Databuilder job config like this. (configuration related to loader and publisher is omitted as it is mostly the same. Please take a look at this [example](#ModeDashboardExtractor) for the configuration that holds loader and publisher.

```python
extractor = ModeDashboardQueriesExtractor()
task = DefaultTask(extractor=extractor, loader=FsNeo4jCSVLoader())

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(extractor.get_scope(), MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(extractor.get_scope(), MODE_PASSWORD_TOKEN): mode_password,
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ModeDashboardChartsExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_charts_extractor.py)
A Extractor that extracts Mode Dashboard charts. Currently, Mode API response schema is undocumented and hard to be used for the schema seems different per chart type. For this reason, this extractor can only extracts Chart token, and Chart URL at this point.

You can create Databuilder job config like this. (configuration related to loader and publisher is omitted as it is mostly the same. Please take a look at this [example](#ModeDashboardExtractor) for the configuration that holds loader and publisher.

```python
extractor = ModeDashboardChartsExtractor()
task = DefaultTask(extractor=extractor, loader=FsNeo4jCSVLoader())

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(extractor.get_scope(), MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(extractor.get_scope(), MODE_PASSWORD_TOKEN): mode_password,
})

job = DefaultJob(conf=job_config,
                 task=task,
                 publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ModeDashboardUsageExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_usage_extractor.py)

A Extractor that extracts Mode dashboard's accumulated view count.

Note that this provides accumulated view count which does [not effectively show relevancy](./docs/dashboard_ingestion_guide.md#21-ingest-dashboard-usage-data-and-decorate-neo4j-over-base-data). Thus, fields from this extractor is not directly compatible with [DashboardUsage](./docs/models.md#dashboardusage) model.

If you are fine with `accumulated usage`, you could use TemplateVariableSubstitutionTransformer to transform Dict payload from [ModeDashboardUsageExtractor](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_usage_extractor.py) to fit [DashboardUsage](./docs/models.md#dashboardusage) and transform Dict to  [DashboardUsage](./docs/models.md#dashboardusage) by [TemplateVariableSubstitutionTransformer](./databuilder/transformer/template_variable_substitution_transformer.py), and [DictToModel](./databuilder/transformer/dict_to_model.py) transformers. ([Example](./databuilder/extractor/dashboard/mode_analytics/mode_dashboard_queries_extractor.py#L36) on how to combining these two transformers)


## List of transformers
#### [ChainedTransformer](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/transformer/base_transformer.py#L41 "ChainedTransformer")
A chanined transformer that can take multiple transformer.

#### [RegexStrReplaceTransformer](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/transformer/regex_str_replace_transformer.py "RegexStrReplaceTransformer")
Generic string replacement transformer using REGEX. User can pass list of tuples where tuple contains regex and replacement pair.
```python
job_config = ConfigFactory.from_dict({
	'transformer.regex_str_replace.{}'.format(REGEX_REPLACE_TUPLE_LIST): [(',', ' '), ('"', '')],
	'transformer.regex_str_replace.{}'.format(ATTRIBUTE_NAME): 'instance_field_name',})

job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=AnyExtractor(),
		transformer=RegexStrReplaceTransformer(),
		loader=AnyLoader()))
job.launch()
```

#### [TemplateVariableSubstitutionTransformer](./databuilder/transformer/template_variable_substitution_transformer.py)
Adds or replaces field in Dict by string.format based on given template and provide record Dict as a template parameter

#### [DictToModel](./databuilder/transformer/dict_to_model.py)
Transforms dictionary into model

#### [TimestampStringToEpoch](./databuilder/transformer/timestamp_string_to_epoch.py)
Transforms string timestamp into int epoch


## List of loader
#### [FsNeo4jCSVLoader](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/loader/file_system_neo4j_csv_loader.py "FsNeo4jCSVLoader")
Write node and relationship CSV file(s) that can be consumed by Neo4jCsvPublisher. It assumes that the record it consumes is instance of Neo4jCsvSerializable.

```python
job_config = ConfigFactory.from_dict({
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH): node_files_folder,
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH): relationship_files_folder},)

job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=AnyExtractor(),
		loader=FsNeo4jCSVLoader()),
	publisher=Neo4jCsvPublisher())
job.launch()
```

#### [GenericLoader](./databuilder/loader/generic_loader.py)
Loader class that calls user provided callback function with record as a parameter

Example that pushes Mode Dashboard accumulated usage via GenericLoader where callback_function expected to insert record to data warehouse.

```python
extractor = ModeDashboardUsageExtractor()
task = DefaultTask(extractor=extractor,
                   loader=GenericLoader(), )

job_config = ConfigFactory.from_dict({
	'{}.{}'.format(extractor.get_scope(), ORGANIZATION): organization,
	'{}.{}'.format(MODE_ACCESS_TOKEN): mode_token,
	'{}.{}'.format(MODE_PASSWORD_TOKEN): mode_password,
	'loader.generic.callback_function': callback_function
})

job = DefaultJob(conf=job_config, task=task)
job.launch()

```


#### [FSElasticsearchJSONLoader](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/loader/file_system_elasticsearch_json_loader.py "FSElasticsearchJSONLoader")
Write Elasticsearch document in JSON format which can be consumed by ElasticsearchPublisher. It assumes that the record it consumes is instance of ElasticsearchDocument.

```python
tmp_folder = '/var/tmp/amundsen/dummy_metadata'
node_files_folder = '{tmp_folder}/nodes/'.format(tmp_folder=tmp_folder)
relationship_files_folder = '{tmp_folder}/relationships/'.format(tmp_folder=tmp_folder)

job_config = ConfigFactory.from_dict({
	'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY): data_file_path,
	'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY): 'w',})

job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=AnyExtractor(),
		loader=FSElasticsearchJSONLoader()),
	publisher=ElasticsearchPublisher())
job.launch()
```

## List of publisher
#### [Neo4jCsvPublisher](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/publisher/neo4j_csv_publisher.py "Neo4jCsvPublisher")
A Publisher takes two folders for input and publishes to Neo4j.
One folder will contain CSV file(s) for Node where the other folder will contain CSV file(s) for Relationship. Neo4j follows Label Node properties Graph and refer to [here](https://neo4j.com/docs/developer-manual/current/introduction/graphdb-concepts/ "here") for more information

```python
job_config = ConfigFactory.from_dict({
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH): node_files_folder,
	'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH): relationship_files_folder,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR): node_files_folder,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR): relationship_files_folder,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY): neo4j_endpoint,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER): neo4j_user,
	'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD): neo4j_password,})

job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=AnyExtractor(),
		loader=FsNeo4jCSVLoader()),
	publisher=Neo4jCsvPublisher())
job.launch()
```

#### [ElasticsearchPublisher](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/publisher/elasticsearch_publisher.py "ElasticsearchPublisher")
Elasticsearch Publisher uses Bulk API to load data from JSON file. Elasticsearch publisher supports atomic operation by utilizing alias in Elasticsearch.
A new index is created and data is uploaded into it. After the upload is complete, index alias is swapped to point to new index from old index and traffic is routed to new index.
```python
tmp_folder = '/var/tmp/amundsen/dummy_metadata'
node_files_folder = '{tmp_folder}/nodes/'.format(tmp_folder=tmp_folder)
relationship_files_folder = '{tmp_folder}/relationships/'.format(tmp_folder=tmp_folder)

job_config = ConfigFactory.from_dict({
	'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY): data_file_path,
	'loader.filesystem.elasticsearch.{}'.format(FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY): 'w',
	'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_PATH_CONFIG_KEY): data_file_path,
	'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.FILE_MODE_CONFIG_KEY): 'r',
	'publisher.elasticsearch{}'.format(ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY): elasticsearch_client,
	'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY): elasticsearch_new_index,
	'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY): elasticsearch_doc_type,
	'publisher.elasticsearch.{}'.format(ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY): elasticsearch_index_alias,)

job = DefaultJob(
	conf=job_config,
	task=DefaultTask(
		extractor=AnyExtractor(),
		loader=FSElasticsearchJSONLoader()),
	publisher=ElasticsearchPublisher())
job.launch()
```

#### [Callback](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/callback/call_back.py "Callback")
Callback interface is built upon a [Observer pattern](https://en.wikipedia.org/wiki/Observer_pattern "Observer pattern") where the participant want to take any action when target's state changes.

Publisher is the first one adopting Callback where registered Callback will be called either when publish succeeded or when publish failed. In order to register callback, Publisher provides [register_call_back](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/publisher/base_publisher.py#L50 "register_call_back") method.

One use case is for Extractor that needs to commit when job is finished (e.g: Kafka). Having Extractor register a callback to Publisher to commit when publish is successful, extractor can safely commit by implementing commit logic into [on_success](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/callback/call_back.py#L18 "on_success") method.

### REST API Query
Databuilder now has a generic REST API Query capability that can be joined each other.
Most of the cases of extraction is currently from Database or Datawarehouse that is queryable via SQL. However, not all metadata sources provide our access to its Database and they mostly provide REST API to consume their metadata.

The challenges come with REST API is that:

 1. there's no explicit standard in REST API. Here, we need to conform to majority of cases (HTTP call with JSON payload & response) but open for extension for different authentication scheme, and different way of pagination, etc.
 2. It is hardly the case that you would get what you want from one REST API call. It is usually the case that you need to snitch (JOIN) multiple REST API calls together to get the information you want.

To solve this challenges, we introduce [RestApiQuery](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/rest_api/rest_api_query.py)

RestAPIQuery is:  
 1. Assuming that REST API is using HTTP(S) call with GET method -- RestAPIQuery intention's is **read**, not write -- where basic HTTP auth is supported out of the box. There's extension point on other authentication scheme such as Oauth, and pagination, etc. (See [ModePaginatedRestApiQuery](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/rest_api/mode_analytics/mode_paginated_rest_api_query.py) for pagination)
 2. Usually, you want the subset of the response you get from the REST API call -- value extraction. To extract the value you want, RestApiQuery uses [JSONPath](https://goessner.net/articles/JsonPath/) which is similar product as XPATH of XML.
 3. You can JOIN multiple RestApiQuery together.

More detail on JOIN operation in RestApiQuery:  
 1. It joins multiple RestApiQuery together by accepting prior RestApiQuery as a constructor -- a [Decorator pattern](https://en.wikipedia.org/wiki/Decorator_pattern)
 2. In REST API, URL is the one that locates the resource we want. Here, JOIN simply means we need to find resource **based on the identifier that other query's result has**. In other words, when RestApiQuery forms URL, it uses previous query's result to compute the URL `e.g: Previous record: {"dashboard_id": "foo"}, URL before: http://foo.bar/dashboard/{dashboard_id} URL after compute: http://foo.bar/dashboard/foo`
With this pattern RestApiQuery supports 1:1 and 1:N JOIN relationship.  
(GROUP BY or any other aggregation, sub-query join is not supported)  

To see in action, take a peek at [ModeDashboardExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/dashboard/mode_analytics/mode_dashboard_extractor.py)
Also, take a look at how it extends to support pagination at [ModePaginatedRestApiQuery](./databuilder/rest_api/mode_analytics/mode_paginated_rest_api_query.py).

### Removing stale data in Neo4j -- [Neo4jStalenessRemovalTask](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/task/neo4j_staleness_removal_task.py):

As Databuilder ingestion mostly consists of either INSERT OR UPDATE, there could be some stale data that has been removed from metadata source but still remains in Neo4j database. Neo4jStalenessRemovalTask basically detects staleness and removes it.

In [Neo4jCsvPublisher](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/publisher/neo4j_csv_publisher.py), it adds attributes "published_tag" and "publisher_last_updated_epoch_ms" on every nodes and relations. You can use either of these two attributes to detect staleness and remove those stale node or relation from the database.

#### Using "published_tag" to remove stale data
Use *published_tag* to remove stale data, when it is certain that non-matching tag is stale once all the ingestion is completed. For example, suppose that you use current date (or execution date in Airflow) as a *published_tag*, "2020-03-31". Once Databuilder ingests all tables and all columns, all table nodes and column nodes should have *published_tag* as "2020-03-31". It is safe to assume that table nodes and column nodes whose *published_tag* is different -- such as "2020-03-30" or "2020-02-10" -- means that it is deleted from the source metadata. You can use Neo4jStalenessRemovalTask to delete those stale data.

    task = Neo4jStalenessRemovalTask()
    job_config_dict = {
        'job.identifier': 'remove_stale_data_job',
        'task.remove_stale_data.neo4j_endpoint': neo4j_endpoint,
        'task.remove_stale_data.neo4j_user': neo4j_user,
        'task.remove_stale_data.neo4j_password': neo4j_password,
        'task.remove_stale_data.staleness_max_pct': 10,
        'task.remove_stale_data.target_nodes': ['Table', 'Column'],
        'task.remove_stale_data.job_publish_tag': '2020-03-31'
    }
    job_config = ConfigFactory.from_dict(job_config_dict)
    job = DefaultJob(conf=job_config, task=task)
    job.launch()

Note that there's protection mechanism, **staleness_max_pct**, that protect your data being wiped out when something is clearly wrong. "**staleness_max_pct**" basically first measure the proportion of elements that will be deleted and if it exceeds threshold per type ( 10% on the configuration above ), the deletion won't be executed and the task aborts.

#### Using "publisher_last_updated_epoch_ms" to remove stale data
You can think this approach as TTL based eviction. This is particularly useful when there are multiple ingestion pipelines and you cannot be sure when all ingestion is done. In this case, you might still can say that if specific node or relation has not been published past 3 days, it's stale data.

    task = Neo4jStalenessRemovalTask()
    job_config_dict = {
        'job.identifier': 'remove_stale_data_job',
        'task.remove_stale_data.neo4j_endpoint': neo4j_endpoint,
        'task.remove_stale_data.neo4j_user': neo4j_user,
        'task.remove_stale_data.neo4j_password': neo4j_password,
        'task.remove_stale_data.staleness_max_pct': 10,
        'task.remove_stale_data.target_relations': ['READ', 'READ_BY'],
        'task.remove_stale_data.milliseconds_to_expire': 86400000 * 3
    }
    job_config = ConfigFactory.from_dict(job_config_dict)
    job = DefaultJob(conf=job_config, task=task)
    job.launch()

Above configuration is trying to delete stale usage relation (READ, READ_BY), by deleting READ or READ_BY relation that has not been published past 3 days. If number of elements to be removed is more than 10% per type, this task will be aborted without executing any deletion.

#### Dry run
Deletion is always scary and it's better to perform dryrun before put this into action. You can use Dry run to see what sort of Cypher query will be executed.

    task = Neo4jStalenessRemovalTask()
    job_config_dict = {
        'job.identifier': 'remove_stale_data_job',
        'task.remove_stale_data.neo4j_endpoint': neo4j_endpoint,
        'task.remove_stale_data.neo4j_user': neo4j_user,
        'task.remove_stale_data.neo4j_password': neo4j_password,
        'task.remove_stale_data.staleness_max_pct': 10,
        'task.remove_stale_data.target_relations': ['READ', 'READ_BY'],
        'task.remove_stale_data.milliseconds_to_expire': 86400000 * 3
        'task.remove_stale_data.dry_run': True
    }
    job_config = ConfigFactory.from_dict(job_config_dict)
    job = DefaultJob(conf=job_config, task=task)
    job.launch()
