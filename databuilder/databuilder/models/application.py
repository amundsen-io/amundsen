# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Iterator, Union

from amundsen_common.utils.atlas import (
    AtlasCommonParams, AtlasCommonTypes, AtlasTableTypes,
)
from amundsen_rds.models import RDSModel
from amundsen_rds.models.application import Application as RDSApplication, ApplicationTable as RDSApplicationTable

from databuilder.models.atlas_entity import AtlasEntity
from databuilder.models.atlas_relationship import AtlasRelationship
from databuilder.models.atlas_serializable import AtlasSerializable
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.table_serializable import TableSerializable
from databuilder.serializers.atlas_serializer import get_entity_attrs
from databuilder.utils.atlas import AtlasRelationshipTypes, AtlasSerializedEntityOperation


class Application(GraphSerializable, TableSerializable, AtlasSerializable):
    """
    Application-table matching model

    Application represent the applications that generate tables
    """

    APPLICATION_LABEL = 'Application'

    APPLICATION_KEY_FORMAT = 'application://{application_type}/{database}/{table}'
    APPLICATION_ID_FORMAT = '{application_type}.{database}.{table}'
    APPLICATION_DESCRIPTION_FORMAT = '{application_type} application for {database}.{table}'

    # Hardcode Airflow configuration values for backwards compatibility
    AIRFLOW_APPLICATION_KEY_FORMAT = 'application://{cluster}.airflow/{dag}/{task}'
    AIRFLOW_APPLICATION_ID_FORMAT = '{dag}/{task}'
    AIRFLOW_APPLICATION_DESCRIPTION_FORMAT = 'Airflow with id {id}'

    APPLICATION_URL_NAME = 'application_url'
    APPLICATION_NAME = 'name'
    APPLICATION_ID = 'id'
    APPLICATION_DESCRIPTION = 'description'
    APPLICATION_TABLE_RELATION_TYPE = 'GENERATES'
    TABLE_APPLICATION_RELATION_TYPE = 'DERIVED_FROM'

    def __init__(self,
                 task_id: str,
                 dag_id: str,
                 application_url_template: str,
                 db_name: str = 'hive',
                 cluster: str = 'gold',
                 schema: str = '',
                 table_name: str = '',
                 application_type: str = 'Airflow',
                 exec_date: str = '',
                 ) -> None:
        # todo: need to modify this hack
        self.application_url = application_url_template.format(dag_id=dag_id)
        self.database = db_name
        self.cluster = cluster
        self.schema = schema
        self.table = table_name
        self.dag = dag_id
        self.application_type = application_type
        self.task = task_id

        application_id_format = Application.APPLICATION_ID_FORMAT
        application_key_format = Application.APPLICATION_KEY_FORMAT
        application_description_format = Application.APPLICATION_DESCRIPTION_FORMAT

        # The Application model was originally designed to only be compatible with Airflow
        # If the type is Airflow we must use the hardcoded Airflow constants for backwards compatibility
        if self.application_type.lower() == 'airflow':
            application_id_format = Application.AIRFLOW_APPLICATION_ID_FORMAT
            application_key_format = Application.AIRFLOW_APPLICATION_KEY_FORMAT
            application_description_format = Application.AIRFLOW_APPLICATION_DESCRIPTION_FORMAT

        self.application_id = application_id_format.format(
            dag=self.dag,
            task=self.task,
            table=self.table,
            database=self.database,
            application_type=self.application_type,
        )
        self.application_key = application_key_format.format(
            dag=self.dag,
            task=self.task,
            table=self.table,
            database=self.database,
            cluster=self.cluster,
            application_type=self.application_type,
        )

        self.application_description = application_description_format.format(
            dag=self.dag,
            task=self.task,
            table=self.table,
            database=self.database,
            cluster=self.cluster,
            id=self.application_id,
            application_type=self.application_type,
        )

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()
        self._record_iter = self._create_record_iterator()
        self._atlas_entity_iterator = self._create_next_atlas_entity()
        self._atlas_relation_iterator = self._create_atlas_relation_iterator()

    def create_next_node(self) -> Union[GraphNode, None]:
        # creates new node
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Union[GraphRelationship, None]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def create_next_record(self) -> Union[RDSModel, None]:
        try:
            return next(self._record_iter)
        except StopIteration:
            return None

    def get_table_model_key(self) -> str:
        # returns formatted string for table name
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database,
                                                     schema=self.schema,
                                                     tbl=self.table,
                                                     cluster=self.cluster)

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create an application node
        :return:
        """
        application_node = GraphNode(
            key=self.application_key,
            label=Application.APPLICATION_LABEL,
            attributes={
                Application.APPLICATION_URL_NAME: self.application_url,
                Application.APPLICATION_NAME: self.application_type,
                Application.APPLICATION_DESCRIPTION: self.application_description,
                Application.APPLICATION_ID: self.application_id
            }
        )
        yield application_node

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relations between application and table nodes
        :return:
        """
        graph_relationship = GraphRelationship(
            start_key=self.get_table_model_key(),
            start_label=TableMetadata.TABLE_NODE_LABEL,
            end_key=self.application_key,
            end_label=Application.APPLICATION_LABEL,
            type=Application.TABLE_APPLICATION_RELATION_TYPE,
            reverse_type=Application.APPLICATION_TABLE_RELATION_TYPE,
            attributes={}
        )
        yield graph_relationship

    def _create_record_iterator(self) -> Iterator[RDSModel]:
        application_record = RDSApplication(
            rk=self.application_key,
            application_url=self.application_url,
            name=self.application_type,
            id=self.application_id,
            description=self.application_description
        )
        yield application_record

        application_table_record = RDSApplicationTable(
            rk=self.get_table_model_key(),
            application_rk=self.application_key,
        )
        yield application_table_record

    def create_next_atlas_entity(self) -> Union[AtlasEntity, None]:
        try:
            return next(self._atlas_entity_iterator)
        except StopIteration:
            return None

    def _create_next_atlas_entity(self) -> Iterator[AtlasEntity]:
        group_attrs_mapping = [
            (AtlasCommonParams.qualified_name, self.application_key),
            ('name', self.application_type),
            ('id', self.application_id),
            ('description', self.application_description),
            ('application_url', self.application_url)
        ]

        entity_attrs = get_entity_attrs(group_attrs_mapping)

        entity = AtlasEntity(
            typeName=AtlasCommonTypes.application,
            operation=AtlasSerializedEntityOperation.CREATE,
            relationships=None,
            attributes=entity_attrs,
        )

        yield entity

    def create_next_atlas_relation(self) -> Union[AtlasRelationship, None]:
        try:
            return next(self._atlas_relation_iterator)
        except StopIteration:
            return None

    def _create_atlas_relation_iterator(self) -> Iterator[AtlasRelationship]:
        relationship = AtlasRelationship(
            relationshipType=AtlasRelationshipTypes.table_application,
            entityType1=AtlasTableTypes.table,
            entityQualifiedName1=self.get_table_model_key(),
            entityType2=AtlasCommonTypes.application,
            entityQualifiedName2=self.application_key,
            attributes={}
        )

        yield relationship
