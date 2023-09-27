# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Iterator, Optional,
)

# from amundsen_common.utils.atlas import AtlasCommonParams, AtlasTableTypes
# from amundsen_rds.models import RDSModel
# from amundsen_rds.models.table import SnowflakeTableShare as RDSSnowflakeTableShare

# from databuilder.models.atlas_entity import AtlasEntity
# from databuilder.models.atlas_relationship import AtlasRelationship
# from databuilder.models.atlas_serializable import AtlasSerializable
from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_metadata import TableMetadata
# from databuilder.models.table_serializable import TableSerializable
# from databuilder.serializers.atlas_serializer import get_entity_attrs
# from databuilder.utils.atlas import AtlasRelationshipTypes, AtlasSerializedEntityOperation


# class SnowflakeTableShare(GraphSerializable, TableSerializable, AtlasSerializable):
class SnowflakeTableShare(GraphSerializable):
    SHARE_LABEL = 'Snowflakeshare'
    SHARE_KEY_FORMAT = 'snowflake://{owner_account}.{share_name}/_share'
    SHARE_TABLE_RELATION_TYPE = 'SNOWFLAKE_SHARE_OF'
    TABLE_SHARE_RELATION_TYPE = 'SNOWFLAKE_SHARE'

    LISTING_LABEL = 'Snowflakelisting'
    LISTING_KEY_FORMAT = 'snowflake://{listing_global_name}/_listing'
    LISTING_SHARE_RELATION_TYPE = 'SNOWFLAKE_LISTING_OF'
    SHARE_LISTING_RELATION_TYPE = 'SNOWFLAKE_LISTING'

    def __init__(self,
                 schema: str,
                 table_name: str,
                 cluster: str,
                 owner_account: str,
                 share_name: str,
                 share_kind: str,
                 data_exchange_name: str = None,
                 listing_global_name: str = None,
                 listing_name: str = None,
                 listing_title: str = None,
                 listing_subtitle: str = None,
                 listing_desc: str = None) -> None:
        self.database = 'snowflake'
        self.schema = schema
        self.table = table_name

        self.cluster = cluster if cluster else 'gold'
        self.owner_account = owner_account
        self.share_name = share_name
        self.share_kind = share_kind
        self.data_exchange_name = data_exchange_name
        self.listing_global_name = listing_global_name
        self.listing_name = listing_name
        self.listing_title = listing_title
        self.listing_subtitle = listing_subtitle
        self.listing_desc = listing_desc

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()
        # self._record_iter = self._create_record_iterator()
        # self._atlas_entity_iterator = self._create_next_atlas_entity()
        # self._atlas_relation_iterator = self._create_atlas_relation_iterator()

    def create_next_node(self) -> Optional[GraphNode]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    # def create_next_record(self) -> Union[RDSModel, None]:
    #     try:
    #         return next(self._record_iter)
    #     except StopIteration:
    #         return None

    def get_listing_model_key(self) -> str:
        return SnowflakeTableShare.LISTING_KEY_FORMAT.format(listing_global_name=self.listing_global_name.lower())

    def get_share_model_key(self) -> str:
        return SnowflakeTableShare.SHARE_KEY_FORMAT.format(owner_account=self.owner_account.lower(),
                                                           share_name=self.share_name.lower())

    def get_table_model_key(self) -> str:
        return TableMetadata.TABLE_KEY_FORMAT.format(db=self.database.lower(),
                                                     cluster=self.cluster.lower(),
                                                     schema=self.schema.lower(),
                                                     tbl=self.table.lower())

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        """
        Create a snowflake share node
        :return:
        """
        share_node = GraphNode(
            key=self.get_share_model_key(),
            label=SnowflakeTableShare.SHARE_LABEL,
            attributes={
                'owner_account': self.owner_account,
                'name': self.share_name
            }
        )
        yield share_node

        if self.listing_global_name:
            listing_node = GraphNode(
                key=self.get_listing_model_key(),
                label=SnowflakeTableShare.LISTING_LABEL,
                attributes={
                    'global_name': self.listing_global_name,
                    'name': self.listing_name,
                    'title': self.listing_title,
                    'subtitle': self.listing_subtitle,
                    'description': self.listing_desc
                }
            )
            yield listing_node

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        """
        Create relation map between the share and the table.  The table should exist already.
        :return:
        """
        table_share_relationship = GraphRelationship(
            start_label=SnowflakeTableShare.SHARE_LABEL,
            start_key=self.get_share_model_key(),
            end_label=TableMetadata.TABLE_NODE_LABEL,
            end_key=self.get_table_model_key(),
            type=SnowflakeTableShare.SHARE_TABLE_RELATION_TYPE,
            reverse_type=SnowflakeTableShare.TABLE_SHARE_RELATION_TYPE,
            attributes={}
        )
        yield table_share_relationship

        if self.listing_global_name:
            listing_share_relationship = GraphRelationship(
                start_label=SnowflakeTableShare.LISTING_LABEL,
                start_key=self.get_listing_model_key(),
                end_label=SnowflakeTableShare.SHARE_LABEL,
                end_key=self.get_share_model_key(),
                type=SnowflakeTableShare.LISTING_SHARE_RELATION_TYPE,
                reverse_type=SnowflakeTableShare.SHARE_LISTING_RELATION_TYPE,
                attributes={}
            )
            yield listing_share_relationship

    # def _create_record_iterator(self) -> Iterator[RDSModel]:
    #     record = RDSTableSource(
    #         rk=self.get_share_model_key(),
    #         source=self.source,
    #         source_type=self.source_type,
    #         table_rk=self.get_table_model_key()
    #     )
    #     yield record

    # def _create_atlas_source_entity(self) -> AtlasEntity:
    #     attrs_mapping = [
    #         (AtlasCommonParams.qualified_name, self.get_share_model_key()),
    #         ('share_name', self.share_name),
    #         ('displayName', self.share_name)
    #     ]

    #     entity_attrs = get_entity_attrs(attrs_mapping)

    #     entity = AtlasEntity(
    #         typeName=AtlasTableTypes.source,
    #         operation=AtlasSerializedEntityOperation.CREATE,
    #         attributes=entity_attrs,
    #         relationships=None
    #     )

    #     return entity

    # def create_next_atlas_relation(self) -> Union[AtlasRelationship, None]:
    #     try:
    #         return next(self._atlas_relation_iterator)
    #     except StopIteration:
    #         return None

    # def _create_atlas_relation_iterator(self) -> Iterator[AtlasRelationship]:
    #     relationship = AtlasRelationship(
    #         relationshipType=AtlasRelationshipTypes.table_source,
    #         entityType1=AtlasTableTypes.source,
    #         entityQualifiedName1=self.get_source_model_key(),
    #         entityType2=AtlasTableTypes.table,
    #         entityQualifiedName2=self.get_metadata_model_key(),
    #         attributes={}
    #     )

    #     yield relationship

    # def _create_next_atlas_entity(self) -> Iterator[AtlasEntity]:
    #     yield self._create_atlas_source_entity()

    # def create_next_atlas_entity(self) -> Union[AtlasEntity, None]:
    #     try:
    #         return next(self._atlas_entity_iterator)
    #     except StopIteration:
    #         return None

    def __repr__(self) -> str:
        return f'SnowflakeTableShare({self.database!r}, \
                                     {self.cluster!r}, \
                                     {self.schema!r}, \
                                     {self.table!r}, \
                                     {self.share_name!r}, \
                                     {self.listing_global_name!r} \
                                     {self.listing_title!r}, \
                                     {self.listing_subtitle!r}, \
                                     {self.listing_desc!r})'
