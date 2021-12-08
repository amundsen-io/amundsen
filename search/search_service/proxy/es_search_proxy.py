# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
from enum import Enum
from typing import (
    Dict, List, Optional, Any, Tuple, Union
)

from amundsen_common.models.api import health_check
from amundsen_common.models.search import Filter, SearchResponse

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ElasticConnectionError
from elasticsearch_dsl import (
    MultiSearch, Q, Search,
)
from elasticsearch_dsl.document import Document
from elasticsearch_dsl.query import MultiMatch
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrDict, AttrList
from werkzeug.exceptions import InternalServerError

LOGGER = logging.getLogger(__name__)

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
            es_query = Q(BOOL_QUERY, should=[term_query], filter=filters)
        elif not filters and term_query:
            es_query = Q(BOOL_QUERY, should=[term_query])
        elif filters and not term_query:
            es_query = Q(BOOL_QUERY, filter=filters)
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
                            result_for_field = search_result._source[field]
                            # AttrList and AttrDict are not json serializable
                            if type(result_for_field) is AttrList:
                                result_for_field = list(result_for_field)
                            elif type(result_for_field) is AttrDict:
                                result_for_field = result_for_field.to_dict()
                            result[f] = result_for_field
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

    def get_document_by_key(self,
                            resource_key: str,
                            resource_type: Resource,
                            field: str) -> Tuple[Document, str]:
        key_query = {
            resource_type: Q(TERM_QUERY, key=resource_key),
        }
        response: Response = self.execute_queries(queries=key_query,
                                                  page_index=0,
                                                  results_per_page=1)[0]
        if response.success():
            results_count = response.hits.total.value
            if results_count > 0:
                es_result = response.hits.hits[0]
                resource_es_id = es_result._id
                field_value = es_result._source.get(field)
                if field_value:
                    # return document and current field value
                    return Document.get(id=resource_es_id), field_value
                else:
                    raise ValueError(f"Request for update of field {field} failed."
                                     f" This field does not exist for {key_query}")
            else:
                # no doc exists with given key in ES
                raise ValueError(f"Requested key {resource_key} returned no results in ES")
        else:
            raise InternalServerError(f"Request to Elasticsearch failed: {response.failures}")

    def _udpate_document_field_helper(self,
                                      current_value: Any,
                                      value: Optional[str],
                                      operation: str,
                                      delete: bool = False) -> Union[str, List]:
        new_value = current_value
        if delete:
            # if field and value given asssume current val is list
            if value:
                current_value = list(current_value)
                new_value = current_value.remove(value)
            else:
                # no value given when deleting implies
                # delete is happening on a single value field
                new_value = None
        else:
            if operation == 'overwrite':
                if type(current_value) is list:
                    new_value = [value]
                else:
                    new_value = value
            else:
                # operation is add
                if type(current_value) is list:
                    current_value = list(current_value)
                    new_value = current_value.append(value)
                else:
                    new_value = [current_value, value]
        return new_value

    def update_document_field(self, *,
                              resource_key: str,
                              resource_type: Resource,
                              field: str,
                              value: str = None,
                              operation: str = 'add',
                              delete: bool = False) -> str:
        mapped_field = self.RESOUCE_TO_MAPPING[resource_type].get(field)
        if not mapped_field:
            return f'Field {field} is not valid for resource {resource_type.name}'

        document, current_value = None, None
        try:
            document, current_value = self.get_document_by_key(resource_key=resource_key,
                                                               resource_type=resource_type,
                                                               field=mapped_field)
        except Exception as e:
            return f'Failed to get ES document for key {resource_key}. {e}'

        new_value = self._udpate_document_field_helper(current_value=current_value,
                                                       value=value,
                                                       operation=operation,
                                                       delete=delete)
        try:
            document.update(**{field: new_value})
        except Exception as e:
            return f'Failed to update field {field} with value {new_value} for {resource_key}. {e}'

        return f'ES document field {field} for {resource_key} with value {value} was updated successfully'
