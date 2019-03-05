import logging
import time

from neo4j.v1 import GraphDatabase, BoltStatementResult  # noqa: F401
from pyhocon import ConfigFactory  # noqa: F401
from pyhocon import ConfigTree  # noqa: F401
from typing import Dict, Iterable, Any  # noqa: F401

from databuilder import Scoped
from databuilder.task.base_task import Task  # noqa: F401
from databuilder.publisher.neo4j_csv_publisher import JOB_PUBLISH_TAG


# A end point for Neo4j e.g: bolt://localhost:9999
NEO4J_END_POINT_KEY = 'neo4j_endpoint'
NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'
NEO4J_USER = 'neo4j_user'
NEO4J_PASSWORD = 'neo4j_password'

TARGET_NODES = "target_nodes"
TARGET_RELATIONS = "target_relations"
BATCH_SIZE = "batch_size"
# Staleness max percentage. Safety net to prevent majority of data being deleted.
STALENESS_MAX_PCT = "staleness_max_pct"
# Staleness max percentage per LABEL/TYPE. Safety net to prevent majority of data being deleted.
STALENESS_PCT_MAX_DICT = "staleness_max_pct_dict"

DEFAULT_CONFIG = ConfigFactory.from_dict({BATCH_SIZE: 100,
                                          NEO4J_MAX_CONN_LIFE_TIME_SEC: 50,
                                          STALENESS_MAX_PCT: 5,
                                          TARGET_NODES: [],
                                          TARGET_RELATIONS: [],
                                          STALENESS_PCT_MAX_DICT: {}})

LOGGER = logging.getLogger(__name__)


