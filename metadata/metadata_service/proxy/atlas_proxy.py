import logging
import re
from typing import Union, List, Dict, Any

from atlasclient.client import Atlas
from atlasclient.exceptions import BadRequest

from metadata_service.entity.popular_table import PopularTable
from metadata_service.entity.table_detail import Table
from metadata_service.entity.user_detail import User as UserEntity
from metadata_service.exception import NotFoundException
from metadata_service.proxy import BaseProxy
from metadata_service.util import UserResourceRel

LOGGER = logging.getLogger(__name__)


class AtlasProxy(BaseProxy):
    """
    Atlas Proxy client for the amundsen metadata
    """
    TABLE_ENTITY = 'Table'
    DATASET_ENTITY = 'DataSet'
    DB_KEY = 'db'
    NAME_KEY = 'qualifiedName'

    def __init__(self, *,
                 host: str,
                 port: int,
                 user: str = 'admin',
                 password: str = '') -> None:
        """
        Initiate the Apache Atlas client with the provided credentials
        """
        self._driver = Atlas(host=host, port=port, username=user, password=password)

    def _get_ids_from_basic_search(self, *, params: Dict) -> List[str]:
        """
        Search for the entities based on the params provided as argument.
        :param params: the dictionary of parameters to be used for the basic search
        :return: The flat list of GUIDs of entities founds based on the params.
        """
        ids = list()
        search_results = self._driver.search_basic(**params)
        for result in search_results:
            # result.entities would directly be accessible after below PR
            # Fix: https://github.com/jpoullet2000/atlasclient/pull/59
            # noinspection PyProtectedMember
            for entity in result._data.get('entities', list()):
                ids.append(entity['guid'])
        return ids

    def _extract_info_from_uri(self, *, table_uri: str) -> Dict:
        """
        Extracts the table information from table_uri coming from frontend.
        :param table_uri:
        :return: Dictionary object, containing following information:
        db: Database Name
        cluster: Cluster information
        schema: Schema Name
        name: Unique Table Identifier
        """
        pattern = re.compile(r"""
            ^   (?P<db>.*?)
            :\/\/
                (?P<cluster>.*)
            \.
                (?P<schema>.*?)
            \/
                (?P<name>.*?)
            $
        """, re.X)
        result = pattern.match(table_uri)
        return result.groupdict() if result else dict()

    def get_user_detail(self, *, user_id: str) -> Union[UserEntity, None]:
        pass

    def get_table(self, *, table_uri: str) -> Table:
        """
        Gathers all the information needed for the Table Detail Page.
        It tries to get the table information from
        :param table_uri:
        :return:
        """
        table_info = self._extract_info_from_uri(table_uri=table_uri)

        try:
            # The reason to use the DATASET_ENTITY here instead of TABLE_ENTITY
            # is to access the older data (if any) which was generated before
            # introducing the TABLE_ENTITY in atlas.
            entity = self._driver.entity_unique_attribute(
                self.DATASET_ENTITY,
                qualifiedName=table_info.get('name')).entity
        except Exception as ex:
            LOGGER.exception('Table not found. {}'.format(str(ex)))
            raise NotFoundException('Table URI( {table_uri} ) does not exist'.format(table_uri=table_uri))

        try:
            table = Table(database=table_info['db'],
                          cluster=table_info['cluster'],
                          schema=table_info['schema'],
                          name=table_info['name'],
                          columns=entity['relationshipAttributes']['columns'],
                          last_updated_timestamp=entity['updateTime'])

            return table
        except KeyError as ex:
            LOGGER.exception('Error while accessing table information. {}'.format(str(ex)))
            raise BadRequest('Some of the required attributes are missing in : ( {table_uri} )'.
                             format(table_uri=table_uri))

    def delete_owner(self, *, table_uri: str, owner: str) -> None:
        pass

    def add_owner(self, *, table_uri: str, owner: str) -> None:
        pass

    def get_table_description(self, *,
                              table_uri: str) -> Union[str, None]:
        pass

    def put_table_description(self, *,
                              table_uri: str,
                              description: str) -> None:
        pass

    def add_tag(self, *, table_uri: str, tag: str) -> None:
        pass

    def delete_tag(self, *, table_uri: str, tag: str) -> None:
        pass

    def put_column_description(self, *,
                               table_uri: str,
                               column_name: str,
                               description: str) -> None:
        pass

    def get_column_description(self, *,
                               table_uri: str,
                               column_name: str) -> Union[str, None]:
        pass

    def get_popular_tables(self, *,
                           num_entries: int = 10) -> List[PopularTable]:
        """
        FixMe: For now it simply returns ALL the tables available,
        Need to generate the formula for popular tables only.
        :param num_entries:
        :return:
        """
        popular_tables = list()
        params = {'typeName': self.TABLE_ENTITY, 'excludeDeletedEntities': True}
        guids = self._get_ids_from_basic_search(params=params)

        entity_collection = self._driver.entity_bulk(guid=guids)
        for _collection in entity_collection:
            for entity in _collection.entities:
                attrs = entity.attributes
                # At the moment, relationship attributes are not available in the entity
                # and hence, we need to make another request to get details of database
                # Fix: https://github.com/jpoullet2000/atlasclient/pull/60
                database = attrs.get(self.DB_KEY)
                if database:
                    db_attrs = self._driver.entity_guid(database['guid']).entity['attributes']
                    db_name = db_attrs.get(self.NAME_KEY)
                    db_cluster = db_attrs.get('cluster')
                else:
                    db_name = ''
                    db_cluster = ''

                popular_table = PopularTable(database=db_name,
                                             cluster=db_cluster,
                                             schema=attrs.get('schema'),
                                             name=attrs.get(self.NAME_KEY),
                                             description=attrs.get('description'))
                popular_tables.append(popular_table)
        return popular_tables

    def get_latest_updated_ts(self) -> int:
        pass

    def get_tags(self) -> List:
        pass

    def get_table_by_user_relation(self, *, user_email: str,
                                   relation_type: UserResourceRel) -> Dict[str, Any]:
        pass

    def add_table_relation_by_user(self, *,
                                   table_uri: str,
                                   user_email: str,
                                   relation_type: UserResourceRel) -> None:
        pass

    def delete_table_relation_by_user(self, *,
                                      table_uri: str,
                                      user_email: str,
                                      relation_type: UserResourceRel) -> None:
        pass
