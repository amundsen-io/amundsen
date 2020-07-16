# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import logging
import uuid
import itertools
from typing import Any, List, Dict, Union

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, query
from elasticsearch.exceptions import NotFoundError
from flask import current_app
from amundsen_common.models.index_map import USER_INDEX_MAP, TABLE_INDEX_MAP

from search_service import config
from search_service.api.dashboard import DASHBOARD_INDEX
from search_service.api.user import USER_INDEX
from search_service.api.table import TABLE_INDEX
from search_service.models.search_result import SearchResult
from search_service.models.table import Table, SearchTableResult
from search_service.models.user import SearchUserResult
from search_service.models.user import User
from search_service.models.dashboard import Dashboard, SearchDashboardResult
from search_service.models.tag import Tag
from search_service.proxy.base import BaseProxy
from search_service.proxy.statsd_utilities import timer_with_counter

# Default Elasticsearch index to use, if none specified
DEFAULT_ES_INDEX = 'table_search_index'

LOGGING = logging.getLogger(__name__)

# mapping to translate request for table resources
TABLE_MAPPING = {
    'badges': 'badges',
    'tag': 'tags',
    'schema': 'schema.raw',
    'table': 'name.raw',
    'column': 'column_names.raw',
    'database': 'database.raw',
    'cluster': 'cluster.raw'
}

# Maps payload to a class
TAG_MAPPING = {
    'badges': Tag,
    'tags': Tag
}

# mapping to translate request for dashboard resources
DASHBOARD_MAPPING = {
    'group_name': 'group_name.raw',
    'name': 'name.raw',
    'product': 'product',
    'tag': 'tags',
}


