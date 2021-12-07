# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Any,
    Dict,
    Optional,
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import (
    NODE_KEY,
    NODE_LABEL,
    RELATION_END_KEY,
    RELATION_END_LABEL,
    RELATION_REVERSE_TYPE,
    RELATION_START_KEY,
    RELATION_START_LABEL,
    RELATION_TYPE,
)
from databuilder.models.user import User as UserMetadata
from databuilder.models.type_metadata import TypeMetadata

# Mandatory fields for Nebula Vertex
NEBULA_VERTEX_MANDATORY_FIELDS = {
    UserMetadata.USER_NODE_LABEL: {
        "is_active": {
            "type": UserMetadata.__init__.__annotations__["is_active"],
            "Default": True
        },
        "user_id": {
            "type": str,
            "Default": ""
        },
        "manager_fullname": {
            "type": str,
            "Default": ""
        },
        "display_name": {
            "type": str,
            "Default": ""
        }
    },
    TypeMetadata.NODE_LABEL: {
        "sort_order": {
            "type": int,
            "Default": 0
        }
    }
}


def serialize_node(node: Optional[GraphNode]) -> Dict[str, Any]:
    if node is None:
        return {}
    tag = node.label
    node_dict = {NODE_LABEL: tag, NODE_KEY: node.key}
    for key, value in node.attributes.items():
        property_type = _get_property_type(value)
        formatted_key = f'{key}:{property_type}'
        node_dict[formatted_key] = value
    if tag in NEBULA_VERTEX_MANDATORY_FIELDS:
        for prop in NEBULA_VERTEX_MANDATORY_FIELDS[tag].keys():
            if prop not in node_dict:
                value = NEBULA_VERTEX_MANDATORY_FIELDS[tag][prop]["Default"]
                property_type = _get_property_type(value)
                formatted_key = f'{prop}:{property_type}'
                node_dict[formatted_key] = value
    return node_dict


def serialize_relationship(
        relationship: Optional[GraphRelationship]) -> Dict[str, Any]:
    if relationship is None:
        return {}

    relationship_dict = {
        RELATION_START_KEY: relationship.start_key,
        RELATION_START_LABEL + ":string": relationship.start_label,
        RELATION_END_KEY: relationship.end_key,
        RELATION_END_LABEL + ":string": relationship.end_label,
        RELATION_TYPE: relationship.type,
        RELATION_REVERSE_TYPE: relationship.reverse_type,
    }
    for key, value in relationship.attributes.items():
        property_type = _get_property_type(value)
        formatted_key = f'{key}:{property_type}'
        relationship_dict[formatted_key] = value

    return relationship_dict


def _get_property_type(value: Any) -> str:
    if isinstance(value, str):
        return "string"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int64"
    elif isinstance(value, float):
        return "float"

    return None
