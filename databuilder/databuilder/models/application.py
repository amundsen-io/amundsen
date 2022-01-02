# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Iterator, Optional, Union,
)

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


class GenericApplication(GraphSerializable, TableSerializable, AtlasSerializable):
    """
    An Application that generates or consumes a resource.
    """

    LABEL = 'Application'
    DEFAULT_KEY_FORMAT = 'application://{application_type}/{application_id}'

    APP_URL = 'application_url'
    APP_NAME = 'name'
    APP_ID = 'id'
    APP_DESCRIPTION = 'description'

    GENERATES_REL_TYPE = 'GENERATES'
    DERIVED_FROM_REL_TYPE = 'DERIVED_FROM'
    CONSUMES_REL_TYPE = 'CONSUMES'
    CONSUMED_BY_REL_TYPE = 'CONSUMED_BY'

    LABELS_PERMITTED_TO_HAVE_USAGE = ['Table']

    def __init__(self,
                 start_label: str,
                 start_key: str,
                 application_type: str,
                 application_id: str,
                 application_url: str,
                 application_description: Optional[str] = None,
                 app_key_override: Optional[str] = None,  # for bw-compatibility only
                 generates_resource: bool = True,
                 ) -> None:

        if start_label not in GenericApplication.LABELS_PERMITTED_TO_HAVE_USAGE:
            raise Exception(f'applications associated with {start_label} are not supported')

        self.start_label = start_label
        self.start_key = start_key
        self.application_type = application_type
        self.application_id = application_id
        self.application_url = application_url
        self.application_description = application_description
        self.application_key = app_key_override or GenericApplication.DEFAULT_KEY_FORMAT.format(
            application_type=self.application_type,
            application_id=self.application_id,
        )
        self.generates_resource = generates_resource

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

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create an application node
        :return:
        """
        attrs = {
            GenericApplication.APP_NAME: self.application_type,
            GenericApplication.APP_ID: self.application_id,
            GenericApplication.APP_URL: self.application_url,
        }
        if self.application_description:
            attrs[GenericApplication.APP_DESCRIPTION] = self.application_description

        yield GraphNode(
            key=self.application_key,
            label=GenericApplication.LABEL,
            attributes=attrs,
        )

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relations between application and table nodes
        :return:
        """
        graph_relationship = GraphRelationship(
            start_key=self.start_key,
            start_label=self.start_label,
            end_key=self.application_key,
            end_label=GenericApplication.LABEL,
            type=(GenericApplication.DERIVED_FROM_REL_TYPE if self.generates_resource
                  else GenericApplication.CONSUMED_BY_REL_TYPE),
            reverse_type=(GenericApplication.GENERATES_REL_TYPE if self.generates_resource
                          else GenericApplication.CONSUMES_REL_TYPE),
            attributes={}
        )
        yield graph_relationship

    # TODO: support consuming/producing relationships and multiple apps per resource
    def _create_record_iterator(self) -> Iterator[RDSModel]:
        yield RDSApplication(
            rk=self.application_key,
            application_url=self.application_url,
            name=self.application_type,
            id=self.application_id,
            description=self.application_description or '',
        )

        yield RDSApplicationTable(
            rk=self.start_key,
            application_rk=self.application_key,
        )

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
            ('description', self.application_description or ''),
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

    # TODO: support consuming/producing relationships and multiple apps per resource
    def _create_atlas_relation_iterator(self) -> Iterator[AtlasRelationship]:
        yield AtlasRelationship(
            relationshipType=AtlasRelationshipTypes.table_application,
            entityType1=AtlasTableTypes.table,
            entityQualifiedName1=self.start_key,
            entityType2=AtlasCommonTypes.application,
            entityQualifiedName2=self.application_key,
            attributes={}
        )


class AirflowApplication(GenericApplication):

    ID_FORMAT = '{dag}/{task}'
    KEY_FORMAT = 'application://{cluster}.airflow/{id}'
    DESCRIPTION_FORMAT = 'Airflow with id {id}'

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
                 generates_table: bool = True,
                 ) -> None:

        self.database = db_name
        self.cluster = cluster
        self.schema = schema
        self.table = table_name
        self.dag = dag_id
        self.task = task_id

        airflow_app_id = AirflowApplication.ID_FORMAT.format(dag=dag_id, task=task_id)
        GenericApplication.__init__(
            self,
            start_label=TableMetadata.TABLE_NODE_LABEL,
            start_key=self.get_table_model_key(),
            application_type=application_type,
            application_id=airflow_app_id,
            application_url=application_url_template.format(dag_id=dag_id),
            application_description=AirflowApplication.DESCRIPTION_FORMAT.format(id=airflow_app_id),
            app_key_override=AirflowApplication.KEY_FORMAT.format(cluster=cluster, id=airflow_app_id),
            generates_resource=generates_table,
        )

    def get_table_model_key(self) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(
            db=self.database,
            cluster=self.cluster,
            schema=self.schema,
            tbl=self.table,
        )


# Alias for backwards compatibility
Application = AirflowApplication
