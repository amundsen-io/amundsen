# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Union  # noqa: F401

from amundsen_common.utils.atlas_utils import AtlasCommonParams
from databuilder.models.atlas_entity import AtlasEntity
from databuilder.models.atlas_relationship import AtlasRelationship


class AtlasSerializable(object, metaclass=abc.ABCMeta):
    """
    A Serializable abstract class asks subclass to implement next node or
    next relation in dict form so that it can be serialized to CSV file.

    Any model class that needs to be pushed to a graph database should inherit this class.
    """

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def create_next_atlas_entity(self) -> Union[AtlasEntity, None]:
        """
        Creates GraphNode the process that consumes this class takes the output
        serializes to the desired graph database.

        :return: a GraphNode or None if no more records to serialize
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_next_atlas_relation(self) -> Union[AtlasRelationship, None]:
        """
        Creates GraphRelationship the process that consumes this class takes the output
        serializes to the desired graph database.

        :return: a GraphRelationship or None if no more record to serialize
        """
        raise NotImplementedError

    def _validate_atlas_entity(self, entity: AtlasEntity) -> None:
        entity_type, operation, relation, attributes = entity

        if entity_type is None:
            raise RuntimeError('Required header missing: entityType')
        if operation is None:
            raise RuntimeError('Required header missing: operation')

        if attributes is None:
            raise RuntimeError('Required header missing: attributes')

        if AtlasCommonParams.qualified_name not in attributes:
            raise RuntimeError(f'Attribute {AtlasCommonParams.qualified_name} is missing')

    def _validate_atlas_relation(self, relation: AtlasRelationship) -> None:
        relation_type, entity_type_1, qualified_name_1, entity_type_2, qualified_name_2, _ = relation

        if relation_type is None:
            raise RuntimeError(f'Required header missing. Missing: {AtlasRelationship.relationshipType}')

        if entity_type_1 is None:
            raise RuntimeError(f'Required header missing. Missing: {AtlasRelationship.entityType1}')

        if qualified_name_1 is None:
            raise RuntimeError(f'Required header missing. Missing: {AtlasRelationship.entityQualifiedName1}')

        if entity_type_2 is None:
            raise RuntimeError(f'Required header missing. Missing: {AtlasRelationship.entityType2}')

        if qualified_name_2 is None:
            raise RuntimeError(f'Required header missing. Missing: {AtlasRelationship.entityQualifiedName2}')

    def next_atlas_entity(self) -> Union[AtlasEntity, None]:
        entity_dict = self.create_next_atlas_entity()
        if not entity_dict:
            return None

        self._validate_atlas_entity(entity_dict)
        return entity_dict

    def next_atlas_relation(self) -> Union[AtlasRelationship, None]:
        relation_dict = self.create_next_atlas_relation()
        if not relation_dict:
            return None

        self._validate_atlas_relation(relation_dict)
        return relation_dict
