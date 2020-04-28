import logging
import warnings

from atlasclient.client import Atlas
from atlasclient.exceptions import BadRequest
from atlasclient.models import Entity, EntityCollection
# default search page size
from atlasclient.utils import parse_table_qualified_name, make_table_qualified_name
from typing import Any, List, Dict, Tuple, Optional
from re import sub

from search_service.models.search_result import SearchResult
from search_service.models.table import Table
from search_service.models.tag import Tag
from search_service.proxy import BaseProxy
from search_service.proxy.statsd_utilities import timer_with_counter

LOGGER = logging.getLogger(__name__)


class AtlasProxy(BaseProxy):
    """
    AtlasSearch connection handler
    """
    ATLAS_TABLE_ENTITY = 'Table'
    ATLAS_QN_ATTRIBUTE = 'qualifiedName'

    def __init__(self, *,
                 host: str = None,
                 user: str = '',
                 password: str = '',
                 client: Atlas = None,
                 page_size: int = 10) -> None:
        self.atlas = client or Atlas(host, username=user, password=password)
        self.page_size = page_size

    @staticmethod
    def _extract_entities(collections: EntityCollection) -> List[Entity]:
        """
        Helper method for flattening all collections from {collections}

        :return: list of all entities
        """
        entities: List[Entity] = []

        for collection in collections:
            entities.extend(collection.entities)
        return entities

    def _prepare_tables(self, response: EntityCollection, enhance_metadata: bool = False) -> List[Table]:
        """
        Based on an Atlas {response} with table entities, we render Table objects.

        :param response: Collection of Atlas Entities
        :param enhance_metadata: Should Atlas be queried to acquire complete entity definitions (search might not
        return all available attributes)
        :return: List of Table objects
        """

        result = list()

        # if condition is satisfied then we query Atlas again to collect all available information regarding each table
        # along with relationship information. This is helpful when using Atlas DSL as returned entities contain minimal
        # amount of attributes.
        if enhance_metadata:
            ids = list()

            for hit in response:
                ids.append(hit.guid)

            entities = self._extract_entities(self.atlas.entity_bulk(guid=ids, ignoreRelationships=False))
        else:
            entities = response

        for entity in entities:
            entity_attrs = entity.attributes

            qn = parse_table_qualified_name(qualified_name=entity_attrs.get(self.ATLAS_QN_ATTRIBUTE))

            entity_name = qn.get('table_name') or entity_attrs.get('name')
            db_name = qn.get('db_name', '')
            db_cluster = qn.get('cluster_name', '')

            tags: List[Tag] = []

            for classification in entity.classificationNames or list():
                tags.append(Tag(tag_name=classification))

            badges: List[Tag] = tags

            table = Table(name=entity_name,
                          key=make_table_qualified_name(entity_name, db_cluster, db_name),
                          description=entity_attrs.get('description'),
                          cluster=db_cluster,
                          database=entity.typeName,
                          schema=db_name,
                          tags=tags,
                          badges=badges,
                          column_names=[],
                          last_updated_timestamp=entity_attrs.get('updateTime'))

            result.append(table)

        return result

    def _atlas_basic_search(self, query_params: Dict) -> Tuple[List[Table], int]:
        """
        Conduct search using Atlas Basic Search API.

        :param query_params: A dictionary of query parameters needed to be pass to Basic Search Post method of Atlas
        :return: List of Table objects and approximate count of entities matching in Atlas
        """

        try:
            # Fetch the table entities based on query terms
            search_results = self.atlas.search_basic.create(data=query_params)
        except BadRequest as ex:
            LOGGER.error(f"Fetching Tables Failed : {str(ex)}")
            return [], 0

        if not len(search_results.entities):
            return [], 0

        # noinspection PyProtectedMember
        results_count = search_results._data.get("approximateCount")

        results = self._prepare_tables(search_results.entities, enhance_metadata=False)

        return results, results_count

    def _prepare_basic_search_query(self, limit: int, page_index: int, query_term: Optional[str] = None,
                                    filters: Optional[List[Tuple[str, str, str]]] = None,
                                    operator: Optional[str] = None,
                                    classifications: Optional[List[str]] = None,
                                    entity_type: str = None) -> Dict[str, Any]:
        """
        Render a query for Atlas Basic Search API.

        :param query_term: Search Query Term
        :param limit:
        :param page_index:
        :param fitlers: Optional list of tuples (field, condition, value) that will translate into entityFilters for
        narrowing down search results
        :param operator:
        :param entity_type: Which kind of entity this query will look for
        :return: Dictionary object prepared for Atlas client basic_search
        """
        if not entity_type:
            entity_type = self.ATLAS_TABLE_ENTITY

        query: Dict[str, Any] = {'typeName': entity_type,
                                 'excludeDeletedEntities': True,
                                 'includeSubTypes': True,
                                 'limit': limit,
                                 'offset': page_index * self.page_size,
                                 'sortBy': 'popularityScore',
                                 'sortOrder': 'DESCENDING'}

        if query_term:
            query_term = f'*{query_term}*'
            query_term = sub('\\*+', '*', query_term)

            query['query'] = query_term

        # filters and query_term shouldn't be mixed
        if filters and not query_term:
            condition = operator or 'AND'
            criterion: List[Dict[str, str]] = list()

            for _query_filter in filters:
                attribute_name, operator, attribute_value = _query_filter

                # filters perform much better when wildcard is dot, not star
                attribute_value = sub('\\*', '.', attribute_value)
                query_filter = {'attributeName': attribute_name,
                                'operator': operator.upper(),
                                'attributeValue': attribute_value}

                criterion.append(query_filter)

            if len(criterion) > 1:
                query['entityFilters'] = {'condition': condition, 'criterion': criterion}
            elif len(criterion) == 1:
                query['entityFilters'] = criterion[0]
        elif classifications:
            query['classification'] = classifications

        return query

    @timer_with_counter
    def fetch_table_search_results(self, *,
                                   query_term: str,
                                   page_index: int = 0,
                                   index: str = '') -> SearchResult:
        """
        Conduct a 'Basic Search' in Amundsen UI.

        Atlas Basic Search API is used for that operation. We search on `qualifiedName` field as
        (following Atlas documentation) any 'Referencable' entity 'can be searched for using a unique attribute called
        qualifiedName'. It provides best performance, simplicity and sorting by popularityScore.

        :param query_term: Search Query Term
        :param page_index: Index of search page user is currently on (for pagination)
        :param index: Search Index (different resource corresponding to different index)
        :return: SearchResult Object
        """
        if not query_term:
            # return empty result for blank query term
            return SearchResult(total_results=0, results=[])

        # @todo switch to search with 'query' not 'filters' once Atlas FreeTextSearchProcessor is fixed
        # https://reviews.apache.org/r/72440/
        filters = [(self.ATLAS_QN_ATTRIBUTE, 'CONTAINS', query_term)]

        # conduct search using filter on qualifiedName (it already contains both dbName and tableName)
        # and table description
        query_params = self._prepare_basic_search_query(self.page_size, page_index, filters=filters, operator='OR')

        tables, approx_count = self._atlas_basic_search(query_params)

        return SearchResult(total_results=approx_count, results=tables)

    @timer_with_counter
    def fetch_table_search_results_with_field(self, *,
                                              query_term: str,
                                              field_name: str,
                                              field_value: str,
                                              page_index: int = 0,
                                              index: str = '') -> SearchResult:
        """
        DEPRECATED

        Query Atlas and return results as list of Table objects.
        Per field name we have a count query and a query for the tables.
        https://atlas.apache.org/Search-Advanced.html

        :param query_term: search query term
        :param field_name: field name to do the searching(e.g schema, tag_names)
        :param field_value: value for the field for filtering
        :param page_index: index of search page user is currently on
        :param index: search index (different resource corresponding to different index
        :return: SearchResult Object
        :return:
        """
        warnings.warn('Function deprecated, please use "Advanced Search" with "fetch_table_search_results_with_filter"',
                      DeprecationWarning)

        # @todo maybe we're ready to delete this function completely ?
        class EntityStatus:
            ACTIVE = 'ACTIVE'

        tables: List[Table] = []
        if field_name in ['tag', 'table']:
            query_params = {'typeName': 'Table',
                            'excludeDeletedEntities': True,
                            'limit': self.page_size,
                            'offset': page_index * self.page_size,
                            'attributes': ['description', 'comment']}
            if field_name == 'tag':
                query_params.update({'classification': field_value})
            else:
                query_params.update({'query': field_value})
            tables, count_value = self._atlas_basic_search(query_params)
        else:
            # Need to use DSL for the advanced relationship operations
            sql = f"Table from Table where false"
            count_sql = f"{sql} select count()"

            if field_name == 'schema':
                sql = f"from Table where  __state = '{EntityStatus.ACTIVE}' and db.name like '{field_value}'"
                count_sql = f"{sql} select count()"
            elif field_name == 'column':
                sql = f"hive_column where  __state = '{EntityStatus.ACTIVE}' and" \
                      f" name like '{field_value}' select table"
                # TODO nanne: count tables instead of columns
                count_sql = f"hive_column where  __state = '{EntityStatus.ACTIVE}' " \
                            f"and name like '{field_value}' select count()"

            LOGGER.debug(f"Used following sql query: {sql}")
            count_value = 0
            try:
                # count results
                count_params = {'query': count_sql}
                count_results = list(self.atlas.search_dsl(**count_params))[0]
                count_value = count_results._data['attributes']['values'][0][0]

                params = {'query': f"{sql} limit {self.page_size} offset {page_index * self.page_size}"}
                search_results = self.atlas.search_dsl(**params)
                if count_value > 0 and page_index * self.page_size <= count_value:
                    # unpack all collections (usually just one collection though)
                    for collection in search_results:
                        if hasattr(collection, 'entities'):
                            tables.extend(self._prepare_tables(collection.entities, enhance_metadata=True))
            except BadRequest:
                LOGGER.error("Atlas Search DSL error with the following query:", sql)
        return SearchResult(total_results=count_value, results=tables)

    def fetch_table_search_results_with_filter(self, *,
                                               query_term: str,
                                               search_request: dict,
                                               page_index: int = 0,
                                               index: str = '') -> SearchResult:
        """
        Conduct an 'Advanced Search' to narrow down search results with a use of filters.

        Using Atlas Basic Search with filters to retrieve precise results and sort them by popularity score.


        :param query_term: A Search Query Term
        :param search_request: Values from Filters
        :param page_index: Index of search page user is currently on (for pagination)
        :param index: Search Index (different resource corresponding to different index)
        :return: SearchResult Object
        """
        _filters = search_request.get('filters', dict())

        db_filter_value = _filters.get('database')
        table_filter_value = _filters.get('table')
        cluster_filter_value = _filters.get('cluster')
        badges_filter_value = _filters.get('badges', list())
        tags_filter_value = _filters.get('tag', list())

        filters = list()

        # qualifiedName follows pattern ${db}.${table}@${cluster}
        if db_filter_value:
            filters.append((self.ATLAS_QN_ATTRIBUTE, 'STARTSWITH', db_filter_value[0] + '.'))

        if cluster_filter_value:
            filters.append((self.ATLAS_QN_ATTRIBUTE, 'ENDSWITH', '@' + cluster_filter_value[0]))

        if table_filter_value:
            filters.append(('name', 'CONTAINS', table_filter_value[0]))

        classifications: List[str] = list()  # noqa: E701

        if badges_filter_value or tags_filter_value:
            classifications = list(set(badges_filter_value + tags_filter_value))

        # Currently Atlas doesn't allow mixing search by filters and classifications
        if filters:
            query_params = self._prepare_basic_search_query(self.page_size, page_index,
                                                            filters=filters)
        elif classifications:
            query_params = self._prepare_basic_search_query(self.page_size, page_index,
                                                            classifications=classifications)

        tables, approx_count = self._atlas_basic_search(query_params)

        return SearchResult(total_results=approx_count, results=tables)

    def fetch_user_search_results(self, *,
                                  query_term: str,
                                  page_index: int = 0,
                                  index: str = '') -> SearchResult:
        pass

    def update_document(self, *, data: List[Dict[str, Any]], index: str = '') -> str:
        raise NotImplementedError()

    def create_document(self, *, data: List[Dict[str, Any]], index: str = '') -> str:
        raise NotImplementedError()

    def delete_document(self, *, data: List[str], index: str = '') -> str:
        raise NotImplementedError()

    def fetch_dashboard_search_results(self, *, query_term: str, page_index: int = 0, index: str = '') -> SearchResult:
        pass
