# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import (
    Any, Dict, List, Union,
)

from amundsen_common.models.api import health_check
from amundsen_common.models.search import (
    Filter, HighlightOptions, SearchResponse,
)
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ElasticConnectionError, ElasticsearchException
from elasticsearch_dsl import (
    MultiSearch, Q, Search,
)
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrList
from werkzeug.exceptions import InternalServerError

from search_service.proxy.es_proxy_utils import Resource, create_search_response

LOGGER = logging.getLogger(__name__)

BOOL_QUERY = 'bool'
WILDCARD_QUERY = 'wildcard'
TERM_QUERY = 'term'
TERMS_QUERY = 'terms'


class ElasticsearchProxyV2():
    PRIMARY_ENTITIES = [Resource.TABLE, Resource.DASHBOARD, Resource.FEATURE, Resource.USER]

    # mapping to translate request for table resources
    TABLE_MAPPING = {
        'key': 'key',
        'badges': 'badges',
        'tag': 'tags',
        'schema': 'schema.raw',
        'table': 'name.raw',
        'column': 'column_names.raw',
        'database': 'database.raw',
        'cluster': 'cluster.raw',
        'description': 'description',
        'resource_type': 'resource_type'
    }

    # mapping to translate request for dashboard resources
    DASHBOARD_MAPPING = {
        'group_name': 'group_name.raw',
        'group_url': 'group_url',
        'url': 'url',
        'uri': 'uri',
        'name': 'name.raw',
        'product': 'product',
        'tag': 'tags',
        'description': 'description',
        'last_successful_run_timestamp': 'last_successful_run_timestamp',
        'resource_type': 'resource_type'
    }

    # mapping to translate request for feature resources
    FEATURE_MAPPING = {
        'key': 'key',
        'feature_group': 'feature_group.raw',
        'feature_name': 'feature_name.raw',
        'entity': 'entity',
        'status': 'status',
        'version': 'version',
        'availability': 'availability.raw',
        'tags': 'tags',
        'badges': 'badges',
        'description': 'description',
        'resource_type': 'resource_type'
    }

    USER_MAPPING = {
        'full_name': 'full_name',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
        'resource_type': 'resource_type'
    }

    RESOURCE_TO_MAPPING = {
        Resource.TABLE: TABLE_MAPPING,
        Resource.DASHBOARD: DASHBOARD_MAPPING,
        Resource.FEATURE: FEATURE_MAPPING,
        Resource.USER: USER_MAPPING,
    }

    MUST_FIELDS_TABLE = ["name^3",
                         "name.raw^3",
                         "schema^2",
                         "description",
                         "column_names",
                         "badges"]

    MUST_FIELDS_DASHBOARD = ["name.raw^75",
                             "name^7",
                             "group_name.raw^15",
                             "group_name^7",
                             "description^3",
                             "query_names^3",
                             "chart_names^2"]

    MUST_FIELDS_FEATURE = ["feature_name.raw^25",
                           "feature_name^7",
                           "feature_group.raw^15",
                           "feature_group^7",
                           "version^7",
                           "description^3",
                           "status",
                           "entity",
                           "tags",
                           "badges"]

    MUST_FIELDS_USER = ["full_name.raw^30",
                        "full_name^5",
                        "first_name.raw^5",
                        "last_name.raw^5",
                        "first_name^3",
                        "last_name^3",
                        "email^3"]

    def __init__(self, *,
                 host: str = None,
                 user: str = '',
                 password: str = '',
                 client: Elasticsearch = None,
                 page_size: int = 10) -> None:
        if client:
            self.elasticsearch = client
        else:
            http_auth = (user, password) if user else None
            self.elasticsearch = Elasticsearch(host, http_auth=http_auth)
        self.page_size = page_size

    def health(self) -> health_check.HealthCheck:
        """
        Returns the health of the Elastic search cluster
        """
        try:
            if self.elasticsearch.ping():
                health = self.elasticsearch.cluster.health()
                # ES status vaues: green, yellow, red
                status = health_check.OK if health['status'] != 'red' else health_check.FAIL
            else:
                health = {'status': 'Unable to connect'}
                status = health_check.FAIL
            checks = {f'{type(self).__name__}:connection': health}
        except ElasticConnectionError:
            status = health_check.FAIL
            checks = {f'{type(self).__name__}:connection': {'status': 'Unable to connect'}}
        return health_check.HealthCheck(status=status, checks=checks)

    def _get_must_fields(self, resource: Resource) -> List[str]:
        must_fields_mapping = {
            Resource.TABLE: self.MUST_FIELDS_TABLE,
            Resource.DASHBOARD: self.MUST_FIELDS_DASHBOARD,
            Resource.FEATURE: self.MUST_FIELDS_FEATURE,
            Resource.USER: self.MUST_FIELDS_USER
        }

        return must_fields_mapping[resource]

    def get_index_alias_for_resource(self, resource_type: Resource) -> str:
        resource_str = resource_type.name.lower()
        return f"{resource_str}_search_index"

    def _build_must_query(self, resource: Resource, query_term: str) -> List[Q]:
        """
        Builds the query object for the inputed search term
        """
        if not query_term:
            # We don't want to create multi_match query for ""
            # because it will result in no matches even with filters
            return []

        try:
            fields: List[str] = self._get_must_fields(resource)
        except KeyError:
            # TODO if you don't specify a resource match for all generic fields in the future
            raise ValueError(f"no fields defined for resource {resource}")

        return [MultiMatch(query=query_term, fields=fields, type='cross_fields')]

    def _build_should_query(self, resource: Resource, query_term: str) -> List[Q]:
        # Can define on custom es_search_proxy class, no default implementation
        return []

    def _build_filters(self, resource: Resource, filters: List[Filter]) -> List:
        """
        Builds the query object for all of the filters given in the search request
        """
        mapping = self.RESOURCE_TO_MAPPING.get(resource)

        filter_queries: List = []

        for filter in filters:
            if mapping is not None and mapping.get(filter.name) is not None:
                # only apply filter to query if field exists for the given resource
                filter_name = mapping.get(filter.name)

                queries_per_term = [Q(WILDCARD_QUERY, **{filter_name: term}) for term in filter.values]

                if filter.operation == 'OR':
                    filter_queries.append(Q(BOOL_QUERY, should=queries_per_term, minimum_should_match=1))

                elif filter.operation == 'AND':
                    for q in queries_per_term:
                        filter_queries.append(q)

                else:
                    msg = f"Invalid operation {filter.operation} for filter {filter_name} with values {filter.values}"
                    raise ValueError(msg)
            else:
                LOGGER.info("Filter {filter.name} does not apply to {resource}")

        return filter_queries

    def _build_elasticsearch_query(self, *,
                                   resource: Resource,
                                   query_term: str,
                                   filters: List[Filter]) -> Q:

        must_query = self._build_must_query(resource=resource,
                                            query_term=query_term)

        should_query = self._build_should_query(resource=resource,
                                                query_term=query_term)

        filters = self._build_filters(resource=resource, filters=filters)

        es_query = Q(BOOL_QUERY, must=must_query, should=should_query, filter=filters)

        return es_query

    def execute_queries(self, queries: Dict[Resource, Q],
                        page_index: int,
                        results_per_page: int) -> List[Response]:
        multisearch = MultiSearch(using=self.elasticsearch)

        for resource in queries.keys():
            query_for_resource = queries.get(resource)
            search = Search(index=self.get_index_alias_for_resource(resource_type=resource)).query(query_for_resource)
            LOGGER.info(json.dumps(search.to_dict()))

            # pagination
            start_from = page_index * results_per_page
            end = results_per_page * (page_index + 1)

            search = search[start_from:end]

            multisearch = multisearch.add(search)
        try:
            response = multisearch.execute()
            return response
        except Exception as e:
            LOGGER.error(f'Failed to execute ES search queries. {e}')
            return []

    def search(self, *,
               query_term: str,
               page_index: int,
               results_per_page: int,
               resource_types: List[Resource],
               filters: List[Filter],
               highlight_options: Dict[Resource, HighlightOptions]) -> SearchResponse:
        if not resource_types:
            # if resource types are not defined then search all resources
            resource_types = self.PRIMARY_ENTITIES

        queries: Dict[Resource, Q] = {}
        for resource in resource_types:
            # build a query for each resource to search
            queries[resource] = self._build_elasticsearch_query(resource=resource,
                                                                query_term=query_term,
                                                                filters=filters)

        responses = self.execute_queries(queries=queries,
                                         page_index=page_index,
                                         results_per_page=results_per_page)

        formatted_response = create_search_response(page_index=page_index,
                                                    results_per_page=results_per_page,
                                                    responses=responses,
                                                    resource_types=resource_types,
                                                    resource_to_field_mapping=self.RESOURCE_TO_MAPPING)

        return formatted_response

    def get_document_json_by_key(self,
                                 resource_key: str,
                                 resource_type: Resource) -> Any:
        key_query = {
            resource_type: Q(TERM_QUERY, key=resource_key),
        }
        response: Response = self.execute_queries(queries=key_query,
                                                  page_index=0,
                                                  results_per_page=1)
        if len(response) < 1:
            msg = f'No response from ES for key query {key_query[resource_type]}'
            LOGGER.error(msg)
            raise ElasticsearchException(msg)

        response = response[0]
        if response.success():
            results_count = response.hits.total.value
            if results_count == 1:
                es_result = response.hits.hits[0]
                return es_result

            if results_count > 1:
                msg = f'Key {key_query[resource_type]} is not unique to a single ES resource'
                LOGGER.error(msg)
                raise ValueError(msg)

            else:
                # no doc exists with given key in ES
                msg = f"Requested key {resource_key} query returned no results in ES"
                LOGGER.error(msg)
                raise ValueError(msg)
        else:
            msg = f'Request to Elasticsearch failed: {response.failures}'
            LOGGER.error(msg)
            raise InternalServerError(msg)

    def update_document_by_id(self, *,
                              resource_type: Resource,
                              field: str,
                              new_value: Union[List, str, None],
                              document_id: str) -> None:

        partial_document = {
            "doc": {
                field: new_value
            }
        }
        self.elasticsearch.update(index=self.get_index_alias_for_resource(resource_type=resource_type),
                                  id=document_id,
                                  body=partial_document)

    def update_document_by_key(self, *,
                               resource_key: str,
                               resource_type: Resource,
                               field: str,
                               value: str = None,
                               operation: str = 'add') -> str:

        mapped_field = self.RESOURCE_TO_MAPPING[resource_type].get(field)
        if not mapped_field:
            mapped_field = field

        try:
            es_hit = self.get_document_json_by_key(resource_key=resource_key,
                                                   resource_type=resource_type)
            document_id = es_hit._id
            current_value = getattr(es_hit._source, mapped_field)

        except Exception as e:
            msg = f'Failed to get ES document id and current value for key {resource_key}. {e}'
            LOGGER.error(msg)
            return msg

        new_value = current_value

        if operation == 'overwrite':
            if type(current_value) is AttrList:
                new_value = [value]
            else:
                new_value = value
        else:
            # operation is add
            if type(current_value) is AttrList:
                curr_list = list(current_value)
                curr_list.append(value)
                new_value = curr_list
            else:
                new_value = [current_value, value]

        try:
            self.update_document_by_id(resource_type=resource_type,
                                       field=mapped_field,
                                       new_value=new_value,
                                       document_id=document_id)
        except Exception as e:
            msg = f'Failed to update field {field} with value {new_value} for {resource_key}. {e}'
            LOGGER.error(msg)
            return msg

        return f'ES document field {field} for {resource_key} with value {value} was updated successfully'

    def delete_document_by_key(self, *,
                               resource_key: str,
                               resource_type: Resource,
                               field: str,
                               value: str = None) -> str:
        mapped_field = self.RESOURCE_TO_MAPPING[resource_type].get(field)
        if not mapped_field:
            mapped_field = field

        try:
            es_hit = self.get_document_json_by_key(resource_key=resource_key,
                                                   resource_type=resource_type)
            document_id = es_hit._id
            current_value = getattr(es_hit._source, mapped_field)

        except Exception as e:
            msg = f'Failed to get ES document id and current value for key {resource_key}. {e}'
            LOGGER.error(msg)
            return msg

        new_value = current_value

        if type(current_value) is AttrList:
            if value:
                curr_list = list(current_value)
                curr_list.remove(value)
                new_value = curr_list
            else:
                new_value = []
        else:
            # no value given when deleting implies
            # delete is happening on a single value field
            new_value = ""
        try:
            self.update_document_by_id(resource_type=resource_type,
                                       field=mapped_field,
                                       new_value=new_value,
                                       document_id=document_id)
        except Exception as e:
            msg = f'Failed to delete field {field} with value {new_value} for {resource_key}. {e}'
            LOGGER.error(msg)
            return msg

        return f'ES document field {field} for {resource_key} with value {value} was deleted successfully'
