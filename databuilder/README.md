# Amundsen Databuilder

[![PyPI version](https://badge.fury.io/py/amundsen-databuilder.svg)](https://badge.fury.io/py/amundsen-databuilder)
[![Build Status](https://api.travis-ci.com/lyft/amundsendatabuilder.svg?branch=master)](https://travis-ci.com/lyft/amundsendatabuilder)
[![Coverage Status](https://img.shields.io/codecov/c/github/lyft/amundsendatabuilder/master.svg)](https://codecov.io/github/lyft/amundsendatabuilder?branch=master)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://amundsenworkspace.slack.com/join/shared_invite/enQtNTk2ODQ1NDU1NDI0LTc3MzQyZmM0ZGFjNzg5MzY1MzJlZTg4YjQ4YTU0ZmMxYWU2MmVlMzhhY2MzMTc1MDg0MzRjNTA4MzRkMGE0Nzk)

Amundsen Databuilder is a data ingestion library, which is inspired by [Apache Gobblin](https://gobblin.apache.org/). It could be used in an orchestration framework(e.g. Apache Airflow) to build data from Amundsen. You could use the library either with an adhoc python script([example](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py)) or inside an Apache Airflow DAG([example](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/sample_dag.py)).

For information about Amundsen and our other services, visit the [main repository](https://github.com/lyft/amundsen#amundsen) `README.md` . Please also see our instructions for a [quick start](https://github.com/lyft/amundsen/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker) setup  of Amundsen with dummy data, and an [overview of the architecture](https://github.com/lyft/amundsen/blob/master/docs/architecture.md#architecture).

## Requirements
- Python = 2.7.x (And Python >= 3.x if you don't use column usage transformer as it depends on antlr python 2 runtime)

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
An extractor that extracts last updated time from Hive metastore and underlying file system. Although, hive metastore as a parameter called "last_modified_time", but it cannot be used as it provides DDL timestamp not DML timestamp.
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

#### [PostgresMetadataExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/postgres_metadata_extractor.py "PostgresMetadataExtractor")
An extractor that extracts table and column metadata including database, schema, table name, table description, column name and column description from a Postgres or Redshift database.

By default, the Postgres/Redshift database name is used as the cluter name. To override this, set `USE_CATALOG_AS_CLUSTER_NAME`
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

#### [TblColUsgAggExtractor](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/extractor/table_column_usage_aggregate_extractor.py "TblColUsgAggExtractor")
An extractor that extracts table usage from SQL statements. It accept any extractor  that extracts row from source that has SQL audit log. Once SQL statement is extracted, it uses [ANTLR](https://www.antlr.org/ "ANTLR") to parse and get tables and columns that it reads from. Also, it aggregates usage based on table and user. (Column level aggregation is not there yet.)


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

#### [SqlToTblColUsageTransformer](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/transformer/sql_to_table_col_usage_transformer.py "SqlToTblColUsageTransformer")
A SQL to usage transformer where it transforms to ColumnReader that has column, user, count. Currently it's collects on table level that column on same table will be de-duped. In many cases, "from" clause does not contain schema and this will be fetched via table name -> schema name mapping which it gets from metadata extractor.

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