class Neo4jStalenessRemovalTask(Task):
    """
    A Specific task that is to remove stale nodes and relations in Neo4j.
    It will use "published_tag" attribute assigned from Neo4jCsvPublisher and if "published_tag" is different from
    the one it is getting it from the config, it will regard the node/relation as stale.
    Not all resource is being published by Neo4jCsvPublisher and you can only set specific LABEL of the node or TYPE
    of relation to perform this deletion.

    """

    def __init__(self):
        # type: () -> None
        pass

    def get_scope(self):
        # type: () -> str
        return 'task.remove_stale_data'

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = Scoped.get_scoped_conf(conf, self.get_scope())\
            .with_fallback(conf)\
            .with_fallback(DEFAULT_CONFIG)
        self.target_nodes = set(conf.get_list(TARGET_NODES))
        self.target_relations = set(conf.get_list(TARGET_RELATIONS))
        self.batch_size = conf.get_int(BATCH_SIZE)
        self.staleness_pct = conf.get_int(STALENESS_MAX_PCT)
        self.staleness_pct_dict = conf.get(STALENESS_PCT_MAX_DICT)
        self.publish_tag = conf.get_string(JOB_PUBLISH_TAG)
        self._driver = \
            GraphDatabase.driver(conf.get_string(NEO4J_END_POINT_KEY),
                                 max_connection_life_time=conf.get_int(NEO4J_MAX_CONN_LIFE_TIME_SEC),
                                 auth=(conf.get_string(NEO4J_USER), conf.get_string(NEO4J_PASSWORD)))

        self._session = self._driver.session()

    def run(self):
        # type: () -> None
        """
        First, performs a safety check to make sure this operation would not delete more than a threshold where
        default threshold is 5%. Once it passes a safety check, it will first delete stale nodes, and then stale
        relations.
        :return:
        """
        self.validate()
        self._delete_stale_nodes()
        self._delete_stale_relations()

    def validate(self):
        """
        Validation method. Focused on limit the risk on deleting nodes and relations.
         - Check if deleted nodes will be within 10% of total nodes.
        :return:
        """
        # type: () -> None
        self._validate_node_staleness_pct()
        self._validate_relation_staleness_pct()

    def _delete_stale_nodes(self):
        statement = """
        MATCH (n:{type})
        WHERE n.published_tag <> $published_tag
        OR NOT EXISTS(n.published_tag)
        WITH n LIMIT $batch_size
        DETACH DELETE (n)
        RETURN COUNT(*) as count;
        """
        self._batch_delete(statement=statement, targets=self.target_nodes)

    def _delete_stale_relations(self):
        statement = """
        MATCH ()-[r:{type}]-()
        WHERE r.published_tag <> $published_tag
        OR NOT EXISTS(r.published_tag)
        WITH r LIMIT $batch_size
        DELETE r
        RETURN count(*) as count;
        """
        self._batch_delete(statement=statement, targets=self.target_relations)

    def _batch_delete(self, statement, targets):
        """
        Performing huge amount of deletion could degrade Neo4j performance. Therefore, it's taking batch deletion here.
        :param statement:
        :param targets:
        :return:
        """
        for t in targets:
            LOGGER.info('Deleting stale data of {} with batch size {}'.format(t, self.batch_size))
            total_count = 0
            while True:
                result = self._execute_cypher_query(statement=statement.format(type=t),
                                                    param_dict={'batch_size': self.batch_size,
                                                                'published_tag': self.publish_tag}).single()
                count = result['count']
                total_count = total_count + count
                if count == 0:
                    break
            LOGGER.info('Deleted {} stale data of {}'.format(total_count, t))

    def _validate_staleness_pct(self, total_records, stale_records, types):
        # type: (Iterable[Dict[str, Any]], Iterable[Dict[str, Any]], Iterable[str]) -> None

        total_count_dict = {record['type']: int(record['count']) for record in total_records}

        for record in stale_records:
            type_str = record['type']
            if type_str not in types:
                continue

            stale_count = record['count']
            if stale_count == 0:
                continue

            node_count = total_count_dict[type_str]
            stale_pct = stale_count * 100 / node_count

            threshold = self.staleness_pct_dict.get(type_str, self.staleness_pct)
            if stale_pct >= threshold:
                raise Exception('Staleness percentage of {} is {} %. Stopping due to over threshold {} %'
                                .format(type_str, stale_pct, threshold))

    def _validate_node_staleness_pct(self):
        # type: () -> None

        total_nodes_statement = """
        MATCH (n)
        WITH DISTINCT labels(n) as node, count(*) as count
        RETURN head(node) as type, count
        """

        stale_nodes_statement = """
        MATCH (n)
        WHERE n.published_tag <> $published_tag
        OR NOT EXISTS(n.published_tag)
        WITH DISTINCT labels(n) as node, count(*) as count
        RETURN head(node) as type, count
        """

        total_records = self._execute_cypher_query(statement=total_nodes_statement)
        stale_records = self._execute_cypher_query(statement=stale_nodes_statement,
                                                   param_dict={'published_tag': self.publish_tag})
        self._validate_staleness_pct(total_records=total_records,
                                     stale_records=stale_records,
                                     types=self.target_nodes)

    def _validate_relation_staleness_pct(self):
        # type: () -> None
        total_relations_statement = """
        MATCH ()-[r]-()
        RETURN type(r) as type, count(*) as count;
        """

        stale_relations_statement = """
        MATCH ()-[r]-()
        WHERE r.published_tag <> $published_tag
        OR NOT EXISTS(r.published_tag)
        RETURN type(r) as type, count(*) as count
        """

        total_records = self._execute_cypher_query(statement=total_relations_statement)
        stale_records = self._execute_cypher_query(statement=stale_relations_statement,
                                                   param_dict={'published_tag': self.publish_tag})
        self._validate_staleness_pct(total_records=total_records,
                                     stale_records=stale_records,
                                     types=self.target_relations)

    def _execute_cypher_query(self, statement, param_dict={}):
        # type: (str, Dict[str, Any]) -> Iterable[Dict[str, Any]]
        LOGGER.info('Executing Cypher query: {statement} with params {params}: '.format(statement=statement,
                                                                                        params=param_dict))
        start = time.time()
        try:
            with self._driver.session() as session:
                return session.run(statement, **param_dict)

        finally:
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug('Cypher query execution elapsed for {} seconds'.format(time.time() - start))
