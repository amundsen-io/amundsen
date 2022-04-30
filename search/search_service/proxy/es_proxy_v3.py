# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import (
    Any, Dict, List, Union,
)

from amundsen_common.models.api import health_check
from amundsen_common.models.search import Filter, SearchResponse
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ElasticConnectionError, ElasticsearchException
from elasticsearch_dsl import (
    MultiSearch, Q, Search,
)

from elasticsearch_dsl.query import Match, RankFeature
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrDict, AttrList
from werkzeug.exceptions import InternalServerError

from search_service.proxy.es_proxy_utils import Resource
from search_service.proxy.es_proxy_v2 import ElasticsearchProxyV2
from upstream.docs.search.search_service.proxy import elasticsearch

LOGGER = logging.getLogger(__name__)

# ES query constants

BOOL_QUERY = 'bool'
WILDCARD_QUERY = 'wildcard'
TERM_QUERY = 'term'
TERMS_QUERY = 'terms'

DEFAULT_FUZZINESS = "AUTO"


class ElasticsearchProxyV3(ElasticsearchProxyV2):

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
        'column': 'columns.keyword',
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

    RESOUCE_TO_MAPPING = {
        Resource.TABLE: TABLE_MAPPING,
        Resource.DASHBOARD: DASHBOARD_MAPPING,
        Resource.FEATURE: FEATURE_MAPPING,
        Resource.USER: USER_MAPPING,
    }

    def __init__(self, *,
                host: str = None,
                user: str = '',
                password: str = '',
                client: Elasticsearch = None,
                page_size: int = 10) -> None:
        LOGGER.info("V3")
        super().__init__(host=host,
                         user=user,
                         password=password,
                         client=client,
                         page_size=page_size)

    def get_index_for_resource(self, resource_type: Resource) -> str:
        resource_str = resource_type.name.lower()
        return f"new_{resource_str}_search_index"

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
                "max_expansions": 10,
                "boost": 5
            }),
            Match(description={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
                "max_expansions": 10,
                "boost": 1.5
            }),
            Match(badges={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
                "max_expansions": 10
            }),
            Match(tags={
                "query": query_term,
                "fuzziness": DEFAULT_FUZZINESS,
                "max_expansions": 10
            }),
        ]

        if resource == Resource.TABLE:
            should_clauses.extend([
                Match(schema={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 3
                }),
                Match(columns={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 2,
                    "max_expansions": 5
                }),
            ])
        elif resource == Resource.DASHBOARD:
            should_clauses.extend([
                Match(group_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 3
                }),
                Match(query_names={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 2
                }),
                Match(chart_names={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 2
                }),
                Match(uri={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 4
                }),
            ])
        elif resource == Resource.FEATURE:
            should_clauses.extend([
                Match(feature_group={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 3
                }),
                Match(version={
                    "query": query_term
                }),
                Match(entity={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
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
                    "max_expansions": 10,
                    "boost": 5
                }),
                Match(first_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 3
                }),
                Match(last_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 3
                }),
                Match(team_name={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10
                }),
                Match(key={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 4
                }),
            ]

        must_clauses: List[Q] = [Q(BOOL_QUERY, should=should_clauses)]

        return must_clauses

    def _build_should_query(self, resource: Resource, query_term: str) -> List[Q]:

        # no scoring happens if there is no search term
        if query_term == '':
            return []

        # general usage metric for searcheable resources
        usage_metric_fields = {
            'total_usage': 10.0,
        }

        if resource == Resource.TABLE:
            usage_metric_fields = {
                **usage_metric_fields,
                'unique_usage': 10.0,
            }
        if resource == Resource.USER:
            usage_metric_fields = {
                'total_read': 10.0,
                'total_own': 10.0,
                'total_follow': 10.0,
            }

        rank_feature_queries = []

        for metric in usage_metric_fields.keys():
            field_name = f'usage.{metric}'
            boost = usage_metric_fields[metric]
            rank_feature_query = RankFeature(field=field_name,
                                             boost=boost)
            rank_feature_queries.append(rank_feature_query)

        return rank_feature_queries

    def __new__(cls, host: str,
                user: str,
                password: str,
                client: Elasticsearch,
                page_size):

        elasticsearch_client = None
        if client:
            elasticsearch_client = client
        else:
            http_auth = (user, password) if user else None
            elasticsearch_client = Elasticsearch(host, http_auth=http_auth)
        # check if any mappings have new mappings 
        
        indices = elasticsearch_client.indices.get_alias('*')
        mappings_up_to_date = False
        for index in indices:
            index_mapping = elasticsearch_client.indices.get_mapping(index).get(index)
            mapping_meta_field = index_mapping.get('mappings').get('_meta')
            if mapping_meta_field is not None and mapping_meta_field.get('new_mapping') is True:
                mappings_up_to_date = True
                break

        if mappings_up_to_date:
            obj = super().__new__(ElasticsearchProxyV3)
            obj.__init__(host=host,
                        user=user,
                        password=password,
                        client=elasticsearch_client,
                        page_size=page_size)
            return obj

        obj = super().__new__(ElasticsearchProxyV2)
        obj.__init__(host=host,
                         user=user,
                         password=password,
                         client=elasticsearch_client,
                         page_size=page_size)
        return obj