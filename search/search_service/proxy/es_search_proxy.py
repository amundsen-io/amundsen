# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import (
    Dict, List, Optional,
)

from amundsen_common.models.search import Filter, SearchResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import (
    MultiSearch, Q, Search,
)
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.response import Response
from werkzeug.exceptions import InternalServerError

BOOL_QUERY = 'bool'
WILDCARD_QUERY = 'wildcard'
TERM_QUERY = 'term'
TERMS_QUERY = 'terms'


class Resource(Enum):
    TABLE = 0
    DASHBOARD = 1
    FEATURE = 2
    USER = 3


RESOURCE_STR_MAPPING = {
    'table': Resource.TABLE,
    'dashboard': Resource.DASHBOARD,
    'feature': Resource.FEATURE,
    'user': Resource.USER,
}


class ElasticsearchProxy():
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
        'cluster': 'cluster.raw'
    }

    # mapping to translate request for dashboard resources
    DASHBOARD_MAPPING = {
        'group_name': 'group_name.raw',
        'name': 'name.raw',
        'product': 'product',
        'tag': 'tags',
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
        'badges': 'badges'
    }

    USER_MAPPING = {
        'full_name': 'full_name',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email'
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
        if client:
            self.elasticsearch = client
        else:
            http_auth = (user, password) if user else None
            self.elasticsearch = Elasticsearch(host, http_auth=http_auth)
        self.page_size = page_size

    def _build_term_query(self, resource: Resource, query_term: str) -> Optional[Q]:
        """
        Builds the query object for the inputed search term
        """
        if not query_term:
            # We don't want to create multi_match query for ""
            # because it will result in no matches even with filters
            return None

        fields = []

        if resource == Resource.TABLE:
            fields = ["display_name^1000",
                      "name.raw^75",
                      "name^5",
                      "schema^3",
                      "description^3",
                      "column_names^2",
                      "column_descriptions",
                      "tags",
                      "badges",
                      "programmatic_descriptions"]
        elif resource == Resource.DASHBOARD:
            fields = ["name.raw^75",
                      "name^7",
                      "group_name.raw^15",
                      "group_name^7",
                      "description^3",
                      "query_names^3",
                      "chart_names^2"]
        elif resource == Resource.FEATURE:
            fields = ["feature_name.raw^25",
                      "feature_name^7",
                      "feature_group.raw^15",
                      "feature_group^7",
                      "version^7",
                      "description^3",
                      "status",
                      "entity",
                      "tags",
                      "badges"]
        elif resource == Resource.USER:
            fields = ["full_name.raw^30",
                      "full_name^5",
                      "first_name.raw^5",
                      "last_name.raw^5",
                      "first_name^3",
                      "last_name^3",
                      "email^3"]
        else:
            # TODO if you don't specify a resource match for all generic fields in the future
            raise ValueError(f"no fields defined for resource {resource}")

        return MultiMatch(query=query_term, fields=fields, type='most_fields')

    def _build_filters(self, resource: Resource, filters: List[Filter]) -> List:
        """
        Builds the query object for all of the filters given in the search request
        """
        mapping = self.RESOUCE_TO_MAPPING.get(resource)

        filter_queries: List = []

        for filter in filters:
            filter_name = mapping.get(filter.name) if mapping is not None \
                and mapping.get(filter.name) is not None else filter.name

            queries_per_term = [Q(WILDCARD_QUERY, **{filter_name: term}) for term in filter.values]

            if filter.operation == 'OR':
                filter_queries.append(Q(BOOL_QUERY, should=queries_per_term, minimum_should_match=1))

            elif filter.operation == 'AND':
                for q in queries_per_term:
                    filter_queries.append(q)

            else:
                msg = f"Invalid operation {filter.operation} for filter {filter_name} with values {filter.values}"
                raise ValueError(msg)

        return filter_queries

    def _build_elasticsearch_query(self, *,
                                   resource: Resource,
                                   query_term: str,
                                   filters: List[Filter]) -> Q:

        term_query = self._build_term_query(resource=resource,
                                            query_term=query_term)
        filters = self._build_filters(resource=resource, filters=filters)

        es_query = None

        if filters and term_query:
            es_query = Q('bool', should=[term_query], filter=filters)
        elif not filters and term_query:
            es_query = Q('bool', should=[term_query])
        elif filters and not term_query:
            es_query = Q('bool', filter=filters)
        else:
            raise ValueError("Invalid search query")

        return es_query

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
                results_count = r.hits.total.value
                if results_count > 0:
                    resource_type = r.hits.hits[0]._type
                    results = []
                    for search_result in r.hits.hits:
                        # mapping gives all the fields in the response
                        result = {}
                        fields = self.RESOUCE_TO_MAPPING[Resource[resource_type.upper()]]
                        for f in fields.keys():
                            # remove "raw" from mapping value
                            field = fields[f].split('.')[0]
                            result[f] = search_result._source[field]
                        result["search_score"] = search_result._score
                        results.append(result)
                    # replace empty results with actual results
                    results_per_resource[resource_type] = {
                        "results": results,
                        "total_results": results_count
                    }
            else:
                raise InternalServerError(f"Request to Elasticsearch failed: {r.failures}")

        return SearchResponse(msg="Success",
                              page_index=page_index,
                              results_per_page=results_per_page,
                              results=results_per_resource,
                              status_code=200)

    def execute_queries(self, queries: Dict[Resource, Q],
                        page_index: int,
                        results_per_page: int) -> List[Response]:
        multisearch = MultiSearch(using=self.elasticsearch)

        for resource in queries.keys():
            resource_str = resource.name.lower()
            resource_index = f"{resource_str}_search_index"
            query_for_resource = queries.get(resource)
            search = Search(index=resource_index).query(query_for_resource)

            # pagination
            start_from = page_index * results_per_page
            search = search[start_from:results_per_page]

            multisearch = multisearch.add(search)

        return multisearch.execute()

    def search(self, *,
               query_term: str,
               page_index: int,
               results_per_page: int,
               resource_types: List[Resource],
               filters: List[Filter]) -> SearchResponse:
        if resource_types == []:
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

        formatted_response = self._format_response(page_index=page_index,
                                                   results_per_page=results_per_page,
                                                   responses=responses,
                                                   resource_types=resource_types)

        return formatted_response
