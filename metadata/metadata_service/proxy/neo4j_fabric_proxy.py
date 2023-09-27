# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import re
import logging
import textwrap
from typing import (Tuple, List, Union, Dict, Any)  # noqa: F401
import os

import neo4j
from amundsen_common.entity.resource_type import ResourceType
from amundsen_common.models.table import (User, Reader)
from amundsen_common.models.user import User as UserEntity
from amundsen_common.models.dashboard import DashboardSummary
from amundsen_common.models.popular_table import PopularTable


from metadata_service.proxy.neo4j_proxy import Neo4jProxy, _CACHE, _GET_POPULAR_RESOURCES_CACHE_EXPIRY_SEC
from metadata_service.proxy.statsd_utilities import timer_with_counter
from metadata_service.util import UserResourceRel
from metadata_service.entity.description import Description


LOGGER = logging.getLogger(__name__)

RETURN_SPECIAL_CHAR_RE = re.compile('[()}{]')

class Neo4jFabricProxy(Neo4jProxy):
    """
    A proxy to Neo4j (Gateway to Neo4j)
    """

    def __init__(self, *,
                 host: str,
                 port: int = 7687,
                 user: str = 'neo4j',
                 password: str = '',
                 num_conns: int = 50,
                 max_connection_lifetime_sec: int = 100,
                 encrypted: bool = False,
                 validate_ssl: bool = False,
                 database_name: str = neo4j.DEFAULT_DATABASE,
                 **kwargs: dict) -> None:
        super().__init__(
            host=host,
            port=port,
            user=user,
            password=password,
            num_conns=num_conns,
            max_connection_lifetime_sec=max_connection_lifetime_sec,
            encrypted=encrypted,
            validate_ssl=validate_ssl,
            database_name=database_name,
            kwargs=kwargs
        )

        self.federated_tag = os.getenv('FEDERATED_TAG', "shared")
    
    def _prepare_federated_return_statement(self, statement: str) -> str:
        """
        This method makes a bunch of assumptions about the query statements provided by the 
        non-fabric proxy. It tries to strip out the RETURN statement which is then parsed
        as there are often aggregations mixed in which does not work with the fabric query.

        We start by grabbing everything after RETURN to the end of the statement.
        Then we remove the ORDER BY clause.  Then we loop through each column (comma split) in the RETURN.
        If there is a AS clause, we grab the alias.  If there is no AS clasue and there are special 
        chars in the column name, we assume it is some aggregation so we ignore it.  Otherwise, we use the proper
        column name.
        """
        cleaned_return_statement = "RETURN "
        return_statement = re.split('return', statement, flags=re.IGNORECASE)[1]
        return_statement = re.split('order by', return_statement, flags=re.IGNORECASE)[0]
        for column in return_statement.split(','):
            as_split = re.split(' as ', column, flags=re.IGNORECASE)
            if len(as_split) == 1:
                if RETURN_SPECIAL_CHAR_RE.search(as_split[0]) == None:
                    cleaned_return_statement += as_split[0]
                else:
                    continue
            else:
                cleaned_return_statement += as_split[1]
            cleaned_return_statement += ','
        
        # Skip the last char, which should be the trailing comma
        return cleaned_return_statement[0: -1]

    def _prepare_federated_resource_tag_rel_statement(self, resource_type: ResourceType = None, include_tag_name: bool = True) -> str:   
        node_label = (f"{resource_type.name.lower()}:{resource_type.name}" if resource_type is not None else 'resource')
        federated_statement = textwrap.dedent(f"""
            ({'shared_tag' if include_tag_name == True else ''}:Tag {{key: "{self.federated_tag}"}})-[:TAG]->({node_label})
        """)
        return federated_statement

    def _prepare_federated_resource_tag_match_statement(self, resource_type: ResourceType = None) -> str:   
        federated_statement = textwrap.dedent(f"""
            MATCH {self._prepare_federated_resource_tag_rel_statement(resource_type=resource_type)}
        """)
        return federated_statement

    def _prepare_federated_query_statement(self, statement: str, resource_type: ResourceType = None) -> str:   
        federated_statement = textwrap.dedent(f"""
            {self._prepare_federated_resource_tag_match_statement(resource_type=resource_type)}
            {statement}
        """)

        return federated_statement

    def _get_fabric_query_statement(self, fabric_db_name: str, statement: str) -> str:
        fabric_statement = textwrap.dedent(f"""
            UNWIND {fabric_db_name}.graphIds() AS graphId
            CALL {{
                USE {fabric_db_name}.graph(graphId)
                {statement.replace(';','')}
            }}
            {self._prepare_federated_return_statement(statement=statement)}
        """)
        LOGGER.info(f"_fabric_query_statement={fabric_statement}")
        return fabric_statement


    ########################## OVERRIDE ##########################


    def _get_col_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_col_query_statement(), 
                resource_type=ResourceType.Table))

    def _get_table_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_table_query_statement(), 
                resource_type=ResourceType.Table))

    def _get_table_query_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_table_query_query_statement(), 
                resource_type=ResourceType.Table))

    def _get_owners_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_owners_query_statement(), 
                resource_type=ResourceType.Table))

    def _get_description_query_statement(self, resource_type: ResourceType) -> str:
        if resource_type == ResourceType.Table or \
           resource_type == ResourceType.Dashboard or \
           resource_type == ResourceType.Feature:
            statement = self._prepare_federated_query_statement(statement=super()._get_description_query_statement(resource_type), resource_type=resource_type)
        else:
            statement = super()._get_description_query_statement(resource_type)
        return self._get_fabric_query_statement(self._database_name, statement)

    def _get_column_description_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_column_description_query_statement(), 
                resource_type=ResourceType.Table))

    def _get_badge_query_statement(self) -> str:
        table_badge_statement = textwrap.dedent(f"""
            MATCH (table:Table)-[:HAS_BADGE]->(badge:Badge)
            {super()._get_badge_query_statement()}
        """)

        dashboard_badge_statement = textwrap.dedent(f"""
            MATCH (dashboard:Dashboard)-[:HAS_BADGE]->(badge:Badge)
            {super()._get_badge_query_statement()}
        """)
        
        statement = textwrap.dedent(f"""
            {self._get_fabric_query_statement(self._database_name, self._prepare_federated_query_statement(statement=table_badge_statement))}
            UNION
            {self._get_fabric_query_statement(self._database_name, self._prepare_federated_query_statement(statement=dashboard_badge_statement))}
        """)
        
        return statement

    def _get_tags_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_tags_query_statement(optional_resource=False)))

    def _get_latest_updated_ts_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            super()._get_latest_updated_ts_query_statement())

    def _get_statistics_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_statistics_query_statement(), 
                resource_type=ResourceType.Table))

    # def _get_global_popular_resources_uris_query_statement(self, resource_type: ResourceType = ResourceType.Table) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_global_popular_resources_uris_query_statement(resource_type))

    # def _get_personal_popular_resources_uris_query_statement(self, resource_type: ResourceType = ResourceType.Table) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_personal_popular_resources_uris_query_statement(resource_type))

    def _get_popular_tables_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_popular_tables_query_statement(), 
                resource_type=ResourceType.Table))
        
    def _get_popular_dashboards_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_popular_dashboards_query_statement(), 
                resource_type=ResourceType.Dashboard))
        
    # def _get_user_query_statement(self) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_user_query_statement())

    # def _get_users_query_statement(self) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_users_query_statement())

    # def _get_dashboard_by_user_relation_query_statement(self, user_email: str, relation_type: UserResourceRel) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_dashboard_by_user_relation_query_statement(user_email, relation_type))

    # def _get_table_by_user_relation_query_statement(self, user_email: str, relation_type: UserResourceRel) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_table_by_user_relation_query_statement(user_email, relation_type))

    # def _get_frequently_used_tables_query_statement(self) -> str:
    #     return self._get_fabric_query_statement(self._database_name, super()._get_frequently_used_tables_query_statement())

    def _get_dashboard_query_statement(self, table_where_clause: str = '') -> str:
        table_where_clause = textwrap.dedent(f"""
            WHERE exists({self._prepare_federated_resource_tag_rel_statement(resource_type=ResourceType.Table, include_tag_name=False)})
        """)
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_dashboard_query_statement(table_where_clause), 
                resource_type=ResourceType.Dashboard))

    def _get_resources_using_table_query_statement(self) -> str:
        statement = textwrap.dedent(f"""
            {self._prepare_federated_resource_tag_match_statement(ResourceType.Table)}
            {self._prepare_federated_resource_tag_match_statement(ResourceType.Dashboard)}
            {super()._get_resources_using_table_query_statement()}
        """)

        return self._get_fabric_query_statement(self._database_name, statement)

    def _get_both_lineage_query_statement(self, resource_type: ResourceType, depth: int = 1) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_both_lineage_query_statement(resource_type, depth), 
                resource_type=resource_type))

    def _get_upstream_lineage_query_statement(self, resource_type: ResourceType, depth: int = 1) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_upstream_lineage_query_statement(resource_type, depth), 
                resource_type=resource_type))

    def _get_downstream_lineage_query_statement(self, resource_type: ResourceType, depth: int = 1) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_downstream_lineage_query_statement(resource_type, depth), 
                resource_type=resource_type))

    def _get_exec_feature_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_exec_feature_query_statement(), 
                resource_type=ResourceType.Feature))

    def _get_resource_generation_code_query_statement(self, resource_type: ResourceType) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_resource_generation_code_query_statement(resource_type), 
                resource_type=resource_type))
    
    def _get_snowflake_table_shares_query_statement(self) -> str:
        return self._get_fabric_query_statement(self._database_name, 
            self._prepare_federated_query_statement(statement=super()._get_snowflake_table_shares_query_statement()))

    ########################## OVERRIDE ##########################

    @timer_with_counter
    def get_frequently_used_tables(self, *, user_email: str) -> Dict[str, Any]:
        LOGGER.info('get_frequently_used_tables: Neo4fFabricProxy is does not support pulling User info from source')
        return {}

    @timer_with_counter
    def get_table_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) -> Dict[str, List[PopularTable]]:
        LOGGER.info('get_table_by_user_relation: Neo4fFabricProxy is does not support pulling User info from source')
        return {}

    @timer_with_counter
    def get_dashboard_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) -> Dict[str, List[DashboardSummary]]:
        LOGGER.info('get_dashboard_by_user_relation: Neo4fFabricProxy is does not support pulling User info from source')
        return {}

    def get_users(self) -> List[UserEntity]:
        LOGGER.info('get_users: Neo4fFabricProxy is does not support pulling User info from source')
        return []

    @timer_with_counter
    def get_user(self, *, id: str) -> Union[UserEntity, None]:
        LOGGER.info('get_user: Neo4fFabricProxy is does not support pulling User info from source')
        return None

    @timer_with_counter
    @_CACHE.cache('_get_personal_popular_tables_uris', _GET_POPULAR_RESOURCES_CACHE_EXPIRY_SEC)
    def _get_personal_popular_resources_uris(self, num_entries: int,
                                             user_id: str,
                                             resource_type: ResourceType = ResourceType.Table) -> List[str]:
        """
        Need a Federated way to determine what is popular
        """
        LOGGER.info('_get_personal_popular_tables_uris: Neo4fFabricProxy is does not support pulling User info from source')
        return []

    @_CACHE.cache('_get_global_popular_resources_uris', expire=_GET_POPULAR_RESOURCES_CACHE_EXPIRY_SEC)
    def _get_global_popular_resources_uris(self, num_entries: int,
                                           resource_type: ResourceType = ResourceType.Table) -> List[str]:
        """
        Need a Federated way to determine what is popular
        """
        LOGGER.info('_get_global_popular_resources_uris: Neo4fFabricProxy is does not support pulling User info from source')
        return []

    @timer_with_counter
    def _exec_usage_query(self, table_uri: str) -> List[Reader]:
        LOGGER.info('_exec_usage_query: Neo4fFabricProxy is does not support pulling User info from source')
        return []
    
    @timer_with_counter
    def get_resource_description(self, *,
                                 resource_type: ResourceType,
                                 uri: str) -> Description:
        description: Description = None
        if resource_type == ResourceType.User:
            LOGGER.info('get_resource_description(): Neo4fFabricProxy is does not support pulling User info from source')            
        else:
            description = super().get_resource_description(resource_type, uri)

        return description
    
    @timer_with_counter
    def put_resource_description(self, *,
                                 resource_type: ResourceType,
                                 uri: str,
                                 description: str) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  put_resource_description() is not supported')

    @timer_with_counter
    def put_column_description(self, *,
                               table_uri: str,
                               column_name: str,
                               description: str) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  put_column_description() is not supported')

    @timer_with_counter
    def add_resource_owner(self, *,
                           uri: str,
                           resource_type: ResourceType,
                           owner: str) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  add_resource_owner() is not supported')

    @timer_with_counter
    def delete_resource_owner(self, *,
                              uri: str,
                              resource_type: ResourceType,
                              owner: str) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  delete_resource_owner() is not supported')

    @timer_with_counter
    def add_badge(self, *,
                  id: str,
                  badge_name: str,
                  category: str = '',
                  resource_type: ResourceType) -> None:

        LOGGER.info('Neo4fFabricProxy is READ ONLY.  add_badge() is not supported')

    @timer_with_counter
    def delete_badge(self, id: str,
                     badge_name: str,
                     category: str,
                     resource_type: ResourceType) -> None:

        LOGGER.info('Neo4fFabricProxy is READ ONLY.  delete_badge() is not supported')

    @timer_with_counter
    def add_tag(self, *,
                id: str,
                tag: str,
                tag_type: str = 'default',
                resource_type: ResourceType = ResourceType.Table) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  add_tag() is not supported')

    @timer_with_counter
    def delete_tag(self, *,
                   id: str,
                   tag: str,
                   tag_type: str = 'default',
                   resource_type: ResourceType = ResourceType.Table) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  delete_tag() is not supported')

    def create_update_user(self, *, user: User) -> Tuple[User, bool]:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  create_update_user() is not supported')
    
    @timer_with_counter
    def add_resource_relation_by_user(self, *,
                                      id: str,
                                      user_id: str,
                                      relation_type: UserResourceRel,
                                      resource_type: ResourceType) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  add_resource_relation_by_user() is not supported')

    @timer_with_counter
    def delete_resource_relation_by_user(self, *,
                                         id: str,
                                         user_id: str,
                                         relation_type: UserResourceRel,
                                         resource_type: ResourceType) -> None:
        LOGGER.info('Neo4fFabricProxy is READ ONLY.  delete_resource_relation_by_user() is not supported')