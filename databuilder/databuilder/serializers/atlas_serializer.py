# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Any, Dict, Optional,
)

from databuilder.models.atlas_entity import AtlasEntity
from databuilder.models.atlas_relationship import AtlasRelationship
from common.amundsen_common.utils.atlas import AtlasSerializedRelationshipFields, AtlasSerializedEntityFields


def serialize_entity(entity: Optional[AtlasEntity]) -> Dict[str, Any]:
    if entity is None:
        return {}

    entity_dict = {
        AtlasSerializedEntityFields.type_name: entity.typeName,
        AtlasSerializedEntityFields.operation: entity.operation,
        AtlasSerializedEntityFields.relationships: entity.relationships
    }
    for key, value in entity.attributes.items():
        entity_dict[key] = value
    return entity_dict


def serialize_relationship(relationship: Optional[AtlasRelationship]) -> Dict[str, Any]:
    if relationship is None:
        return {}

    relationship_dict = {
        AtlasSerializedRelationshipFields.relation_type: relationship.relationshipType,
        AtlasSerializedRelationshipFields.entity_type_1: relationship.entityType1,
        AtlasSerializedRelationshipFields.qualified_name_1: relationship.entityQualifiedName1,
        AtlasSerializedRelationshipFields.entity_type_2: relationship.entityType2,
        AtlasSerializedRelationshipFields.qualified_name_2: relationship.entityQualifiedName2,
    }
    for key, value in relationship.attributes.items():
        relationship_dict[key] = value

    return relationship_dict
