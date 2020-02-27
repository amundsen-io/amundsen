import logging
import re
import uuid
from typing import Any, List, Dict

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, query
from elasticsearch.exceptions import NotFoundError
from flask import current_app

from search_service import config
from search_service.api.user import USER_INDEX
from search_service.api.table import TABLE_INDEX
from search_service.models.search_result import SearchResult
from search_service.models.table import Table
from search_service.models.user import User
from search_service.models.index_map import IndexMap, USER_INDEX_MAP
from search_service.proxy.base import BaseProxy
from search_service.proxy.statsd_utilities import timer_with_counter

# Default Elasticsearch index to use, if none specified
DEFAULT_ES_INDEX = 'table_search_index'

LOGGING = logging.getLogger(__name__)


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
                           model: Any) -> SearchResult:
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
                        result[attr] = val
                results.append(model(**result))
            except Exception:
                LOGGING.exception('The record doesnt contain specified field.')

        return SearchResult(total_results=response.hits.total,
                            results=results)

    def _search_helper(self, page_index: int,
                       client: Search,
                       query_name: dict,
                       model: Any) -> SearchResult:
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
                                       model=model)

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
        index_key = str(uuid.uuid4())
        mapping: str = self._get_mapping(alias=alias)
        self.elasticsearch.indices.create(index=index_key, body=mapping)

        # alias our new index
        index_actions = {'actions': [{'add': {'index': index_key, 'alias': alias}}]}
        self.elasticsearch.indices.update_aliases(index_actions)
        return index_key

    def _get_mapping(self, alias: str) -> str:
        if alias is USER_INDEX:
            return IndexMap(map=USER_INDEX_MAP).mapping
        elif alias is TABLE_INDEX:
            return IndexMap().mapping
        return ''

    def _search_wildcard_helper(self, field_value: str,
                                page_index: int,
                                client: Search,
                                field_name: str) -> SearchResult:
        """
        Do a wildcard match search with the query term.

        :param field_value:
        :param page_index:
        :param client:
        :param field_name
        :param query_name: name of query
        :return:
        """
        if field_value and field_name:
            d = {
                "wildcard": {
                    field_name: field_value
                }
            }
            q = query.Q(d)
            client = client.query(q)

        return self._get_search_result(page_index=page_index,
                                       client=client,
                                       model=Table)

    @timer_with_counter
    def fetch_table_search_results_with_field(self, *,
                                              query_term: str,
                                              field_name: str,
                                              field_value: str,
                                              page_index: int = 0,
                                              index: str = '') -> SearchResult:
        """
        Query Elasticsearch and return results as list of Table objects
        In order to support search filtered by field, it uses Elasticsearch's filter.
        https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=filter#dotted-fields

        :param query_term: search query term
        :param field_name: field name to do the searching(e.g schema, tag_names)
        :param field_value: value for the field for filtering
        :param page_index: index of search page user is currently on
        :param index: current index for search. Provide different index for different resource.
        :return: SearchResult Object
        :return:
        """

        current_index = index if index else \
            current_app.config.get(config.ELASTICSEARCH_INDEX_KEY, DEFAULT_ES_INDEX)

        s = Search(using=self.elasticsearch, index=current_index)

        mapping = {
            'tag': 'tags',
            'schema': 'schema.raw',
            'table': 'name.raw',
            'column': 'column_names.raw',
            'database': 'database.raw'
        }

        if query_term:
            query_name = {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": query_term,
                            "fields": ["display_name^1000",
                                       "name.raw^30",
                                       "name^5",
                                       "schema^3",
                                       "description^3",
                                       "column_names^2",
                                       "column_descriptions", "tags"],
                        }
                    },
                    "field_value_factor": {
                        "field": "total_usage",
                        "modifier": "log2p"
                    }
                }
            }
        else:
            query_name = {}

        # Convert field name to actual type in ES doc
        new_field_name = mapping[field_name]

        # We allow user to use ? * for wildcard support
        m = re.search('[?*]', field_value)
        if m:
            return self._search_wildcard_helper(field_value=field_value,
                                                page_index=page_index,
                                                client=s,
                                                field_name=new_field_name)
        else:

            s = s.filter('term', **{new_field_name: field_value})
            return self._search_helper(page_index=page_index,
                                       client=s,
                                       query_name=query_name,
                                       model=Table)

    @timer_with_counter
    def fetch_table_search_results(self, *,
                                   query_term: str,
                                   page_index: int = 0,
                                   index: str = '') -> SearchResult:
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
            return SearchResult(total_results=0, results=[])

        s = Search(using=self.elasticsearch, index=current_index)
        query_name = {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query_term,
                        "fields": ["display_name^1000",
                                   "name.raw^30",
                                   "name^5",
                                   "schema^3",
                                   "description^3",
                                   "column_names^2",
                                   "column_descriptions", "tags"],
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
                                   model=Table)

    @timer_with_counter
    def fetch_user_search_results(self, *,
                                  query_term: str,
                                  page_index: int = 0,
                                  index: str = '') -> SearchResult:
        if not index:
            raise Exception('Index cant be empty for user search')
        if not query_term:
            # return empty result for blank query term
            return SearchResult(total_results=0, results=[])

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
                                   model=User)

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
