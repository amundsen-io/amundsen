import logging
import re
from typing import Union, List, Dict, Any, Tuple

from atlasclient.client import Atlas
from atlasclient.exceptions import BadRequest
from atlasclient.models import EntityUniqueAttribute

from metadata_service.entity.tag_detail import TagDetail

from metadata_service.entity.popular_table import PopularTable
from metadata_service.entity.table_detail import Table, User, Tag
from metadata_service.entity.user_detail import User as UserEntity
from metadata_service.exception import NotFoundException
from metadata_service.proxy import BaseProxy
from metadata_service.util import UserResourceRel

LOGGER = logging.getLogger(__name__)


class AtlasProxy(BaseProxy):
    """
    Atlas Proxy client for the amundsen metadata
    {ATLAS_API_DOCS} = https://atlas.apache.org/api/v2/
    """
    TABLE_ENTITY = 'Table'
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
        entity: Type of entity example: rdbms_table, hive_table etc.
        cluster: Cluster information
        db: Database Name
        name: Unique Table Identifier
        """
        pattern = re.compile(r"""
            ^   (?P<entity>.*?)
            :\/\/
                (?P<cluster>.*)
            \.
                (?P<db>.*?)
            \/
                (?P<name>.*?)
            $
        """, re.X)
        result = pattern.match(table_uri)
        return result.groupdict() if result else dict()

    def _get_table_entity(self, *, table_uri: str) -> Tuple[EntityUniqueAttribute, Dict]:
        """
        Fetch information from table_uri and then find the appropriate entity
        The reason, we're not returning the entity_unique_attribute().entity
        directly is because the entity_unique_attribute() return entity Object
        that can be used for update purposes,
        while entity_unique_attribute().entity only returns the dictionary
        :param table_uri:
        :return:
        """
        table_info = self._extract_info_from_uri(table_uri=table_uri)

        try:
            return self._driver.entity_unique_attribute(
                table_info['entity'],
                qualifiedName=table_info.get('name')), table_info
        except Exception as ex:
            LOGGER.exception('Table not found. {}'.format(str(ex)))
            raise NotFoundException('Table URI( {table_uri} ) does not exist'
                                    .format(table_uri=table_uri))

    def get_user_detail(self, *, user_id: str) -> Union[UserEntity, None]:
        pass

    def get_table(self, *, table_uri: str) -> Table:
        """
        Gathers all the information needed for the Table Detail Page.
        :param table_uri:
        :return:
        """
        entity, table_info = self._get_table_entity(table_uri=table_uri)
        table_details = entity.entity

        try:
            attrs = table_details['attributes']
            rel_attrs = table_details['relationshipAttributes']

            tags = []
            for classification in table_details.get("classifications", list()):
                tags.append(
                    Tag(
                        tag_name=classification.get('typeName'),
                        tag_type="default"
                    )
                )

            table = Table(database=table_info['entity'],
                          cluster=table_info['cluster'],
                          schema=table_info['db'],
                          name=table_info['name'],
                          tags=tags,
                          description=attrs.get('description'),
                          owners=[User(email=attrs.get('owner'))],
                          columns=rel_attrs.get('columns'),
                          last_updated_timestamp=table_details.get('updateTime'))

            return table
        except KeyError as ex:
            LOGGER.exception('Error while accessing table information. {}'
                             .format(str(ex)))
            raise BadRequest('Some of the required attributes '
                             'are missing in : ( {table_uri} )'
                             .format(table_uri=table_uri))

    def delete_owner(self, *, table_uri: str, owner: str) -> None:
        pass

    def add_owner(self, *, table_uri: str, owner: str) -> None:
        """
        It simply replaces the owner field in atlas with the new string.
        FixMe (Verdan): Implement multiple data owners and
        atlas changes in the documentation if needed to make owner field a list
        :param table_uri:
        :param owner: Email address of the owner
        :return: None, as it simply adds the owner.
        """
        entity, _ = self._get_table_entity(table_uri=table_uri)
        entity.entity['attributes']['owner'] = owner
        entity.update()

    def get_table_description(self, *,
                              table_uri: str) -> Union[str, None]:
        """
        :param table_uri:
        :return: The description of the table as a string
        """
        entity, _ = self._get_table_entity(table_uri=table_uri)
        return entity.entity['attributes']['description']

    def put_table_description(self, *,
                              table_uri: str,
                              description: str) -> None:
        """
        Update the description of the given table.
        :param table_uri:
        :param description: Description string
        :return: None
        """
        entity, _ = self._get_table_entity(table_uri=table_uri)
        entity.entity['attributes']['description'] = description
        entity.update()

    def add_tag(self, *, table_uri: str, tag: str) -> None:
        """
        Assign the tag/classification to the give table
        API Ref: /resource_EntityREST.html#resource_EntityREST_addClassification_POST
        :param table_uri:
        :param tag: Tag/Classfification Name
        :return: None
        """
        entity, _ = self._get_table_entity(table_uri=table_uri)
        entity_bulk_tag = {"classification": {"typeName": tag},
                           "entityGuids": [entity.entity['guid']]}
        self._driver.entity_bulk_classification.create(data=entity_bulk_tag)

    def delete_tag(self, *, table_uri: str, tag: str) -> None:
        """
        Delete the assigned classfication/tag from the given table
        API Ref: /resource_EntityREST.html#resource_EntityREST_deleteClassification_DELETE
        :param table_uri:
        :param tag:
        :return:
        """
        try:
            entity, _ = self._get_table_entity(table_uri=table_uri)
            guid_entity = self._driver.entity_guid(entity.entity['guid'])
            guid_entity.classifications(tag).delete()
        except Exception as ex:
            LOGGER.exception('For some reason this deletes the classification '
                             'but also always return exception. {}'.format(str(ex)))

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
                    db_entity = self._driver.entity_guid(database['guid'])
                    db_attrs = db_entity.entity['attributes']
                    db_name = db_attrs.get(self.NAME_KEY)
                    db_cluster = db_attrs.get('clusterName')
                else:
                    db_name = ''
                    db_cluster = ''

                popular_table = PopularTable(database=entity.typeName,
                                             cluster=db_cluster,
                                             schema=db_name,
                                             name=attrs.get(self.NAME_KEY),
                                             description=attrs.get('description'))
                popular_tables.append(popular_table)
        return popular_tables

    def get_latest_updated_ts(self) -> int:
        pass

    def get_tags(self) -> List:
        """
        Fetch all the classification entity definitions from atlas  as this
        will be used to generate the autocomplete on the table detail page
        :return: A list of TagDetail Objects
        """
        tags = []
        for type_def in self._driver.typedefs:
            for classification in type_def.classificationDefs:
                tags.append(
                    TagDetail(
                        tag_name=classification.name,
                        tag_count=0     # FixMe (Verdan): Implement the tag count
                    )
                )
        return tags

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
