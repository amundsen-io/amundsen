# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Iterator, Union

from amundsen_common.utils.atlas import AtlasCommonParams, AtlasCommonTypes

from databuilder.models.atlas_entity import AtlasEntity
from databuilder.models.atlas_relationship import AtlasRelationship
from databuilder.models.atlas_serializable import AtlasSerializable
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.serializers.atlas_serializer import get_entity_attrs
from databuilder.utils.atlas import AtlasRelationshipTypes, AtlasSerializedEntityOperation


class ResourceReport(GraphSerializable, AtlasSerializable):
    """
    Resource Report matching model

    Report represents a document that can be linked to any resource (like a table) in Amundsen.

    Example would be Pandas Profiling HTML report containing full advanced profile of a table.
    """

    RESOURCE_REPORT_LABEL = 'Report'

    RESOURCE_REPORT_NAME = 'name'
    RESOURCE_REPORT_URL = 'url'

    REPORT_KEY_FORMAT = '{resource_uri}/_report/{report_name}'

    REPORT_RESOURCE_RELATION_TYPE = 'REFERS_TO'
    RESOURCE_REPORT_RELATION_TYPE = 'HAS_REPORT'

    def __init__(self,
                 name: str,
                 url: str,
                 resource_uri: str,
                 resource_label: str,  # for example 'Table'
                 ) -> None:
        self.report_name = name
        self.report_url = url

        self.resource_uri = resource_uri
        self.resource_label = resource_label

        self.resource_report_key = self.get_resource_model_key()

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()
        self._atlas_entity_iterator = self._create_next_atlas_entity()
        self._atlas_relation_iterator = self._create_atlas_relation_iterator()

    def get_resource_model_key(self) -> str:
        return ResourceReport.REPORT_KEY_FORMAT.format(resource_uri=self.resource_uri, report_name=self.report_name)

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

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create an application node
        :return:
        """
        report_node = GraphNode(
            key=self.resource_report_key,
            label=ResourceReport.RESOURCE_REPORT_LABEL,
            attributes={
                ResourceReport.RESOURCE_REPORT_NAME: self.report_name,
                ResourceReport.RESOURCE_REPORT_URL: self.report_url
            }
        )

        yield report_node

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relations between application and table nodes
        :return:
        """
        graph_relationship = GraphRelationship(
            start_key=self.resource_uri,
            start_label=self.resource_label,
            end_key=self.resource_report_key,
            end_label=ResourceReport.RESOURCE_REPORT_LABEL,
            type=ResourceReport.RESOURCE_REPORT_RELATION_TYPE,
            reverse_type=ResourceReport.REPORT_RESOURCE_RELATION_TYPE,
            attributes={}
        )

        yield graph_relationship

    def create_next_atlas_entity(self) -> Union[AtlasEntity, None]:
        try:
            return next(self._atlas_entity_iterator)
        except StopIteration:
            return None

    def _create_next_atlas_entity(self) -> Iterator[AtlasEntity]:
        group_attrs_mapping = [
            (AtlasCommonParams.qualified_name, self.resource_report_key),
            ('name', self.report_name),
            ('url', self.report_url)
        ]

        entity_attrs = get_entity_attrs(group_attrs_mapping)

        entity = AtlasEntity(
            typeName=AtlasCommonTypes.resource_report,
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
            relationshipType=AtlasRelationshipTypes.referenceable_report,
            entityType1=self.resource_label,
            entityQualifiedName1=self.resource_uri,
            entityType2=AtlasCommonTypes.resource_report,
            entityQualifiedName2=self.resource_report_key,
            attributes={}
        )

        yield relationship
