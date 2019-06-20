import logging
import re
from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, query
from flask import current_app

from search_service import config
from search_service.models.search_result import SearchResult
from search_service.models.table import Table
from search_service.models.user import User
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
            self.elasticsearch = Elasticsearch(host, http_auth=(user, password))

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
        start_from = page_index * self.page_size
        end_at = start_from + self.page_size
        client = client[start_from:end_at]
        response = client.execute()

        for hit in response:

            try:
                results.append(model(**vars(hit)))
            except Exception:
                LOGGING.exception('The record doesnt contain specified field.')

        return SearchResult(total_results=response.hits.total,
                            results=results)

    def _search_helper(self, query_term: str,
                       page_index: int,
                       client: Search,
                       query_name: dict,
                       model: Any) -> SearchResult:
        """
        Constructs Elasticsearch Query DSL to:
          1. Use function score to customize scoring of search result. It currently uses "total_usage" field to score.
          `Link https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html`_
          2. Uses multi match query to search term in multiple fields.
          `Link https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html`_

        :param query_term:
        :param page_index:
        :param client:
        :param query_name: name of query to query the ES
        :return:
        """

        if query_term and query_name:
            q = query.Q(query_name)
            client = client.query(q)
            return self._get_search_result(page_index=page_index,
                                           client=client,
                                           model=model)
        else:
            raise Exception('Query term and query name must be provided!')

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
        :param field_name: field name to do the searching(e.g schema_name, tag_names)
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
            'schema': 'schema_name.raw',
            'table': 'name.raw',
            'column': 'column_names.raw'
        }

        # Convert field name to actual type in ES doc
        field_name = mapping[field_name]

        # We allow user to use ? * for wildcard support
        m = re.search('[\?\*]', field_value)
        if m:
            return self._search_wildcard_helper(field_value=field_value,
                                                page_index=page_index,
                                                client=s,
                                                field_name=field_name)
        else:
            query_name = {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": query_term,
                            "fields": ["name.raw^30",
                                       "name^5",
                                       "schema_name^3",
                                       "description^3",
                                       "column_names^2",
                                       "column_descriptions", "tags"]
                        }
                    },
                    "field_value_factor": {
                        "field": "total_usage",
                        "modifier": "log1p"
                    }
                }
            }
            s = s.filter('term', **{field_name: field_value})
            return self._search_helper(query_term=query_term,
                                       page_index=page_index,
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
                        "fields": ["name.raw^30",
                                   "name^5",
                                   "schema_name^3",
                                   "description^3",
                                   "column_names^2",
                                   "column_descriptions", "tags"]
                    }
                },
                "field_value_factor": {
                    "field": "total_usage",
                    "modifier": "log1p"
                }
            }
        }

        return self._search_helper(query_term=query_term,
                                   page_index=page_index,
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
                        "fields": ["name.raw^30",
                                   "name^5",
                                   "first_name.raw^5",
                                   "last_name.raw^5",
                                   "first_name^3",
                                   "last_name^3",
                                   "email^3"]
                    }
                }
            }
        }

        return self._search_helper(query_term=query_term,
                                   page_index=page_index,
                                   client=s,
                                   query_name=query_name,
                                   model=User)
