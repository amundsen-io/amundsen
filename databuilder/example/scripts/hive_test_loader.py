# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
import textwrap
import uuid
sys.path.append('/Users/dye/Dev/amundsen/databuilder')
from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory
from sqlalchemy.ext.declarative import declarative_base
import pymysql
pymysql.install_as_MySQLdb()

from databuilder.extractor.hive_table_metadata_extractor import HiveTableMetadataExtractor
from databuilder.extractor.hive_table_last_updated_extractor import HiveTableLastUpdatedExtractor
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.models.table_metadata import DESCRIPTION_NODE_LABEL
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher

es_host = None
neo_host = None
if len(sys.argv) > 1:
    es_host = sys.argv[1]
if len(sys.argv) > 2:
    neo_host = sys.argv[2]

es = Elasticsearch([
    {'host': es_host or 'localhost'},
])

DB_FILE = '/tmp/test.db'
SQLITE_CONN_STRING = 'sqlite:////tmp/test.db'
Base = declarative_base()

# NEO4J cluster endpoints
NEO4J_ENDPOINT = 'bolt://localhost:7687'

neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

# Todo: user provides a list of schema for indexing
SUPPORTED_HIVE_SCHEMAS = ['prod_lbu_pii','prod_lbu_cube','prod_lbu_datelist','prod_lbu_nonpii','prod_stream_data','prod_lbu_metrics_summary']
# Global used in all Hive metastore queries.
# String format - ('schema1', schema2', .... 'schemaN')
SUPPORTED_HIVE_SCHEMA_SQL_IN_CLAUSE = "('{schemas}')".format(schemas="', '".join(SUPPORTED_HIVE_SCHEMAS))

LOGGER = logging.getLogger(__name__)


# Todo: user needs to modify and provide a hivemetastore connection string
def connection_string():
    user = 'root:luobu123!@#'
    hostname = '172.28.244.39'
    port = 3306
    db = 'hivemetastore'
    return "mysql+pymysql://%s@%s:%s/%s" % (user, hostname, port, db)

def create_table_wm_job(**kwargs):
    sql_wm = textwrap.dedent("""
        SELECT From_unixtime(A0.create_time) as create_time,
               'hive'                        as `database`,
               C0.NAME                       as `schema`,
               B0.tbl_name as table_name,
               {func}(A0.part_name) as part_name,
               {watermark} as part_type
        FROM   PARTITIONS A0
               LEFT OUTER JOIN TBLS B0
                            ON A0.tbl_id = B0.tbl_id
               LEFT OUTER JOIN DBS C0
                            ON B0.db_id = C0.db_id
        WHERE  C0.NAME IN {schemas}
               AND B0.tbl_type IN ( 'EXTERNAL_TABLE', 'MANAGED_TABLE' )
               AND A0.PART_NAME NOT LIKE '%%__HIVE_DEFAULT_PARTITION__%%'
        GROUP  BY C0.NAME, B0.tbl_name
        ORDER by create_time desc
    """).format(func=kwargs['templates_dict'].get('agg_func'),
                watermark=kwargs['templates_dict'].get('watermark_type'),
                schemas=SUPPORTED_HIVE_SCHEMA_SQL_IN_CLAUSE)

    LOGGER.info('SQL query: %s', sql_wm)
    tmp_folder = '/var/tmp/amundsen/table_{hwm}'.format(hwm=kwargs['templates_dict'].get('watermark_type').strip("\""))
    node_files_folder = f'{tmp_folder}/nodes'
    relationship_files_folder = f'{tmp_folder}/relationships'

    hwm_extractor = SQLAlchemyExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=hwm_extractor, loader=csv_loader, transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        f'extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': connection_string(),
        f'extractor.sqlalchemy.{SQLAlchemyExtractor.EXTRACT_SQL}': sql_wm,
        'extractor.sqlalchemy.model_class': 'databuilder.models.watermark.Watermark',
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        'publisher.neo4j.job_publish_tag': 'test_hive_watermark'  # TO-DO unique tag must be added
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job

