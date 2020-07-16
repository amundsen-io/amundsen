# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any, Dict, List, Mapping, Optional, Union

import gremlin_python
from amundsen_common.models.popular_table import PopularTable
from amundsen_common.models.table import Table
from amundsen_common.models.user import User as UserEntity
from amundsen_common.models.dashboard import DashboardSummary
from gremlin_python.driver.driver_remote_connection import \
    DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import GraphTraversalSource

from metadata_service.entity.dashboard_detail import DashboardDetail as DashboardDetailEntity
from metadata_service.entity.description import Description
from metadata_service.entity.resource_type import ResourceType
from metadata_service.proxy import BaseProxy
from metadata_service.util import UserResourceRel

__all__ = ['AbstractGremlinProxy', 'GenericGremlinProxy']

LOGGER = logging.getLogger(__name__)


def _parse_gremlin_server_error(exception: Exception) -> Dict[str, Any]:
    if not isinstance(exception, gremlin_python.driver.protocol.GremlinServerError) or len(exception.args) != 1:
        return {}
    # this is like '444: {...json object...}'
    return json.loads(exception.args[0][exception.args[0].index(': ') + 1:])


class AbstractGremlinProxy(BaseProxy):
    """
    Gremlin Proxy client for the amundsen metadata
    """

    def __init__(self, *, key_property_name: str, remote_connection: DriverRemoteConnection) -> None:
        # these might vary from datastore type to another, but if you change these while talking to the same instance
        # without migration, it will go poorly
        self.key_property_name: str = key_property_name

        # safe this for use in _submit
        self.remote_connection: DriverRemoteConnection = remote_connection

        self._g: GraphTraversalSource = traversal().withRemote(self.remote_connection)

    @property
    def g(self) -> GraphTraversalSource:
        """
        might not actually refer to g, but usually is so let's call it that here.
        no setter so we don't accidentally self.g = somewhere
        """
        return self._g

    @classmethod
    def _is_retryable_exception(cls, *, method_name: str, exception: Exception) -> bool:
        """
        overridde this if you want to retry the exception for the given method_name
        """
        return False

    def _submit(self, *, command: str, bindings: Any = None) -> Any:
        """
        Do not use this.

        ...except if you are doing graph management or other things not supported
        by Gremlin.  For example, with JanusGraph, you might:

        >>> self._submit('''
        graph.tx().rollback()
        mgmt = graph.openManagement()
        keyProperty = mgmt.getPropertyKey('_key')
        vertexLabel = mgmt.getVertexLabel('Table')
        mgmt.buildIndex('TableByKeyUnique', Vertex.class).addKey(keyProperty).indexOnly(vertexLabel).unique().buildCompositeIndex()
        mgmt.commit()
        ''')

        >>> self._submit('''
        graph.openManagement().getGraphIndex('TableByKey')
        ''')

        >>> self._submit('''
        graph.openManagement().getGraphIndexes(Vertex.class)
        ''')

        >>> self._submit('''
        graph.openManagement().getGraphIndexes(Edge.class)
        ''')
        """  # noqa: E501
        return self.remote_connection._client.submit(message=command, bindings=bindings).all().result()

    def get_user(self, *, id: str) -> Union[UserEntity, None]:
        pass

    def get_users(self) -> List[UserEntity]:
        pass

    def get_table(self, *, table_uri: str) -> Table:
        pass

    def delete_owner(self, *, table_uri: str, owner: str) -> None:
        pass

    def add_owner(self, *, table_uri: str, owner: str) -> None:
        pass

    def get_table_description(self, *,
                              table_uri: str) -> Union[str, None]:
        pass

    def put_table_description(self, *,
                              table_uri: str,
                              description: str) -> None:
        pass

    def add_tag(self, *, id: str, tag: str, tag_type: str,
                resource_type: ResourceType = ResourceType.Table) -> None:
        pass

    def delete_tag(self, *, id: str, tag: str, tag_type: str,
                   resource_type: ResourceType = ResourceType.Table) -> None:
        pass

    def put_column_description(self, *,
                               table_uri: str,
                               column_name: str,
                               description: str) -> None:
        pass

    def get_column_description(self, *,
                               table_uri: str,
                               column_name: str) -> Union[str, None]:
        pass

    def get_popular_tables(self, *, num_entries: int) -> List[PopularTable]:
        pass

    def get_latest_updated_ts(self) -> int:
        pass

    def get_tags(self) -> List:
        pass

    def get_dashboard_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) \
            -> Dict[str, List[DashboardSummary]]:
        pass

    def get_table_by_user_relation(self, *, user_email: str,
                                   relation_type: UserResourceRel) -> Dict[str, Any]:
        pass

    def get_frequently_used_tables(self, *, user_email: str) -> Dict[str, Any]:
        pass

    def add_resource_relation_by_user(self, *,
                                      id: str,
                                      user_id: str,
                                      relation_type: UserResourceRel,
                                      resource_type: ResourceType) -> None:
        pass

    def delete_resource_relation_by_user(self, *,
                                         id: str,
                                         user_id: str,
                                         relation_type: UserResourceRel,
                                         resource_type: ResourceType) -> None:
        pass

    def get_dashboard(self,
                      dashboard_uri: str,
                      ) -> DashboardDetailEntity:
        pass

    def get_dashboard_description(self, *,
                                  id: str) -> Description:
        pass

    def put_dashboard_description(self, *,
                                  id: str,
                                  description: str) -> None:
        pass

    def get_resources_using_table(self, *,
                                  id: str,
                                  resource_type: ResourceType) -> Dict[str, List[DashboardSummary]]:
        return {}


class GenericGremlinProxy(AbstractGremlinProxy):
    """
    A generic Gremlin proxy
    :param host: a websockets URL
    :param port: None (put it in the URL passed in host)
    :param user: (as optional as your server allows) username
    :param password: (as optional as your server allows) password
    :param driver_remote_connection_options: passed to DriverRemoteConnection's constructor.
    """

    def __init__(self, *, host: str, port: Optional[int] = None, user: Optional[str] = None,
                 password: Optional[str] = None, traversal_source: 'str' = 'g', key_property_name: str = 'key',
                 driver_remote_connection_options: Mapping[str, Any] = {}) -> None:
        driver_remote_connection_options = dict(driver_remote_connection_options)
        # as others, we repurpose host a url
        driver_remote_connection_options.update(url=host)
        # port should be part of that url
        if port is not None:
            raise NotImplementedError(f'port is not allowed! port={port}')

        if user is not None:
            driver_remote_connection_options.update(username=user)
        if password is not None:
            driver_remote_connection_options.update(password=password)

        driver_remote_connection_options.update(traversal_source=traversal_source)

        super().__init__(key_property_name=key_property_name,
                         remote_connection=DriverRemoteConnection(**driver_remote_connection_options))
