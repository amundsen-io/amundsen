from collections import namedtuple

from typing import Iterable, Any, Union, Iterator, Dict, Set  # noqa: F401

# TODO: We could separate TagMetadata from table_metadata to own module
from databuilder.models.table_metadata import TagMetadata
from databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)


NodeTuple = namedtuple('KeyName', ['key', 'name', 'label'])
RelTuple = namedtuple('RelKeys', ['start_label', 'end_label', 'start_key', 'end_key', 'type', 'reverse_type'])


class DashboardMetadata(Neo4jCsvSerializable):
    """
    Dashboard metadata that contains dashboardgroup, tags, description, userid and lastreloadtime.
    It implements Neo4jCsvSerializable so that it can be serialized to produce
    Dashboard, Tag, Description, Lastreloadtime and relation of those. Additionally, it will create
    Dashboardgroup with relationships to Dashboard. If users exist in neo4j, it will create
    the relation between dashboard and user (owner).

    Lastreloadtime is the time when the Dashboard was last reloaded.
    """
    DASHBOARD_NODE_LABEL = 'Dashboard'
    DASHBOARD_KEY_FORMAT = '{dashboard_group}://{dashboard_name}'
    DASHBOARD_NAME = 'name'

    DASHBOARD_DESCRIPTION_NODE_LABEL = 'Description'
    DASHBOARD_DESCRIPTION = 'description'
    DASHBOARD_DESCRIPTION_FORMAT = '{dashboard_group}://{dashboard_name}/_description'
    DASHBOARD_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_DASHBOARD_RELATION_TYPE = 'DESCRIPTION_OF'

    DASHBOARD_GROUP_NODE_LABEL = 'Dashboardgroup'
    DASHBOARD_GROUP_KEY_FORMAT = 'dashboardgroup://{dashboard_group}'
    DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE = 'DASHBOARD'
    DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE = 'DASHBOARD_OF'

    DASHBOARD_LAST_RELOAD_TIME_NODE_LABEL = 'Lastreloadtime'
    DASHBOARD_LAST_RELOAD_TIME = 'value'
    DASHBOARD_LAST_RELOAD_TIME_FORMAT = '{dashboard_group}://{dashboard_name}/_lastreloadtime'
    DASHBOARD_LAST_RELOAD_TIME_RELATION_TYPE = 'LAST_RELOAD_TIME'
    LAST_RELOAD_TIME_DASHBOARD_RELATION_TYPE = 'LAST_RELOAD_TIME_OF'

    OWNER_NODE_LABEL = 'User'
    OWNER_KEY_FORMAT = '{user_id}'
    DASHBOARD_OWNER_RELATION_TYPE = 'OWNER'
    OWNER_DASHBOARD_RELATION_TYPE = 'OWNER_OF'
    OWNER_ID = 'user_id'

    DASHBOARD_TAG_RELATION_TYPE = 'TAG'
    TAG_DASHBOARD_RELATION_TYPE = 'TAG_OF'

    serialized_nodes = set()  # type: Set[Any]
    serialized_rels = set()  # type: Set[Any]

    def __init__(self,
                 dashboard_group,  # type: str
                 dashboard_name,  # type: str
                 description,  # type: Union[str, None]
                 last_reload_time,  # type: str
                 user_id,  # type: str
                 tags  # type: List
                 ):
        # type: (...) -> None

        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.description = description
        self.last_reload_time = last_reload_time
        self.user_id = user_id
        self.tags = tags
        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self):
        # type: () -> str
        return 'DashboardMetadata({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}' \
            .format(self.dashboard_group,
                    self.dashboard_name,
                    self.description,
                    self.last_reload_time,
                    self.user_id,
                    self.tags
                    )

    def _get_dashboard_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_KEY_FORMAT.format(dashboard_group=self.dashboard_group,
                                                             dashboard_name=self.dashboard_name)

    def _get_dashboard_description_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_DESCRIPTION_FORMAT.format(dashboard_group=self.dashboard_group,
                                                                     dashboard_name=self.dashboard_name)

    def _get_dashboard_group_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_GROUP_KEY_FORMAT.format(dashboard_group=self.dashboard_group)

    def _get_dashboard_last_reload_time_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_FORMAT.format(dashboard_group=self.dashboard_group,
                                                                          dashboard_name=self.dashboard_name)

    def _get_owner_key(self):
        # type: () -> str
        return DashboardMetadata.OWNER_KEY_FORMAT.format(user_id=self.user_id)

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self):
        # type: () -> Iterator[Any]
        # Dashboard node
        yield {NODE_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
               NODE_KEY: self._get_dashboard_key(),
               DashboardMetadata.DASHBOARD_NAME: self.dashboard_name,
               }

        # Dashboard group
        if self.dashboard_group:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_group_key(),
                   DashboardMetadata.DASHBOARD_NAME: self.dashboard_group,
                   }

        # Dashboard description node
        if self.description:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_description_key(),
                   DashboardMetadata.DASHBOARD_DESCRIPTION: self.description}

        # Dashboard last reload time node
        if self.last_reload_time:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_last_reload_time_key(),
                   DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME: self.last_reload_time}

        # Dashboard tag node
        if self.tags:
            for tag in self.tags:
                yield {NODE_LABEL: TagMetadata.TAG_NODE_LABEL,
                       NODE_KEY: TagMetadata.get_tag_key(tag),
                       TagMetadata.TAG_TYPE: 'dashboard'}

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self):
        # type: () -> Iterator[Any]

        # Dashboard group > Dashboard relation
        yield {
            RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            RELATION_END_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
            RELATION_START_KEY: self._get_dashboard_key(),
            RELATION_END_KEY: self._get_dashboard_group_key(),
            RELATION_TYPE: DashboardMetadata.DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE,
            RELATION_REVERSE_TYPE: DashboardMetadata.DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE
        }

        # Dashboard > Dashboard description relation
        if self.description:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_dashboard_description_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.DESCRIPTION_DASHBOARD_RELATION_TYPE
            }

        # Dashboard > Dashboard last reload time relation
        if self.last_reload_time:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_dashboard_last_reload_time_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.LAST_RELOAD_TIME_DASHBOARD_RELATION_TYPE
            }

        # Dashboard > Dashboard tag relation
        if self.tags:
            for tag in self.tags:
                yield {
                    RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                    RELATION_END_LABEL: TagMetadata.TAG_NODE_LABEL,
                    RELATION_START_KEY: self._get_dashboard_key(),
                    RELATION_END_KEY: TagMetadata.get_tag_key(tag),
                    RELATION_TYPE: DashboardMetadata.DASHBOARD_TAG_RELATION_TYPE,
                    RELATION_REVERSE_TYPE: DashboardMetadata.TAG_DASHBOARD_RELATION_TYPE
                }

        # Dashboard > Dashboard owner relation
        others = [
            RelTuple(start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
                     end_label=DashboardMetadata.OWNER_NODE_LABEL,
                     start_key=self._get_dashboard_key(),
                     end_key=self._get_owner_key(),
                     type=DashboardMetadata.DASHBOARD_OWNER_RELATION_TYPE,
                     reverse_type=DashboardMetadata.OWNER_DASHBOARD_RELATION_TYPE)
        ]

        for rel_tuple in others:
            if rel_tuple not in DashboardMetadata.serialized_rels:
                DashboardMetadata.serialized_rels.add(rel_tuple)
                yield {
                    RELATION_START_LABEL: rel_tuple.start_label,
                    RELATION_END_LABEL: rel_tuple.end_label,
                    RELATION_START_KEY: rel_tuple.start_key,
                    RELATION_END_KEY: rel_tuple.end_key,
                    RELATION_TYPE: rel_tuple.type,
                    RELATION_REVERSE_TYPE: rel_tuple.reverse_type
                }
