# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import (
    Any, Dict, List, Union
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
from elasticsearch_dsl.query import Match, RankFeature
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrList
from flask import current_app
from werkzeug.exceptions import InternalServerError

from search_service import config
from search_service.proxy.es_proxy_utils import Resource, create_search_response

LOGGER = logging.getLogger(__name__)

# ES query constants

DEFAULT_FUZZINESS = "AUTO"

# using fvh as the default highlighter because it supports very large documents
DEFAULT_HIGHLIGHTER = 'fvh'

BOOL_QUERY = 'bool'
WILDCARD_QUERY = 'wildcard'
TERM_QUERY = 'term'
TERMS_QUERY = 'terms'


class ElasticsearchProxyV2_1():

    # map the field name in FE to the field used to filter in ES
    # note: ES needs keyword field types to filter

    GENERAL_MAPPING = {
        'key': 'key',
        'description': 'description',
        'resource_type': 'resource_type',
    }

    TABLE_MAPPING = {
        **GENERAL_MAPPING,
        'badges': 'badges.keyword',
        'tag': 'tags.keyword',
        'schema': 'schema.keyword',
        'table': 'name.keyword',
        'column': 'column_names.keyword',
        'database': 'database.keyword',
        'cluster': 'cluster.keyword',
    }

    DASHBOARD_MAPPING = {
        **GENERAL_MAPPING,
        'url': 'url',
        'uri': 'uri',
        'last_successful_run_timestamp': 'last_successful_run_timestamp',
        'group_name': 'group_name.keyword',
        'chart_names': 'chart_names.keyword',
        'query_names': 'query_names.keyword',
        'name': 'name.keyword',
        'tag': 'tags.keyword',
        'product': 'product.keyword',
    }

    FEATURE_MAPPING = {
        **GENERAL_MAPPING,
        'version': 'version',
        'availability': 'availability',
        'feature_group': 'feature_group.keyword',
        'feature_name': 'name.keyword',
        'entity': 'entity.keyword',
        'status': 'status.keyword',
        'tags': 'tags.keyword',
        'badges': 'badges.keyword',
    }

    USER_MAPPING = {
        'full_name': 'name.keyword',
        'email': 'key',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'resource_type': 'resource_type',
    }

    DATA_PROVIDER_MAPPING = {
        **GENERAL_MAPPING,
        # 'badges': 'badges.keyword',
        # 'tag': 'tags.keyword',
        'name': 'name.keyword',
        'data_channel_names': 'data_channel_names.keyword',
        'data_channel_types': 'data_channel_types.keyword',
        'data_channel_descriptions': 'data_channel_descriptions.keyword',
        'data_location_names': 'data_location_names.keyword',
        'data_location_types': 'data_location_types.keyword',
    }

    RESOURCE_TO_MAPPING = {
        Resource.TABLE: TABLE_MAPPING,
        Resource.DASHBOARD: DASHBOARD_MAPPING,
        Resource.FEATURE: FEATURE_MAPPING,
        Resource.USER: USER_MAPPING,
        Resource.DATA_PROVIDER: DATA_PROVIDER_MAPPING,
    }

    MUST_FIELDS_TABLE = ['name^3',
                         'name.raw^3',
                         'schema^2',
                         'description',
                         'column_names',
                         'badges']

    MUST_FIELDS_DASHBOARD = ['name.raw^75',
                             'name^7',
                             'group_name.raw^15',
                             'group_name^7',
                             'description^3',
                             'query_names^3',
                             'chart_names^2']

    MUST_FIELDS_FEATURE = ['feature_name.raw^25',
                           'feature_name^7',
                           'feature_group.raw^15',
                           'feature_group^7',
                           'version^7',
                           'description^3',
                           'status',
                           'entity',
                           'tags',
                           'badges']

    MUST_FIELDS_USER = ['full_name.raw^30',
                        'full_name^5',
                        'first_name.raw^5',
                        'last_name.raw^5',
                        'first_name^3',
                        'last_name^3',
                        'email^3']

    MUST_FIELDS_DATA_PROVIDER = ['name.raw^30',
                                 'name^5']


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
            Resource.USER: self.MUST_FIELDS_USER,
            Resource.DATA_PROVIDER: self.MUST_FIELDS_DATA_PROVIDER
        }

        return must_fields_mapping[resource]

    def get_index_alias_for_resource(self, resource_type: Resource) -> str:
        resource_str = resource_type.name.lower()
        alias_config = current_app.config.get(
            config.ES_INDEX_ALIAS_TEMPLATE
        )

        if alias_config is None:
            return f'{resource_str}_search_index_v2_1'

        alias = str(alias_config).format(resource=resource_str)

        return alias

    def _build_must_query(self, resource: Resource, query_term: str) -> List[Q]:
        """
        Builds the query object for the inputed search term
        """

        if not query_term:
            # We don't want to create match query for ""
            # because it will result in no matches even with filters
            return []

        # query for fields general to all resources
        should_clauses: List[Q] = [
            Match(name={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
                "boost": 5
            }),
            Match(description={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
                "boost": 1.5
            }),
            Match(badges={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
            }),
            Match(tags={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
            }),
        ]

        if resource == Resource.TABLE:
            columns_subfield = 'column_names.general'
            should_clauses.extend([
                Match(schema={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 3
                }),
                Match(**{columns_subfield: {
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 2
                }}),
                Match(column_descriptions={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS
                }),
            ])
        elif resource == Resource.DASHBOARD:
            should_clauses.extend([
                Match(group_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 3
                }),
                Match(query_names={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 2
                }),
                Match(chart_names={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 2
                }),
                Match(uri={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 4
                }),
            ])
        elif resource == Resource.FEATURE:
            should_clauses.extend([
                Match(feature_group={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 3
                }),
                Match(version={
                    "query": query_term
                }),
                Match(entity={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 2
                }),
                Match(status={
                    "query": query_term
                }),
            ])
        elif resource == Resource.USER:
            # replaces rather than extending
            should_clauses = [
                Match(name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 5
                }),
                Match(first_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 3
                }),
                Match(last_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 3
                }),
                Match(team_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS
                }),
                Match(key={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 4
                }),
            ]
        elif resource == Resource.DATA_PROVIDER:
            should_clauses.extend([
                Match(data_provider={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 3
                }),
            ])

        must_clauses: List[Q] = [Q(BOOL_QUERY, should=should_clauses)]

        return must_clauses

    def _build_should_query(self, resource: Resource, query_term: str) -> List[Q]:

        # no scoring happens if there is no search term
        if query_term == '':
            return []

        # general usage metric for searcheable resources
        usage_metric_field_boosts = {
            'total_usage': 10.0,
        }

        if resource == Resource.TABLE:
            usage_metric_field_boosts = {
                **usage_metric_field_boosts,
                'unique_usage': 10.0,
            }
        if resource == Resource.USER:
            usage_metric_field_boosts = {
                'total_read': 10.0,
                'total_own': 10.0,
                'total_follow': 10.0,
            }

        rank_feature_queries = []

        for metric in usage_metric_field_boosts.keys():
            field_name = f'usage.{metric}'
            boost = usage_metric_field_boosts[metric]
            rank_feature_query = RankFeature(field=field_name,
                                             boost=boost)
            rank_feature_queries.append(rank_feature_query)

        return rank_feature_queries

    def _build_filters(self, resource: Resource, filters: List[Filter]) -> List:
        """
        Builds the query object for all of the filters given in the search request
        """
        mapping = type(self).RESOURCE_TO_MAPPING.get(resource)

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
                    msg = f'Invalid operation {filter.operation} for filter {filter_name} with values {filter.values}'
                    raise ValueError(msg)
            else:
                LOGGER.info(f'Filter {filter.name} does not apply to {resource}')

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

    def _search_highlight(self,
                          resource: Resource,
                          search: Search,
                          highlight_options: Dict[Resource, HighlightOptions]) -> Search:
        # get highlighting options for resource
        resource_options = highlight_options.get(resource)
        highlighting_enabled = resource_options.enable_highlight if resource_options else None

        if highlighting_enabled:
            # default highlighted fields
            search = search.highlight('name',
                                      type=DEFAULT_HIGHLIGHTER,
                                      number_of_fragments=0)
            search = search.highlight('description',
                                      type=DEFAULT_HIGHLIGHTER,
                                      number_of_fragments=0)
            if resource == Resource.TABLE:
                search = search.highlight('column_names.general',
                                          type=DEFAULT_HIGHLIGHTER,
                                          number_of_fragments=10,
                                          order='score')
                search = search.highlight('column_descriptions',
                                          type=DEFAULT_HIGHLIGHTER,
                                          number_of_fragments=5,
                                          order='score')
            if resource == Resource.DASHBOARD:
                search = search.highlight('chart_names',
                                          type=DEFAULT_HIGHLIGHTER,
                                          number_of_fragments=10,
                                          order='score')
                search = search.highlight('query_names',
                                          type=DEFAULT_HIGHLIGHTER,
                                          number_of_fragments=10,
                                          order='score')

        return search

    def execute_multisearch_query(self, multisearch: MultiSearch) -> List[Response]:
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

        multisearch = MultiSearch(using=self.elasticsearch)

        for resource in resource_types:
            # build a query for each resource to search
            query_for_resource = self._build_elasticsearch_query(resource=resource,
                                                                 query_term=query_term,
                                                                 filters=filters)
            # wrap the query in a search object
            search = Search(index=self.get_index_alias_for_resource(resource_type=resource)).query(query_for_resource)

            # highlighting
            if highlight_options:
                search = self._search_highlight(resource=resource,
                                                search=search,
                                                highlight_options=highlight_options)

            # pagination
            start_from = page_index * results_per_page
            end = results_per_page * (page_index + 1)
            search = search[start_from:end]

            # add search object to multisearch
            LOGGER.info(f"resource={resource};search={json.dumps(search.to_dict())}")
            multisearch = multisearch.add(search)

        LOGGER.info(f"multisearch={json.dumps(multisearch.to_dict())}")
        responses = self.execute_multisearch_query(multisearch=multisearch)

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
                msg = f'Requested key {resource_key} query returned no results in ES'
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
            'doc': {
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
            new_value = ''
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