class ElasticsearchProxy(BaseProxy):
    """
    ElasticSearch connection handler
    """

    def __init__(self, *,
                 host: str = None,
                 user: str = '',
                 password: str = '',
                 client: Elasticsearch = None,
                 page_size: int = 10
                 ) -> None:
        """
        Constructs Elasticsearch client for interactions with the cluster.
        Allows caller to pass a fully constructed Elasticsearch client, {elasticsearch_client}
        or constructs one from the parameters provided.

        :param host: Elasticsearch host we should connect to
        :param auth_user: user name to use for authentication
        :param auth_pw: user password to use for authentication
        :param elasticsearch_client: Elasticsearch client to use, if provided
        :param  page_size: Number of search results to return per request
        """
        if client:
            self.elasticsearch = client
        else:
            http_auth = (user, password) if user else None
            self.elasticsearch = Elasticsearch(host, http_auth=http_auth)

        self.page_size = page_size

    def _get_search_result(self, page_index: int,
                           client: Search,
                           model: Any,
                           search_result_model: Any = SearchResult) -> Any:
        """
        Common helper function to get result.

        :param page_index:
        :param client:
        :param model: The model to import result(table, user etc)
        :return:
        """
        if model is None:
            raise Exception('ES Doc model must be provided!')

        results = []
        # Use {page_index} to calculate index of results to fetch from
        if page_index != -1:
            start_from = page_index * self.page_size
            end_at = start_from + self.page_size
            client = client[start_from:end_at]
        else:
            # if page index is -1, return everything
            client = client[0:client.count()]

        response = client.execute()

        for hit in response:
            try:
                # ES hit: {'_d_': {'key': xxx...}
                es_payload = hit.__dict__.get('_d_', {})
                if not es_payload:
                    raise Exception('The ES doc not contain required field')
                result = {}
                for attr, val in es_payload.items():
                    if attr in model.get_attrs():
                        result[attr] = self._get_instance(attr=attr, val=val)

                results.append(model(**result))
            except Exception:
                LOGGING.exception('The record doesnt contain specified field.')

        return search_result_model(total_results=response.hits.total,
                                   results=results)

    def _get_instance(self, attr: str, val: Any) -> Any:
        if attr in TAG_MAPPING:
            # maps a given badge or tag to a tag class
            return [TAG_MAPPING[attr](tag_name=property_val) for property_val in val]  # type: ignore
        else:
            return val

    def _search_helper(self, page_index: int,
                       client: Search,
                       query_name: dict,
                       model: Any,
                       search_result_model: Any = SearchResult) -> Any:
        """
        Constructs Elasticsearch Query DSL to:
          1. Use function score to customize scoring of search result. It currently uses "total_usage" field to score.
          `Link https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html`_
          2. Uses multi match query to search term in multiple fields.
          `Link https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html`_

        :param page_index:
        :param client:
        :param query_name: name of query to query the ES
        :return:
        """

        if query_name:
            q = query.Q(query_name)
            client = client.query(q)

        return self._get_search_result(page_index=page_index,
                                       client=client,
                                       model=model,
                                       search_result_model=search_result_model)

    @timer_with_counter
    def fetch_table_search_results(self, *,
                                   query_term: str,
                                   page_index: int = 0,
                                   index: str = '') -> SearchTableResult:
        """
        Query Elasticsearch and return results as list of Table objects

        :param query_term: search query term
        :param page_index: index of search page user is currently on
        :param index: current index for search. Provide different index for different resource.
        :return: SearchResult Object
        """
        current_index = index if index else \
            current_app.config.get(config.ELASTICSEARCH_INDEX_KEY, DEFAULT_ES_INDEX)
        if not query_term:
            # return empty result for blank query term
            return SearchTableResult(total_results=0, results=[])

        s = Search(using=self.elasticsearch, index=current_index)
        query_name = {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query_term,
                        "fields": ["display_name^1000",
                                   "name.raw^75",
                                   "name^5",
                                   "schema^3",
                                   "description^3",
                                   "column_names^2",
                                   "column_descriptions",
                                   "tags",
                                   "badges",
                                   "programmatic_descriptions"],
                    }
                },
                "field_value_factor": {
                    "field": "total_usage",
                    "modifier": "log2p"
                }
            }
        }

        return self._search_helper(page_index=page_index,
                                   client=s,
                                   query_name=query_name,
                                   model=Table,
                                   search_result_model=SearchTableResult)

    @staticmethod
    def get_model_by_index(index: str) -> Any:
        if index == TABLE_INDEX:
            return Table
        elif index == USER_INDEX:
            return User
        elif index == DASHBOARD_INDEX:
            return Dashboard

        raise Exception('Unable to map given index to a valid model')

    @staticmethod
    def parse_filters(filter_list: Dict,
                      index: str) -> str:
        query_list = []  # type: List[str]
        if index == TABLE_INDEX:
            mapping = TABLE_MAPPING
        elif index == DASHBOARD_INDEX:
            mapping = DASHBOARD_MAPPING
        else:
            raise Exception(f'index {index} doesnt exist nor support search filter')
        for category, item_list in filter_list.items():
            mapped_category = mapping.get(category)
            if mapped_category is None:
                LOGGING.warn(f'Unsupported filter category: {category} passed in list of filters')
            elif item_list is '' or item_list == ['']:
                LOGGING.warn(f'The filter value cannot be empty.In this case the filter {category} is ignored')
            else:
                query_list.append(mapped_category + ':' + '(' + ' OR '.join(item_list) + ')')

        if len(query_list) == 0:
            return ''

        return ' AND '.join(query_list)

    @staticmethod
    def validate_filter_values(search_request: dict) -> Any:
        if 'filters' in search_request:
            filter_values_list = search_request['filters'].values()
            # Ensure all values are arrays
            filter_values_list = list(
                map(lambda x: x if type(x) == list else [x], filter_values_list))
            # Flatten the array of arrays
            filter_values_list = list(itertools.chain.from_iterable(filter_values_list))
            # Check if / or : exist in any of the values
            if any(("/" in str(item) or ":" in str(item)) for item in (filter_values_list)):
                return False
            return True

    @staticmethod
    def parse_query_term(query_term: str,
                         index: str) -> str:
        # TODO: Might be some issue with using wildcard & underscore
        # https://discuss.elastic.co/t/wildcard-search-with-underscore-is-giving-no-result/114010/8
        if index == TABLE_INDEX:
            query_term = f'(name:(*{query_term}*) OR name:({query_term}) ' \
                         f'OR schema:(*{query_term}*) OR schema:({query_term}) ' \
                         f'OR description:(*{query_term}*) OR description:({query_term}) ' \
                         f'OR column_names:(*{query_term}*) OR column_names:({query_term}) ' \
                         f'OR column_descriptions:(*{query_term}*) OR column_descriptions:({query_term}))'
        elif index == DASHBOARD_INDEX:
            query_term = f'(name:(*{query_term}*) OR name:({query_term}) ' \
                         f'OR group_name:(*{query_term}*) OR group_name:({query_term}) ' \
                         f'OR query_names:(*{query_term}*) OR query_names:({query_term}) ' \
                         f'OR description:(*{query_term}*) OR description:({query_term}) ' \
                         f'OR tags:(*{query_term}*) OR tags:({query_term}) ' \
                         f'OR badges:(*{query_term}*) OR badges:({query_term}) ' \
                         f'OR product:(*{query_term}*) OR product:({query_term}))'
        else:
            raise Exception(f'index {index} doesnt exist nor support search filter')
        return query_term

    @classmethod
    def convert_query_json_to_query_dsl(self, *,
                                        search_request: dict,
                                        query_term: str,
                                        index: str) -> str:
        """
        Convert the generic query json to query DSL
        e.g
        ```
        {
            'type': 'AND'
            'filters': {
                'database': ['hive', 'bigquery'],
                'schema': ['test-schema1', 'test-schema2'],
                'table': ['*amundsen*'],
                'column': ['*ds*']
                'tag': ['test-tag']
            }
        }

        This generic JSON will convert into DSL depending on the backend engines.

        E.g in Elasticsearch, it will become
        'database':('hive' OR 'bigquery') AND
        'schema':('test-schema1' OR 'test-schema2') AND
        'table':('*amundsen*') AND
        'column':('*ds*') AND
        'tag':('test-tag')
        ```

        :param search_request:
        :param query_term:
        :param index: table_index, dashboard_index
        :return: The search engine query DSL
        """
        filter_list = search_request.get('filters')
        add_query = ''
        query_dsl = ''
        if filter_list:
            valid_filters = self.validate_filter_values(search_request)
            if valid_filters is False:
                raise Exception(
                    'The search filters contain invalid characters and thus cannot be handled by ES')
            query_dsl = self.parse_filters(filter_list,
                                           index)

        if query_term:
            add_query = self.parse_query_term(query_term,
                                              index)

        if not query_dsl and not add_query:
            raise Exception('Unable to convert parameters to valid query dsl')

        result = ''
        if query_dsl and add_query:
            result = query_dsl + ' AND ' + add_query
        elif add_query and not query_dsl:
            result = add_query
        elif query_dsl and not add_query:
            result = query_dsl

        return result

    @timer_with_counter
    def fetch_search_results_with_filter(self, *,
                                         query_term: str,
                                         search_request: dict,
                                         page_index: int = 0,
                                         index: str = '') -> Union[SearchDashboardResult,
                                                                   SearchTableResult]:
        """
        Query Elasticsearch and return results as list of Table objects
        :param search_request: A json representation of search request
        :param page_index: index of search page user is currently on
        :param index: current index for search. Provide different index for different resource.
        :return: SearchResult Object
        """
        current_index = index if index else \
            current_app.config.get(config.ELASTICSEARCH_INDEX_KEY, DEFAULT_ES_INDEX)  # type: str
        if current_index == DASHBOARD_INDEX:
            search_model = SearchDashboardResult  # type: Any
        elif current_index == TABLE_INDEX:
            search_model = SearchTableResult
        else:
            raise RuntimeError(f'the {index} doesnt have search filter support')
        if not search_request:
            # return empty result for blank query term
            return search_model(total_results=0, results=[])

        try:
            query_string = self.convert_query_json_to_query_dsl(search_request=search_request,
                                                                query_term=query_term,
                                                                index=current_index)  # type: str
        except Exception as e:
            LOGGING.exception(e)
            # return nothing if any exception is thrown under the hood
            return search_model(total_results=0, results=[])

        s = Search(using=self.elasticsearch, index=current_index)

        query_name = {
            "function_score": {
                "query": {
                    "query_string": {
                        "query": query_string
                    }
                },
                "field_value_factor": {
                    "field": "total_usage",
                    "modifier": "log2p"
                }
            }
        }

        model = self.get_model_by_index(current_index)
        return self._search_helper(page_index=page_index,
                                   client=s,
                                   query_name=query_name,
                                   model=model,
                                   search_result_model=search_model)

    @timer_with_counter
    def fetch_user_search_results(self, *,
                                  query_term: str,
                                  page_index: int = 0,
                                  index: str = '') -> SearchUserResult:
        if not index:
            raise Exception('Index cant be empty for user search')
        if not query_term:
            # return empty result for blank query term
            return SearchUserResult(total_results=0, results=[])

        s = Search(using=self.elasticsearch, index=index)

        # Don't use any weight(total_follow, total_own, total_use)
        query_name = {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query_term,
                        "fields": ["full_name.raw^30",
                                   "full_name^5",
                                   "first_name.raw^5",
                                   "last_name.raw^5",
                                   "first_name^3",
                                   "last_name^3",
                                   "email^3"],
                        "operator": "and"
                    }
                }
            }
        }

        return self._search_helper(page_index=page_index,
                                   client=s,
                                   query_name=query_name,
                                   model=User,
                                   search_result_model=SearchUserResult)

    @timer_with_counter
    def fetch_dashboard_search_results(self, *,
                                       query_term: str,
                                       page_index: int = 0,
                                       index: str = '') -> SearchDashboardResult:
        """
        Fetch dashboard search result with fuzzy search

        :param query_term:
        :param page_index:
        :param index:
        :return:
        """
        current_index = index if index else \
            current_app.config.get(config.ELASTICSEARCH_INDEX_KEY, DEFAULT_ES_INDEX)

        if not query_term:
            # return empty result for blank query term
            return SearchDashboardResult(total_results=0, results=[])
        s = Search(using=self.elasticsearch, index=current_index)

        query_name = {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query_term,
                        "fields": ["name.raw^75",
                                   "name^7",
                                   "group_name.raw^15",
                                   "group_name^7",
                                   "description^3",
                                   "query_names^3"]
                    }
                },
                "field_value_factor": {
                    "field": "total_usage",
                    "modifier": "log2p"
                }
            }
        }

        return self._search_helper(page_index=page_index,
                                   client=s,
                                   query_name=query_name,
                                   model=Dashboard,
                                   search_result_model=SearchDashboardResult)

    # The following methods are related to document API that needs to update
    @timer_with_counter
    def create_document(self, *, data: List[Table], index: str) -> str:
        """
        Creates new index in elasticsearch, then routes traffic to the new index
        instead of the old one
        :return: str
        """

        if not index:
            raise Exception('Index cant be empty for creating document')
        if not data:
            LOGGING.warn('Received no data to upload to Elasticsearch')
            return ''

        return self._create_document_helper(data=data, index=index)

    @timer_with_counter
    def update_document(self, *, data: List[Table], index: str) -> str:
        """
        Updates the existing index in elasticsearch
        :return: str
        """
        if not index:
            raise Exception('Index cant be empty for updating document')
        if not data:
            LOGGING.warn('Received no data to upload to Elasticsearch')
            return ''

        return self._update_document_helper(data=data, index=index)

    @timer_with_counter
    def delete_document(self, *, data: List[str], index: str) -> str:
        if not index:
            raise Exception('Index cant be empty for deleting document')
        if not data:
            LOGGING.warn('Received no data to upload to Elasticsearch')
            return ''

        return self._delete_document_helper(data=data, index=index)

    def _create_document_helper(self, data: List[Table], index: str) -> str:
        # fetch indices that use our chosen alias (should only ever return one in a list)
        indices = self._fetch_old_index(index)

        for i in indices:
            # build a list of elasticsearch actions for bulk upload
            actions = self._build_index_actions(data=data, index_key=i)

            # bulk create or update data
            self._bulk_helper(actions)

        return index

    def _update_document_helper(self, data: List[Table], index: str) -> str:
        # fetch indices that use our chosen alias (should only ever return one in a list)
        indices = self._fetch_old_index(index)

        for i in indices:
            # build a list of elasticsearch actions for bulk update
            actions = self._build_update_actions(data=data, index_key=i)

            # bulk update existing documents in index
            self._bulk_helper(actions)

        return index

    def _delete_document_helper(self, data: List[str], index: str) -> str:
        # fetch indices that use our chosen alias
        indices = self._fetch_old_index(index)

        # set the document type
        type = User.get_type() if index is USER_INDEX else Table.get_type()

        for i in indices:
            # build a list of elasticsearch actions for bulk deletion
            actions = self._build_delete_actions(data=data, index_key=i, type=type)

            # bulk delete documents in index
            self._bulk_helper(actions)

        return index

    def _build_index_actions(self, data: List[Table], index_key: str) -> List[Dict[str, Any]]:
        actions = list()
        for item in data:
            index_action = {'index': {'_index': index_key, '_type': item.get_type(), '_id': item.get_id()}}
            actions.append(index_action)
            actions.append(item.__dict__)
        return actions

    def _build_update_actions(self, data: List[Table], index_key: str) -> List[Dict[str, Any]]:
        actions = list()

        for item in data:
            actions.append({'update': {'_index': index_key, '_type': item.get_type(), '_id': item.get_id()}})
            actions.append({'doc': item.__dict__})
        return actions

    def _build_delete_actions(self, data: List[str], index_key: str, type: str) -> List[Dict[str, Any]]:
        return [{'delete': {'_index': index_key, '_id': id, '_type': type}} for id in data]

    def _bulk_helper(self, actions: List[Dict[str, Any]]) -> None:
        result = self.elasticsearch.bulk(actions)

        if result['errors']:
            # ES's error messages are nested within elasticsearch objects and can
            # fail silently if you aren't careful
            LOGGING.error('Error during Elasticsearch bulk actions')
            LOGGING.debug(result['items'])
            return

    def _fetch_old_index(self, alias: str) -> List[str]:
        """
        Retrieve all indices that are currently tied to alias
        (Can most often expect only one index to be returned in this list)
        :return: list of elasticsearch indices
        """
        try:
            indices = self.elasticsearch.indices.get_alias(alias).keys()
            return indices
        except NotFoundError:
            LOGGING.warn('Received index not found error from Elasticsearch', exc_info=True)

            # create a new index if there isn't already one that is usable
            new_index = self._create_index_helper(alias=alias)
            return [new_index]

    def _create_index_helper(self, alias: str) -> str:
        def _get_mapping(alias: str) -> str:
            if alias is USER_INDEX:
                return USER_INDEX_MAP
            elif alias is TABLE_INDEX:
                return TABLE_INDEX_MAP
            return ''
        index_key = str(uuid.uuid4())
        mapping: str = _get_mapping(alias=alias)
        self.elasticsearch.indices.create(index=index_key, body=mapping)

        # alias our new index
        index_actions = {'actions': [{'add': {'index': index_key, 'alias': alias}}]}
        self.elasticsearch.indices.update_aliases(index_actions)
        return index_key
