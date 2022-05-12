# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any, Dict, List

from amundsen_common.models.search import Filter, HighlightOptions, SearchResponse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search, MultiSearch
from elasticsearch_dsl.query import Match, RankFeature
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrDict, AttrList
from flask import current_app

from search_service import config
from search_service.proxy.es_proxy_utils import Resource
from search_service.proxy.es_proxy_v2 import BOOL_QUERY, ElasticsearchProxyV2
from werkzeug.exceptions import InternalServerError

LOGGER = logging.getLogger(__name__)

# ES query constants

DEFAULT_FUZZINESS = "AUTO"

# using fvh as the default highlighter because it supports very large documents
DEFAULT_HIGHLIGHTER = 'fvh'


class ElasticsearchProxyV2_1(ElasticsearchProxyV2):

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

    # The overriding of __new__ here is a temporary solution to provide backwards compatiblity
    # until most of the community has moved to using the new Elasticsearch mappings and it will
    # be removed once ElasticsearchProxyV2 id deprecated
    def __new__(cls: Any,
                host: str,
                user: str,
                password: str,
                client: Elasticsearch,
                page_size: int, *args: str, **kwargs: int) -> Any:
        elasticsearch_client = None
        if client:
            elasticsearch_client = client
        else:
            http_auth = (user, password) if user else None
            elasticsearch_client = Elasticsearch(host, http_auth=http_auth)

        # check if any index uses the most up to date mappings (version == 2)
        indices = elasticsearch_client.indices.get_alias(index='*')
        mappings_up_to_date = False
        for index in indices:
            index_mapping = elasticsearch_client.indices.get_mapping(index=index).get(index)
            mapping_meta_field = index_mapping.get('mappings').get('_meta')
            if mapping_meta_field is not None and mapping_meta_field.get('version') == 2:
                mappings_up_to_date = True
                break

        if mappings_up_to_date:
            # Use ElasticsearchProxyV2_1 if indexes are up to date with mappings
            obj = super(ElasticsearchProxyV2_1, cls).__new__(cls)
            return obj

        # If old mappings are used proxy client should be ElasticsearchProxyV2
        obj = super(ElasticsearchProxyV2_1, cls).__new__(ElasticsearchProxyV2)
        obj.__init__(host=host,
                     user=user,
                     password=password,
                     client=elasticsearch_client,
                     page_size=page_size)
        return obj

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
            columns_subfield = 'columns.general'
            should_clauses.extend([
                Match(schema={
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "max_expansions": 10,
                    "boost": 3
                }),
                Match(**{columns_subfield: {
                    "query": query_term,
                    "fuzziness": DEFAULT_FUZZINESS,
                    "boost": 2,
                    "max_expansions": 10
                }}),
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

    def _search_highlight(self,
                          resource: Resource,
                          search: Search,
                          highlight_options: Dict[Resource, HighlightOptions]) -> Search:
        # get highlighting options for resource
        highlighting_enabled = highlight_options.get(resource).enable_highlight

        if highlighting_enabled and resource != Resource.USER:
            # default highlighted fields
            search = search.highlight('name',
                                    type=DEFAULT_HIGHLIGHTER,
                                    number_of_fragments=0)
            search = search.highlight('description',
                                    type=DEFAULT_HIGHLIGHTER,
                                    number_of_fragments=5, order='none')
            if resource == Resource.TABLE:
                search = search.highlight('columns.general',
                                        type=DEFAULT_HIGHLIGHTER,
                                        number_of_fragments=5, order='score')
            if resource == Resource.DASHBOARD:
                search = search.highlight('chart_names',
                                        type=DEFAULT_HIGHLIGHTER,
                                        number_of_fragments=5, order='score')
                search = search.highlight('query_names',
                                        type=DEFAULT_HIGHLIGHTER,
                                        number_of_fragments=5, order='score')

        return search

    def _format_response(self, page_index: int,
                         results_per_page: int,
                         responses: List[Response],
                         resource_types: List[Resource]) -> SearchResponse:
        resource_types_str = [r.name.lower() for r in resource_types]
        no_results_for_resource = {
            "results": [],
            "total_results": 0
        }
        results_per_resource = {resource: no_results_for_resource for resource in resource_types_str}

        for r in responses:
            if r.success():
                if len(r.hits.hits) > 0:
                    resource_type = r.hits.hits[0]._source['resource_type']
                    fields = self.RESOUCE_TO_MAPPING[Resource[resource_type.upper()]]
                    results = []
                    for search_result in r.hits.hits:
                        # mapping gives all the fields in the response
                        result = {}
                        highlights_per_field = {}
                        for f in fields.keys():
                            # remove "keyword" from mapping value
                            field = fields[f].split('.')[0]
                            try:
                                result_for_field = search_result._source[field]
                                # AttrList and AttrDict are not json serializable
                                if type(result_for_field) is AttrList:
                                    result_for_field = list(result_for_field)
                                elif type(result_for_field) is AttrDict:
                                    result_for_field = result_for_field.to_dict()
                                result[f] = result_for_field
                            except KeyError:
                                logging.debug(f'Field: {field} missing in search response.')
                                pass
                        # add highlighting results if they exist for a hit
                        try:
                            for hf in search_result.highlight.to_dict().keys():
                                field = hf.split('.')[0]
                                field_highlight = search_result.highlight[hf]
                                if type(field_highlight) is AttrList:
                                    field_highlight = list(field_highlight)
                                elif type(field_highlight) is AttrDict:
                                    field_highlight = field_highlight.to_dict()
                                highlights_per_field[field] = field_highlight

                            result["highlight"] = highlights_per_field
                        except AttributeError:
                            # no highlights
                            pass

                        result["search_score"] = search_result._score
                        results.append(result)
                    # replace empty results with actual results
                    results_per_resource[resource_type] = {
                        "results": results,
                        "total_results": r.hits.total.value
                    }

            else:
                raise InternalServerError(f"Request to Elasticsearch failed: {r.failures}")

        return SearchResponse(msg="Success",
                              page_index=page_index,
                              results_per_page=results_per_page,
                              results=results_per_resource,
                              status_code=200)

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
        if resource_types == []:
            # if resource types are not defined then search all resources
            resource_types = self.PRIMARY_ENTITIES

        multisearch = MultiSearch(using=self.elasticsearch)
        print('THIS SEARCH')
        for resource in resource_types:
            # build a query for each resource to search
            query_for_resource = self._build_elasticsearch_query(resource=resource,
                                                                query_term=query_term,
                                                                filters=filters)
            # wrap the query in a search object
            search = Search(index=self.get_index_alias_for_resource(resource_type=resource)).query(query_for_resource)

            # highlighting
            search = self._search_highlight(resource=resource,
                                            search=search,
                                            highlight_options=highlight_options)

            # pagination
            start_from = page_index * results_per_page
            end = results_per_page * (page_index + 1)
            search = search[start_from:end]
            # add search object to multisearch
            LOGGER.info(json.dumps(search.to_dict()))
            multisearch = multisearch.add(search)

        responses = self.execute_multisearch_query(multisearch=multisearch)

        formatted_response = self._format_response(page_index=page_index,
                                                   results_per_page=results_per_page,
                                                   responses=responses,
                                                   resource_types=resource_types)

        return formatted_response