# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, Any, Union, Iterator

from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY)
from databuilder.models.schema.schema_constant import SCHEMA_NODE_LABEL, SCHEMA_NAME_ATTR
from databuilder.models.table_metadata import DescriptionMetadata


class SchemaModel(Neo4jCsvSerializable):

    def __init__(self,
                 schema_key: str,
                 schema: str,
                 description: str=None,
                 description_source: str=None,
                 **kwargs: Any
                 ) -> None:
        self._schema_key = schema_key
        self._schema = schema
        self._description = DescriptionMetadata.create_description_metadata(text=description,
                                                                            source=description_source) \
            if description else None
        self._node_iterator = self._create_node_iterator()
        self._relation_iterator = self._create_relation_iterator()

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[Dict[str, Any]]:
        yield {
            NODE_LABEL: SCHEMA_NODE_LABEL,
            NODE_KEY: self._schema_key,
            SCHEMA_NAME_ATTR: self._schema,
        }

        if self._description:
            yield self._description.get_node_dict(self._get_description_node_key())

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _get_description_node_key(self) -> str:
        desc = self._description.get_description_id() if self._description is not None else ''
        return '{}/{}'.format(self._schema_key, desc)

    def _create_relation_iterator(self) -> Iterator[Dict[str, Any]]:
        if self._description:
            yield self._description.get_relation(start_node=SCHEMA_NODE_LABEL,
                                                 start_key=self._schema_key,
                                                 end_key=self._get_description_node_key())
