# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List
import json

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, MultiSearch
from elasticsearch_dsl.query import MultiMatch

from search_service.models.results import SearchResult

class Filter():
    def __init__(self, name: str, values: list, operation: str) -> None:
        self.name = name
        self.values = values
        self.operation = operation

class ElasticsearchProxy():
    PRIMARY_ENTITIES = ['table', 'dashboard', 'user', 'feature']

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

    RESOUCE_TO_MAPPING = {
        'table': TABLE_MAPPING,
        'dashboard': DASHBOARD_MAPPING,
        'feature': FEATURE_MAPPING,
    }


    def __init__(self, *,
                 host: str = None,
                 user: str = '',
                 password: str = '',
                 client: Elasticsearch = None) -> None:
        # TODO actually implement this
        if client:
            self.elasticsearch = client
        else:
            http_auth = (user, password) if user else None
            # doesn't this go against the whole point oh having a singleton pattern?
            self.elasticsearch = Elasticsearch(host, http_auth=http_auth)

    def _build_query_pagination(self, page_index: int, results_per_page: int) -> Q:
        """
        TODO
        https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#pagination
        """
        pass

    def _build_term_query(self, resource:str, query_term: str) -> Q:
        """
        Builds the query object for the inputed search term
        TODO multimathc query
        """
        fields = []
        if resource == 'table':
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
        elif resource == 'dashboard':
            fields = ["name.raw^75",
                                   "name^7",
                                   "group_name.raw^15",
                                   "group_name^7",
                                   "description^3",
                                   "query_names^3",
                                   "chart_names^2"]
        elif resource == 'feature':
            fields = []
        elif resource == 'user':
            fields = ["full_name.raw^30",
                                   "full_name^5",
                                   "first_name.raw^5",
                                   "last_name.raw^5",
                                   "first_name^3",
                                   "last_name^3",
                                   "email^3"]
        else:
            raise ValueError(f"unknown resource, cannot search resource {resource}")

        return MultiMatch(query=query_term, fields=fields)


    def _build_filters_query(self, resource: str, filters: List[Filter]) -> Q:
        """
        Builds the query object for all of the filters given
        in the search request
        """
        mapping = self.RESOUCE_TO_MAPPING.get(resource)
        # if mapping == None:
            # Resource has no valid filtered search mapping like user
            # return None
        # TODO verify if relying on ES behavior when a filter doesn't exists for a resource works
        filter_queries: List[Q] = []
        for filter in filters:

            filter_name = mapping.get(filter.name)
            if filter_name == None:
                # Invalid filter name for resource, dont filter for this resource
                filter_name = filter.name

            has_wildcard = len([term for term in filter.values if '*' in term]) > 0

            if filter.operation == 'OR' and has_wildcard:
                filter_queries.append(Q('bool', filter=[Q('bool', should=[Q('wildcard',  **{filter_name: term}) for term in filter.values], minimum_should_match=1)]))
                pass

            elif filter.operation == 'OR' and not has_wildcard:
                filter_queries.append(Q('terms', **{filter_name: filter.values}))

            elif filter.operation == 'AND' and has_wildcard:
                filter_queries.append(Q('bool', filter=[Q('wildcard',  **{filter_name: term}) for term in filter.values]))

            elif filter.operation == 'AND' and not has_wildcard:
                [filter_queries.append(Q('term', **{filter_name: term})) for term in filter.values]

            else:
                raise ValueError(f"Invalid filter operation {filter.operation} for filter {filter_name} with values {filter.values}")

        filtered_query = Q('bool', filter=filter_queries)
        # print(json.dumps(filtered_query.to_dict()))
        
        return filtered_query


    def _build_elasticsearch_query(self, *,
                                   resource: str,
                                   query_term: str,
                                   filters: List[Filter]) -> Q:
        term_query = self._build_term_query(resource=resource,
                                            query_term=query_term)
        # print(json.dumps(term_query.to_dict()))
        filters_query = self._build_filters_query(resource=resource, filters=filters)
        if filters_query == None:
            return Q('bool', must=[term_query])
        else:
            return Q('bool',
                            must=[term_query, filters_query])
        # print(json.dumps(es_search_query.to_dict()))


    def execute_queries(self, queries: List[Q]):
        # TODO
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-multi-search.html
        multisearch = MultiSearch()
        search = Search(self.elasticsearch)
        for q in queries:
            multisearch.add(search=search.query(q))
        print(json.dumps(multisearch.to_dict()))
        raise ValueError("TEST")
        

    def search(self, *,
               query_term: str,
               page_index: int,
               results_per_page: int,
               resource_types: list,
               filters: List[Filter])  -> Any:
            # TODO change any for correct type when done and have schemas
        if resource_types == []:
            resource_types = self.PRIMARY_ENTITIES
        # if resource types are not defined then search all resources    
        queries: Dict[str, Q] = {}
        for resource in resource_types:
            queries[resource] = self._build_elasticsearch_query(resource=resource,
                                                   query_term=query_term,
                                                   filters=filters)
        print(queries)
        # TODO execute the queries
        self.execute_queries(queries=queries)
