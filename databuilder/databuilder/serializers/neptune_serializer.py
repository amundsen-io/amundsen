# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import (
    Any, Dict, List, Optional,
)

import six

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship

NEPTUNE_HEADER_ID = "~id"
NEPTUNE_HEADER_LABEL = "~label"
NEPTUNE_RELATIONSHIP_HEADER_FROM = "~from"
NEPTUNE_RELATIONSHIP_HEADER_TO = "~to"


# last seen property names
NEPTUNE_LAST_EXTRACTED_AT_NODE_PROPERTY_NAME = "last_extracted_datetime"
NEPTUNE_LAST_EXTRACTED_AT_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT = "{name}:Date(single)".format(
    name=NEPTUNE_LAST_EXTRACTED_AT_NODE_PROPERTY_NAME
)
NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME = "last_extracted_datetime"
NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT = "{name}:Date(single)".format(
    name=NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME
)
# Add a property showing where the the node or relationship comes from
NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME = "creation_type"
NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT = "{name}:String(single)".format(
    name=NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME
)
NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME = "creation_type"
NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT = "{name}:String".format(
    name=NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME
)

NEPTUNE_CREATION_TYPE_JOB = "job"


def convert_relationship(relationship: Optional[GraphRelationship]) -> List[Dict[str, Any]]:
    if relationship is None:
        return []

    if relationship.start_key == '' or relationship.end_key == '':
        return []

    relation_id = "{from_vertex_id}_{to_vertex_id}_{label}".format(
        from_vertex_id=relationship.start_key,
        to_vertex_id=relationship.end_key,
        label=relationship.type
    )
    relation_id_reverse = "{from_vertex_id}_{to_vertex_id}_{label}".format(
        from_vertex_id=relationship.end_key,
        to_vertex_id=relationship.start_key,
        label=relationship.reverse_type
    )
    current_string_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    forward_relationship_doc = {
        NEPTUNE_HEADER_ID: relation_id,
        NEPTUNE_RELATIONSHIP_HEADER_FROM: relationship.start_key,
        NEPTUNE_RELATIONSHIP_HEADER_TO: relationship.end_key,
        NEPTUNE_HEADER_LABEL: relationship.type,
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: current_string_time,
        NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
    }

    reverse_relationship_doc = {
        NEPTUNE_HEADER_ID: relation_id_reverse,
        NEPTUNE_RELATIONSHIP_HEADER_FROM: relationship.end_key,
        NEPTUNE_RELATIONSHIP_HEADER_TO: relationship.start_key,
        NEPTUNE_HEADER_LABEL: relationship.reverse_type,
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: current_string_time,
        NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
    }

    for key, value in relationship.attributes.items():
        neptune_value_type = _get_neptune_type_for_value(value)
        doc_key = "{key_name}:{neptune_value_type}(single)".format(
            key_name=key,
            neptune_value_type=neptune_value_type
        )
        forward_relationship_doc[doc_key] = value
        reverse_relationship_doc[doc_key] = value

    return [
        forward_relationship_doc,
        reverse_relationship_doc
    ]


def convert_node(node: Optional[GraphNode]) -> Dict[str, Any]:
    if node is None:
        return {}

    if not node.key:
        return {}

    current_string_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    node_dict = {
        NEPTUNE_HEADER_ID: node.key,
        NEPTUNE_HEADER_LABEL: node.label,
        NEPTUNE_LAST_EXTRACTED_AT_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: current_string_time,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
    }

    for attr_key, attr_value in node.attributes.items():
        neptune_value_type = _get_neptune_type_for_value(attr_value)
        doc_key = "{key_name}:{neptune_value_type}(single)".format(
            key_name=attr_key,
            neptune_value_type=neptune_value_type
        )
        if doc_key not in node_dict:
            node_dict[doc_key] = attr_value

    return node_dict


def _get_neptune_type_for_value(value: Any) -> Optional[str]:
    if isinstance(value, six.string_types):
        return "String"
    elif isinstance(value, bool):
        return "Bool"
    elif isinstance(value, six.integer_types):
        return "Long"
    elif isinstance(value, float):
        return "Double"

    return None