def create_table_owner_job():
    sql_owner = textwrap.dedent("""
        SELECT 'hive' as `db_name`,
               C0.NAME as `schema`,
               B0.tbl_name as table_name,
               GROUP_CONCAT(OWNER) as owners
        FROM TBLS B0
        LEFT OUTER JOIN DBS C0 ON B0.db_id = C0.db_id
        WHERE  C0.NAME IN {schemas}
               AND B0.tbl_type IN ( 'EXTERNAL_TABLE', 'MANAGED_TABLE' )
        GROUP BY C0.NAME, B0.tbl_name
    """).format(schemas=SUPPORTED_HIVE_SCHEMA_SQL_IN_CLAUSE)

    LOGGER.info('SQL query: %s', sql_owner)
    tmp_folder = '/var/tmp/amundsen/table_owner'
    node_files_folder = f'{tmp_folder}/nodes'
    relationship_files_folder = f'{tmp_folder}/relationships'

    hwm_extractor = SQLAlchemyExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=hwm_extractor, loader=csv_loader, transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        f'extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': connection_string(),
        f'extractor.sqlalchemy.{SQLAlchemyExtractor.EXTRACT_SQL}': sql_owner,
        'extractor.sqlalchemy.model_class': 'databuilder.models.table_owner.TableOwner',
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        'publisher.neo4j.job_publish_tag': 'test_hive_owner'  # TO-DO unique tag must be added
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job

def create_table_last_update_job():
    """
    Launches data builder job that extracts table last update info from MySQL Hive metastore database,
    and publishes to Neo4j.
    """
    sql_last_update = textwrap.dedent("""
        SELECT
            DBS.NAME as `schema`,
            TBL_NAME as table_name,
            MAX(PARTITIONS.CREATE_TIME) as last_updated_time_epoch
        FROM TBLS
        JOIN DBS ON TBLS.DB_ID = DBS.DB_ID
        JOIN PARTITIONS ON TBLS.TBL_ID = PARTITIONS.TBL_ID
        WHERE  DBS.NAME IN {schemas}
            AND TBLS.tbl_type IN ( 'EXTERNAL_TABLE', 'MANAGED_TABLE' )
            AND TBL_NAME NOT REGEXP '^[0-9]+'
        GROUP BY `schema`, table_name
        ORDER BY `schema`, table_name
    """).format(schemas=SUPPORTED_HIVE_SCHEMA_SQL_IN_CLAUSE)

    tmp_folder = '/var/tmp/amundsen/table_last_update'
    node_files_folder = f'{tmp_folder}/nodes'
    relationship_files_folder = f'{tmp_folder}/relationships'

    hwm_extractor = SQLAlchemyExtractor()
    csv_loader = FsNeo4jCSVLoader()
    task = DefaultTask(extractor=hwm_extractor, loader=csv_loader, transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        f'extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': connection_string(),
        f'extractor.sqlalchemy.{SQLAlchemyExtractor.EXTRACT_SQL}': sql_last_update,
        'extractor.sqlalchemy.model_class': 'databuilder.models.table_last_updated.TableLastUpdated',
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_CREATE_ONLY_NODES}': [DESCRIPTION_NODE_LABEL],
        'publisher.neo4j.job_publish_tag': 'test_hive_last_update'  # TO-DO unique tag must be added
    })

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job

def create_table_metadata_databuilder_job():
    """
    Launches data builder job that extracts table and column metadata from MySQL Hive metastore database,
    and publishes to Neo4j.
    @param kwargs:
    @return:
    """

    # Adding to where clause to scope schema, filter out temp tables which start with numbers and views
    where_clause_suffix = textwrap.dedent("""
        WHERE d.NAME IN {schemas}
         AND t.TBL_NAME NOT REGEXP '^[0-9]+'
         AND t.TBL_TYPE IN ( 'EXTERNAL_TABLE', 'MANAGED_TABLE' )
    """).format(schemas=SUPPORTED_HIVE_SCHEMA_SQL_IN_CLAUSE)

    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = f'{tmp_folder}/nodes/'
    relationship_files_folder = f'{tmp_folder}/relationships/'

    job_config = ConfigFactory.from_dict({
        f'extractor.hive_table_metadata.{HiveTableMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY}': where_clause_suffix,
        f'extractor.hive_table_metadata.extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': connection_string(),
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_CREATE_ONLY_NODES}': [DESCRIPTION_NODE_LABEL],
        'publisher.neo4j.job_publish_tag': 'test_hive'  # TO-DO unique tag must be added
    })

    job = DefaultJob(conf=job_config,
                     task=DefaultTask(extractor=HiveTableMetadataExtractor(), loader=FsNeo4jCSVLoader()),
                     publisher=Neo4jCsvPublisher())
    return job

