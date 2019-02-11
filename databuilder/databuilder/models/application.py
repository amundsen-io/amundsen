from typing import Any, Dict, List, Union  # noqa: F401

from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable, NODE_KEY, \
    NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE

from databuilder.models.table_metadata import TableMetadata


class Application(Neo4jCsvSerializable):
    """
    Application-table matching model (Airflow task and table)
    """

    APPLICATION_LABEL = 'Application'
    APPLICATION_KEY_FORMAT = 'application://{cluster}.airflow/{dag}/{task}'
    APPLICATION_URL_NAME = 'application_url'
    APPLICATION_NAME = 'name'
    APPLICATION_ID = 'id'
    APPLICATION_ID_FORMAT = '{dag_id}/{task_id}'
    APPLICATION_DESCRIPTION = 'description'
    APPLICATION_TYPE = 'Airflow'

    APPLICATION_TABLE_RELATION_TYPE = 'GENERATES'
    TABLE_APPLICATION_RELATION_TYPE = 'DERIVED_FROM'

    def __init__(self,
                 task_id,  # type: str
                 dag_id,  # type: str,
                 application_url_template,  # type: str
                 exec_date,  # type: str
                 ):
        # type: (...) -> None
        self.task = task_id

        # todo: need to modify this hack
        self.application_url = application_url_template.format(dag_id=dag_id)
        self.database, self.schema, self.table = task_id.split('.')

        self.dag = dag_id

        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self):
        # type: (...) -> Union[Dict[str, Any], None]
        # creates new node
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self):
        # type: (...) -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def get_table_model_key(self):
        # type: (...) -> str
        # returns formatted string for table name
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     schema=self.schema,
                                                     tbl=self.table,
                                                     cluster='gold')

    def get_application_model_key(self):
        # type: (...) -> str
        # returns formatting string for application of type dag
        return Application.APPLICATION_KEY_FORMAT.format(cluster='gold',
                                                         dag=self.dag,
                                                         task=self.task)

    def create_nodes(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of Neo4j node records
        :return:
        """
        results = []

        results.append({
            NODE_KEY: self.get_application_model_key(),
            NODE_LABEL: Application.APPLICATION_LABEL,
            Application.APPLICATION_URL_NAME: self.application_url,
            Application.APPLICATION_NAME: Application.APPLICATION_TYPE,
            Application.APPLICATION_DESCRIPTION:
                '{app_type} with id {id}'.format(app_type=Application.APPLICATION_TYPE,
                                                 id=Application.APPLICATION_ID_FORMAT.format(dag_id=self.dag,
                                                                                             task_id=self.task)),
            Application.APPLICATION_ID: Application.APPLICATION_ID_FORMAT.format(dag_id=self.dag,
                                                                                 task_id=self.task)
        })

        return results

    def create_relation(self):
        # type: () -> List[Dict[str, Any]]
        """
        Create a list of relation map between watermark record with original hive table
        :return:
        """
        results = [{
            RELATION_START_KEY: self.get_table_model_key(),
            RELATION_START_LABEL: TableMetadata.TABLE_NODE_LABEL,
            RELATION_END_KEY: self.get_application_model_key(),
            RELATION_END_LABEL: Application.APPLICATION_LABEL,
            RELATION_TYPE: Application.TABLE_APPLICATION_RELATION_TYPE,
            RELATION_REVERSE_TYPE: Application.APPLICATION_TABLE_RELATION_TYPE
        }]

        return results
