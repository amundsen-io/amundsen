from typing import (
    Iterator, Optional, Dict
)
from datetime import datetime

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.serializers.atlas_serializer import get_entity_attrs


class Score(GraphSerializable):
    LABELS_PERMITTED_TO_HAVE_SCORE = ['Table']

    SCORE_NODE_KEY = "{table_key}/score"
    SCORE_NODE_LABEL = 'Score'
    SCORE_NODE_SCORE= 'score'
    SCORE_NODE_SCORE_METADATA= 'score_metadata'
    SCORE_NODE_SCORE_DATE = 'score_date'
    SCORE_NODE_SCORE_VERSION = 'score_version'
    SCORE_RELATION_TYPE = 'SCORE'
    SCORE_OF_OBJECT_RELATION_TYPE = 'SCORE_OF'

    def __init__(self,
                 start_label: str,
                 start_key: str,
                 score: float,
                 score_metadata: Dict[str,str],
                 score_dt: datetime,
                 score_version: str
                 ) -> None:
        if start_label not in Score.LABELS_PERMITTED_TO_HAVE_SCORE:
            raise Exception(f'scores for {start_label} are not supported')
        self.start_label = start_label
        self.start_key = start_key
        self.score = score
        self.score_metadata = score_metadata
        self.score_dt = score_dt
        self.score_version = score_version

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()


    def __repr__(self) -> str:
        return f'Score({self.start_label!r}, {self.start_key!r}, {self.score!r}, {self.score_dt!r}, {self.score_version!r})'

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        yield GraphNode(
            key=self.get_score_key(),
            label=self.SCORE_NODE_LABEL,
            attributes={
                self.SCORE_NODE_SCORE: self.score,
                self.SCORE_NODE_SCORE_METADATA: self.score_metadata,
                self.SCORE_NODE_SCORE_DATE: self.score_dt,
                self.SCORE_NODE_SCORE_VERSION: self.score_version,
            }
        )

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=self.start_label,
            start_key=self.start_key,
            end_label=self.SCORE_NODE_LABEL,
            end_key=self.get_score_key(),
            type=self.SCORE_RELATION_TYPE,
            reverse_type=self.SCORE_OF_OBJECT_RELATION_TYPE,
            attributes={}
        )

    def get_score_key(self) -> str:
        return Score.SCORE_NODE_KEY.format(table_key=self.start_key)