def create_es_publisher_sample_job(elasticsearch_index_alias='table_search_index',
                                   elasticsearch_doc_type_key='table',
                                   model_name='databuilder.models.table_elasticsearch_document.TableESDocument',
                                   cypher_query=None,
                                   elasticsearch_mapping=None):
    """
    :param elasticsearch_index_alias:  alias for Elasticsearch used in
                                       amundsensearchlibrary/search_service/config.py as an index
    :param elasticsearch_doc_type_key: name the ElasticSearch index is prepended with. Defaults to `table` resulting in
                                       `table_search_index`
    :param model_name:                 the Databuilder model class used in transporting between Extractor and Loader
    :param cypher_query:               Query handed to the `Neo4jSearchDataExtractor` class, if None is given (default)
                                       it uses the `Table` query baked into the Extractor
    :param elasticsearch_mapping:      Elasticsearch field mapping "DDL" handed to the `ElasticsearchPublisher` class,
                                       if None is given (default) it uses the `Table` query baked into the Publisher
    """
    # loader saves data to this location and publisher reads it from here
    extracted_search_data_path = '/var/tmp/amundsen/search_data.json'

    task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                       extractor=Neo4jSearchDataExtractor(),
                       transformer=NoopTransformer())

    # elastic search client instance
    elasticsearch_client = es
    # unique name of new index in Elasticsearch
    elasticsearch_new_index_key = 'tables' + str(uuid.uuid4())

    job_config = ConfigFactory.from_dict({
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.GRAPH_URL_CONFIG_KEY}': neo4j_endpoint,
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.MODEL_CLASS_CONFIG_KEY}': model_name,
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.NEO4J_AUTH_USER}': neo4j_user,
        f'extractor.search_data.extractor.neo4j.{Neo4jExtractor.NEO4J_AUTH_PW}': neo4j_password,
        f'loader.filesystem.elasticsearch.{FSElasticsearchJSONLoader.FILE_PATH_CONFIG_KEY}': extracted_search_data_path,
        f'loader.filesystem.elasticsearch.{FSElasticsearchJSONLoader.FILE_MODE_CONFIG_KEY}': 'w',
        f'publisher.elasticsearch.{ElasticsearchPublisher.FILE_PATH_CONFIG_KEY}': extracted_search_data_path,
        f'publisher.elasticsearch.{ElasticsearchPublisher.FILE_MODE_CONFIG_KEY}': 'r',
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_CLIENT_CONFIG_KEY}':
            elasticsearch_client,
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_NEW_INDEX_CONFIG_KEY}':
            elasticsearch_new_index_key,
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_DOC_TYPE_CONFIG_KEY}':
            elasticsearch_doc_type_key,
        f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_ALIAS_CONFIG_KEY}':
            elasticsearch_index_alias,
    })

    # only optionally add these keys, so need to dynamically `put` them
    if cypher_query:
        job_config.put(f'extractor.search_data.{Neo4jSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY}',
                       cypher_query)
    if elasticsearch_mapping:
        job_config.put(f'publisher.elasticsearch.{ElasticsearchPublisher.ELASTICSEARCH_MAPPING_CONFIG_KEY}',
                       elasticsearch_mapping)

    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=ElasticsearchPublisher())
    return job

if __name__ == "__main__":
    # Uncomment next line to get INFO level logging
    # logging.basicConfig(level=logging.INFO)

    amundsen_databuilder_table_metadata_job = create_table_metadata_databuilder_job()
    amundsen_databuilder_table_metadata_job.launch()

    amundsen_hwm_job = create_table_wm_job(
        provide_context=True,
        templates_dict={'agg_func': 'max',
                        'watermark_type': '"high_watermark"',
                        'part_regex': '{{ ds }}'}
    )

    amundsen_lwm_job = create_table_wm_job(
        provide_context=True,
        templates_dict={'agg_func': 'min',
                        'watermark_type': '"low_watermark"',
                        'part_regex': '{{ ds }}'}
    )

    amundsen_hwm_job.launch()
    amundsen_lwm_job.launch()

    amundsen_owner_job = create_table_owner_job()
    amundsen_owner_job.launch()
    amundsen_last_update_job = create_table_last_update_job()
    amundsen_last_update_job.launch()

    job_es_table = create_es_publisher_sample_job(
        elasticsearch_index_alias='table_search_index',
        elasticsearch_doc_type_key='table',
        model_name='databuilder.models.table_elasticsearch_document.TableESDocument')
    job_es_table.launch()
