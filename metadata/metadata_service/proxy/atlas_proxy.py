# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import re
from operator import attrgetter
from random import randint
from typing import Any, Dict, List, Union, Optional, Tuple

from amundsen_common.models.dashboard import DashboardSummary
from amundsen_common.models.popular_table import PopularTable
from amundsen_common.models.table import Column, Stat, Table, Tag, User, Reader, \
    ProgrammaticDescription, ResourceReport, Watermark
from amundsen_common.models.user import User as UserEntity
from atlasclient.client import Atlas
from atlasclient.exceptions import BadRequest, Conflict, NotFound
from atlasclient.models import EntityUniqueAttribute
from atlasclient.utils import (make_table_qualified_name,
                               parse_table_qualified_name,
                               extract_entities)
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from flask import current_app as app

from metadata_service.entity.dashboard_detail import DashboardDetail as DashboardDetailEntity
from metadata_service.entity.description import Description
from metadata_service.entity.resource_type import ResourceType
from metadata_service.entity.tag_detail import TagDetail
from metadata_service.exception import NotFoundException
from metadata_service.proxy import BaseProxy
from metadata_service.util import UserResourceRel

LOGGER = logging.getLogger(__name__)

# Expire cache every 11 hours + jitter
_ATLAS_PROXY_CACHE_EXPIRY_SEC = 11 * 60 * 60 + randint(0, 3600)


class Status:
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


# noinspection PyMethodMayBeStatic
class AtlasProxy(BaseProxy):
    """
    Atlas Proxy client for the amundsen metadata
    {ATLAS_API_DOCS} = https://atlas.apache.org/api/v2/
    """
    TABLE_ENTITY = app.config['ATLAS_TABLE_ENTITY']
    DB_ATTRIBUTE = app.config['ATLAS_DB_ATTRIBUTE']
    STATISTICS_FORMAT_SPEC = app.config['STATISTICS_FORMAT_SPEC']
    BOOKMARK_TYPE = 'Bookmark'
    USER_TYPE = 'User'
    READER_TYPE = 'Reader'
    QN_KEY = 'qualifiedName'
    BOOKMARK_ACTIVE_KEY = 'active'
    GUID_KEY = 'guid'
    ATTRS_KEY = 'attributes'
    REL_ATTRS_KEY = 'relationshipAttributes'
    ENTITY_URI_KEY = 'entityUri'
    _CACHE = CacheManager(**parse_cache_config_options({'cache.regions': 'atlas_proxy',
                                                        'cache.atlas_proxy.type': 'memory',
                                                        'cache.atlas_proxy.expire': _ATLAS_PROXY_CACHE_EXPIRY_SEC}))

    def __init__(self, *,
                 host: str,
                 port: int,
                 user: str = 'admin',
                 password: str = '',
                 encrypted: bool = False,
                 validate_ssl: bool = False,
                 client_kwargs: dict = dict()) -> None:
        """
        Initiate the Apache Atlas client with the provided credentials
        """
        protocol = 'https' if encrypted else 'http'
        self._driver = Atlas(host=host,
                             port=port,
                             username=user,
                             password=password,
                             protocol=protocol,
                             validate_ssl=validate_ssl,
                             **client_kwargs)

    def _get_ids_from_basic_search(self, *, params: Dict) -> List[str]:
        """
        FixMe (Verdan): UNUSED. Please remove after implementing atlas proxy
        Search for the entities based on the params provided as argument.
        :param params: the dictionary of parameters to be used for the basic search
        :return: The flat list of GUIDs of entities founds based on the params.
        """
        ids = list()
        search_results = self._driver.search_basic(**params)
        for result in search_results:
            for entity in result.entities:
                ids.append(entity.guid)
        return ids

    def _get_flat_values_from_dsl(self, dsl_param: dict) -> List:
        """
        Makes a DSL query asking for specific attribute, extracts that attribute
        from result (which is a list of list, and converts that into a flat list.
        :param dsl_param: A DSL parameter, with SELECT clause
        :return: A Flat list of specified attributes in SELECT clause
        """
        attributes: List = list()
        _search_collection = self._driver.search_dsl(**dsl_param)
        for collection in _search_collection:
            attributes = collection.flatten_attrs()
        return attributes

    def _extract_info_from_uri(self, *, table_uri: str) -> Dict:
        """
        Extracts the table information from table_uri coming from frontend.
        :param table_uri:
        :return: Dictionary object, containing following information:
        entity: Type of entity example: rdbms_table, hive_table etc.
        cluster: Cluster information
        db: Database Name
        name: Table Name
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

    def _parse_reader_qn(self, reader_qn: str) -> Dict:
        """
        Parse reader qualifiedName and extract the info
        :param reader_qn:
        :return: Dictionary object containing following information:
        cluster: cluster information
        db: Database name
        name: Table name
        """
        pattern = re.compile(r"""
        ^(?P<db>[^.]*)
        \.
        (?P<table>[^.]*)
        \.
        (?P<user_id>[^.]*)\.reader
        \@
        (?P<cluster>.*)
        $
        """, re.X)
        result = pattern.match(reader_qn)
        return result.groupdict() if result else dict()

    def _parse_bookmark_qn(self, bookmark_qn: str) -> Dict:
        """
        Parse bookmark qualifiedName and extract the info
        :param bookmark_qn: Qualified Name of Bookmark entity
        :return: Dictionary object containing following information:
        cluster: cluster information
        db: Database name
        name: Table name
        """
        pattern = re.compile(r"""
        ^(?P<db>[^.]*)
        \.
        (?P<table>[^.]*)
        \.
        (?P<entity_type>[^.]*)
        \.
        (?P<user_id>[^.]*)\.bookmark
        \@
        (?P<cluster>.*)
        $
        """, re.X)
        result = pattern.match(bookmark_qn)
        return result.groupdict() if result else dict()

    def _get_user_details(self, user_id: str) -> Dict:
        """
        Helper function to help get the user details if the `USER_DETAIL_METHOD` is configured,
        else uses the user_id for both email and user_id properties.
        :param user_id: The Unique user id of a user entity
        :return: a dictionary of user details
        """
        if app.config.get('USER_DETAIL_METHOD'):
            user_details = app.config.get('USER_DETAIL_METHOD')(user_id)  # type: ignore
        else:
            user_details = {'email': user_id, 'user_id': user_id}

        return user_details

    def _get_table_entity(self, *, table_uri: str) -> EntityUniqueAttribute:
        """
        Fetch information from table_uri and then find the appropriate entity
        The reason, we're not returning the entity_unique_attribute().entity
        directly is because the entity_unique_attribute() return entity Object
        that can be used for update purposes,
        while entity_unique_attribute().entity only returns the dictionary
        :param table_uri:
        :return: A tuple of Table entity and parsed information of table qualified name
        """
        table_info = self._extract_info_from_uri(table_uri=table_uri)
        table_qn = make_table_qualified_name(table_info.get('name'),
                                             table_info.get('cluster'),
                                             table_info.get('db')
                                             )

        try:
            return self._driver.entity_unique_attribute(table_info['entity'], qualifiedName=table_qn)
        except Exception as ex:
            LOGGER.exception(f'Table not found. {str(ex)}')
            raise NotFoundException('Table URI( {table_uri} ) does not exist'
                                    .format(table_uri=table_uri))

    def _get_user_entity(self, user_id: str) -> EntityUniqueAttribute:
        """
        Fetches an user entity from an id
        :param user_id:
        :return:
        """
        try:
            return self._driver.entity_unique_attribute("User",
                                                        qualifiedName=user_id)
        except Exception as ex:
            raise NotFoundException('(User {user_id}) does not exist'
                                    .format(user_id=user_id))

    def _create_bookmark(self, entity: EntityUniqueAttribute, user_guid: str, bookmark_qn: str,
                         table_uri: str) -> None:
        """
        Creates a bookmark entity for a specific user and table uri.
        :param user_guid: User's guid
        :param bookmark_qn: Bookmark qualifiedName
        :return:
        """

        bookmark_entity = {
            'entity': {
                'typeName': self.BOOKMARK_TYPE,
                'attributes': {'qualifiedName': bookmark_qn,
                               self.BOOKMARK_ACTIVE_KEY: True,
                               'entityUri': table_uri,
                               'user': {'guid': user_guid},
                               'entity': {'guid': entity.entity[self.GUID_KEY]}}
            }
        }

        self._driver.entity_post.create(data=bookmark_entity)

    def _get_bookmark_entity(self, entity_uri: str, user_id: str) -> EntityUniqueAttribute:
        """
        Fetch a Bookmark entity from parsing table uri and user id.
        If Bookmark is not present, create one for the user.
        :param table_uri:
        :param user_id: Qualified Name of a user
        :return:
        """
        table_info = self._extract_info_from_uri(table_uri=entity_uri)
        bookmark_qn = '{}.{}.{}.{}.bookmark@{}'.format(table_info.get('db'),
                                                       table_info.get('name'),
                                                       table_info.get('entity'),
                                                       user_id,
                                                       table_info.get('cluster'))

        try:
            bookmark_entity = self._driver.entity_unique_attribute(self.BOOKMARK_TYPE, qualifiedName=bookmark_qn)

            if not bookmark_entity.entity:
                table_entity = self._get_table_entity(table_uri=entity_uri)
                # Fetch user entity from user_id for relation
                user_entity = self._get_user_entity(user_id)
                # Create bookmark entity with the user relation.
                self._create_bookmark(table_entity,
                                      user_entity.entity[self.GUID_KEY], bookmark_qn, entity_uri)
                # Fetch bookmark entity after creating it.
                bookmark_entity = self._driver.entity_unique_attribute(self.BOOKMARK_TYPE, qualifiedName=bookmark_qn)

            return bookmark_entity

        except Exception as ex:
            LOGGER.exception(f'Bookmark not found. {str(ex)}')
            raise NotFoundException('Bookmark( {bookmark_qn} ) does not exist'
                                    .format(bookmark_qn=bookmark_qn))

    def _get_column(self, *, table_uri: str, column_name: str) -> Dict:
        """
        Fetch the column information from referredEntities of the table entity
        :param table_uri:
        :param column_name:
        :return: A dictionary containing the column details
        """
        try:
            table_entity = self._get_table_entity(table_uri=table_uri)
            columns = table_entity.entity[self.REL_ATTRS_KEY].get('columns')
            for column in columns or list():
                col_details = table_entity.referredEntities[column[self.GUID_KEY]]
                if column_name == col_details[self.ATTRS_KEY]['name']:
                    return col_details

            raise NotFoundException(f'Column not found: {column_name}')

        except KeyError as ex:
            LOGGER.exception(f'Column not found: {str(ex)}')
            raise NotFoundException(f'Column not found: {column_name}')

    def _serialize_columns(self, *, entity: EntityUniqueAttribute) -> \
            Union[List[Column], List]:
        """
        Helper function to fetch the columns from entity and serialize them
        using Column and Stat model.
        :param entity: EntityUniqueAttribute object,
        along with relationshipAttributes
        :return: A list of Column objects, if there are any columns available,
        else an empty list.
        """
        columns = list()
        for column in entity.entity[self.REL_ATTRS_KEY].get('columns') or list():
            column_status = column.get('entityStatus', 'inactive').lower()

            if column_status != 'active':
                continue

            col_entity = entity.referredEntities[column[self.GUID_KEY]]
            col_attrs = col_entity[self.ATTRS_KEY]
            statistics = list()

            for stats in col_attrs.get('statistics') or list():
                stats_attrs = stats['attributes']

                stat_type = stats_attrs.get('stat_name')

                stat_format = self.STATISTICS_FORMAT_SPEC.get(stat_type, dict())

                if not stat_format.get('drop', False):
                    stat_type = stat_format.get('new_name', stat_type)

                    stat_val = stats_attrs.get('stat_val')

                    format_val = stat_format.get('format')

                    if format_val:
                        stat_val = format_val.format(stat_val)
                    else:
                        stat_val = str(stat_val)

                    start_epoch = stats_attrs.get('start_epoch')
                    end_epoch = stats_attrs.get('end_epoch')

                    statistics.append(
                        Stat(
                            stat_type=stat_type,
                            stat_val=stat_val,
                            start_epoch=start_epoch,
                            end_epoch=end_epoch,
                        )
                    )

            columns.append(
                Column(
                    name=col_attrs.get('name'),
                    description=col_attrs.get('description') or col_attrs.get('comment'),
                    col_type=col_attrs.get('type') or col_attrs.get('dataType') or col_attrs.get('data_type'),
                    sort_order=col_attrs.get('position') or 9999,
                    stats=statistics,
                )
            )
        return sorted(columns, key=lambda item: item.sort_order)

    def _get_reports(self, guids: List[str]) -> List[ResourceReport]:
        reports = []
        if guids:
            report_entities_collection = self._driver.entity_bulk(guid=guids)
            for report_entity in extract_entities(report_entities_collection):
                try:
                    if report_entity.status == Status.ACTIVE:
                        report_attrs = report_entity.attributes
                        reports.append(
                            ResourceReport(
                                name=report_attrs['name'],
                                url=report_attrs['url']
                            )
                        )
                except (KeyError, AttributeError) as ex:
                    LOGGER.exception('Error while accessing table report: {}. {}'
                                     .format(str(report_entity), str(ex)))

        parsed_reports = app.config['RESOURCE_REPORT_CLIENT'](reports) \
            if app.config['RESOURCE_REPORT_CLIENT'] else reports

        return parsed_reports

    def _get_owners(self, data_owners: list, fallback_owner: str = None) -> List[User]:
        owners_detail = list()
        active_owners_list = list()
        active_owners = filter(lambda item:
                               item['entityStatus'] == Status.ACTIVE and
                               item['relationshipStatus'] == Status.ACTIVE,
                               data_owners)

        for owner in active_owners:
            owner_qn = owner['displayText']
            owner_data = self._get_user_details(owner_qn)
            owners_detail.append(User(**owner_data))
            active_owners_list.append(owner_qn)

        # To avoid the duplication,
        # we are checking if the fallback is not in data_owners
        if fallback_owner and (fallback_owner not in active_owners_list):
            owners_detail.append(User(**self._get_user_details(fallback_owner)))

        return owners_detail

    def get_user(self, *, id: str) -> Union[UserEntity, None]:
        pass

    def get_users(self) -> List[UserEntity]:
        pass

    def get_table(self, *, table_uri: str) -> Table:
        """
        Gathers all the information needed for the Table Detail Page.
        :param table_uri:
        :return: A Table object with all the information available
        or gathered from different entities.
        """
        entity = self._get_table_entity(table_uri=table_uri)
        table_details = entity.entity

        try:
            attrs = table_details[self.ATTRS_KEY]

            programmatic_descriptions = self._get_programmatic_descriptions(attrs.get('parameters', dict()))

            table_qn = parse_table_qualified_name(
                qualified_name=attrs.get(self.QN_KEY)
            )

            tags = []
            # Using or in case, if the key 'classifications' is there with a None
            for classification in table_details.get('classifications') or list():
                tags.append(
                    Tag(
                        tag_name=classification.get('typeName'),
                        tag_type="default"
                    )
                )

            columns = self._serialize_columns(entity=entity)

            reports_guids = [report.get("guid") for report in attrs.get("reports") or list()]

            table_type = attrs.get('tableType') or 'table'
            is_view = 'view' in table_type.lower()

            readers = self._get_readers(table_details)

            table = Table(
                database=table_details.get('typeName'),
                cluster=table_qn.get('cluster_name', ''),
                schema=table_qn.get('db_name', ''),
                name=attrs.get('name') or table_qn.get("table_name", ''),
                tags=tags,
                description=attrs.get('description') or attrs.get('comment'),
                owners=self._get_owners(
                    table_details[self.REL_ATTRS_KEY].get('ownedBy', []), attrs.get('owner')),
                resource_reports=self._get_reports(guids=reports_guids),
                columns=columns,
                is_view=is_view,
                table_readers=readers,
                last_updated_timestamp=self._parse_date(table_details.get('updateTime')),
                programmatic_descriptions=programmatic_descriptions,
                watermarks=self._get_table_watermarks(table_details))

            return table
        except KeyError as ex:
            LOGGER.exception('Error while accessing table information. {}'
                             .format(str(ex)))
            raise BadRequest('Some of the required attributes '
                             'are missing in : ( {table_uri} )'
                             .format(table_uri=table_uri))

    @staticmethod
    def _validate_date(text_date: str, date_format: str) -> Tuple[Optional[datetime.datetime], Optional[str]]:
        try:
            return datetime.datetime.strptime(text_date, date_format), date_format
        except (ValueError, TypeError):
            return None, None

    @staticmethod
    def _select_watermark_format(partition_names: List[str]) -> Optional[str]:
        result = None

        for partition_name in partition_names:
            # Assume that all partitions for given table have the same date format. Only thing that needs to be done
            # is establishing which format out of the supported ones it is and then we validate every partition
            # against it.
            for df in app.config['WATERMARK_DATE_FORMATS']:
                _, result = AtlasProxy._validate_date(partition_name, df)

                if result:
                    LOGGER.debug('Established date format', extra=dict(date_format=result))
                    return result

        return result

    @staticmethod
    def _render_partition_key_name(entity: EntityUniqueAttribute) -> Optional[str]:
        _partition_keys = []

        for partition_key in entity.get('attributes', dict()).get('partitionKeys', []):
            partition_key_column_name = partition_key.get('displayName')

            if partition_key_column_name:
                _partition_keys.append(partition_key_column_name)

        partition_key = ' '.join(_partition_keys).strip()

        return partition_key

    def _get_table_watermarks(self, entity: EntityUniqueAttribute) -> List[Watermark]:
        partition_value_format = '%Y-%m-%d %H:%M:%S'

        _partitions = entity.get('relationshipAttributes', dict()).get('partitions', list())

        names = [_partition.get('displayText') for _partition in _partitions
                 if _partition.get('entityStatus') == Status.ACTIVE
                 and _partition.get('relationshipStatus') == Status.ACTIVE]

        if not names:
            return []

        partition_key = AtlasProxy._render_partition_key_name(entity)
        watermark_date_format = AtlasProxy._select_watermark_format(names)

        partitions = {}

        for _partition in _partitions:
            partition_name = _partition.get('displayText')
            if partition_name and watermark_date_format:
                partition_date, _ = AtlasProxy._validate_date(partition_name, watermark_date_format)

                if partition_date:
                    common_values = {'partition_value': datetime.datetime.strftime(partition_date,
                                                                                   partition_value_format),
                                     'create_time': 0,
                                     'partition_key': partition_key}

                    partitions[partition_date] = common_values

        if partitions:
            low_watermark_date = min(partitions.keys())
            high_watermark_date = max(partitions.keys())

            low_watermark = Watermark(watermark_type='low_watermark', **partitions.get(low_watermark_date))
            high_watermark = Watermark(watermark_type='high_watermark', **partitions.get(high_watermark_date))

            return [low_watermark, high_watermark]
        else:
            return []

    def delete_owner(self, *, table_uri: str, owner: str) -> None:
        """
        :param table_uri:
        :param owner:
        :return:
        """
        table = self._get_table_entity(table_uri=table_uri)
        table_entity = table.entity

        if table_entity[self.REL_ATTRS_KEY].get("ownedBy"):
            try:
                active_owners = filter(lambda item:
                                       item['relationshipStatus'] == Status.ACTIVE
                                       and item['displayText'] == owner,
                                       table_entity[self.REL_ATTRS_KEY]['ownedBy'])
                if list(active_owners):
                    self._driver.relationship_guid(next(active_owners)
                                                   .get('relationshipGuid')).delete()
                else:
                    raise BadRequest('You can not delete this owner.')
            except NotFound as ex:
                LOGGER.exception('Error while removing table data owner. {}'
                                 .format(str(ex)))

    def add_owner(self, *, table_uri: str, owner: str) -> None:
        """
        Query on Atlas User entity to find if the entity exist for the
        owner string in parameter, if not create one. And then use that User
        entity's GUID and add a relationship between Table and User, on ownedBy field.
        :param table_uri:
        :param owner: Email address of the owner
        :return: None, as it simply adds the owner.
        """
        owner_info = self._get_user_details(owner)

        if not owner_info:
            raise NotFoundException(f'User "{owner}" does not exist.')

        user_dict = {
            "entity": {
                "typeName": "User",
                "attributes": {"qualifiedName": owner},
            }
        }

        # Get or Create a User
        user_entity = self._driver.entity_post.create(data=user_dict)
        user_guid = next(iter(user_entity.get("guidAssignments").values()))

        table = self._get_table_entity(table_uri=table_uri)

        entity_def = {
            "typeName": "DataSet_Users_Owner",
            "end1": {
                "guid": table.entity.get("guid"), "typeName": "Table",
            },
            "end2": {
                "guid": user_guid, "typeName": "User",
            },
        }
        try:
            self._driver.relationship.create(data=entity_def)
        except Conflict as ex:
            LOGGER.exception('Error while adding the owner information. {}'
                             .format(str(ex)))
            raise BadRequest(f'User {owner} is already added as a data owner for '
                             f'table {table_uri}.')

    def get_table_description(self, *,
                              table_uri: str) -> Union[str, None]:
        """
        :param table_uri:
        :return: The description of the table as a string
        """
        entity = self._get_table_entity(table_uri=table_uri)
        return entity.entity[self.ATTRS_KEY].get('description')

    def put_table_description(self, *,
                              table_uri: str,
                              description: str) -> None:
        """
        Update the description of the given table.
        :param table_uri:
        :param description: Description string
        :return: None
        """
        entity = self._get_table_entity(table_uri=table_uri)
        entity.entity[self.ATTRS_KEY]['description'] = description
        entity.update()

    def add_tag(self, *, id: str, tag: str, tag_type: str,
                resource_type: ResourceType = ResourceType.Table) -> None:
        """
        Assign the tag/classification to the give table
        API Ref: /resource_EntityREST.html#resource_EntityREST_addClassification_POST
        :param table_uri:
        :param tag: Tag/Classification Name
        :param tag_type
        :return: None
        """
        entity = self._get_table_entity(table_uri=id)
        entity_bulk_tag = {"classification": {"typeName": tag},
                           "entityGuids": [entity.entity[self.GUID_KEY]]}
        self._driver.entity_bulk_classification.create(data=entity_bulk_tag)

    def add_badge(self, *, id: str, badge_name: str, category: str = '',
                  resource_type: ResourceType) -> None:
        # Not implemented
        raise NotImplementedError

    def delete_tag(self, *, id: str, tag: str, tag_type: str,
                   resource_type: ResourceType = ResourceType.Table) -> None:
        """
        Delete the assigned classfication/tag from the given table
        API Ref: /resource_EntityREST.html#resource_EntityREST_deleteClassification_DELETE
        :param table_uri:
        :param tag:
        :return:
        """
        try:
            entity = self._get_table_entity(table_uri=id)
            guid_entity = self._driver.entity_guid(entity.entity[self.GUID_KEY])
            guid_entity.classifications(tag).delete()
        except Exception as ex:
            # FixMe (Verdan): Too broad exception. Please make it specific
            LOGGER.exception('For some reason this deletes the classification '
                             'but also always return exception. {}'.format(str(ex)))

    def delete_badge(self, *, id: str, badge_name: str, category: str,
                     resource_type: ResourceType) -> None:
        # Not implemented
        raise NotImplementedError

    def put_column_description(self, *,
                               table_uri: str,
                               column_name: str,
                               description: str) -> None:
        """
        :param table_uri:
        :param column_name: Name of the column to update the description
        :param description: The description string
        :return: None, as it simply updates the description of a column
        """
        column_detail = self._get_column(
            table_uri=table_uri,
            column_name=column_name)
        col_guid = column_detail[self.GUID_KEY]

        entity = self._driver.entity_guid(col_guid)
        entity.entity[self.ATTRS_KEY]['description'] = description
        entity.update(attribute='description')

    def get_column_description(self, *,
                               table_uri: str,
                               column_name: str) -> Union[str, None]:
        """
        :param table_uri:
        :param column_name:
        :return: The column description using the referredEntities
        information of a table entity
        """
        column_detail = self._get_column(
            table_uri=table_uri,
            column_name=column_name)
        return column_detail[self.ATTRS_KEY].get('description')

    def _serialize_popular_tables(self, entities: list) -> List[PopularTable]:
        """
        Gets a list of entities and serialize the popular tables.
        :param entities: List of entities from atlas client
        :return: a list of PopularTable objects
        """
        popular_tables = list()
        for table in entities:
            table_attrs = table.attributes

            table_qn = parse_table_qualified_name(
                qualified_name=table_attrs.get(self.QN_KEY)
            )

            table_name = table_qn.get("table_name") or table_attrs.get('name')
            db_name = table_qn.get("db_name", '')
            db_cluster = table_qn.get("cluster_name", '')

            popular_table = PopularTable(
                database=table.typeName,
                cluster=db_cluster,
                schema=db_name,
                name=table_name,
                description=table_attrs.get('description') or table_attrs.get('comment'))
            popular_tables.append(popular_table)

        return popular_tables

    def get_popular_tables(self, *,
                           num_entries: int,
                           user_id: Optional[str] = None) -> List[PopularTable]:
        """
        Generates a list of Popular tables to be shown on the home page of Amundsen.
        :param num_entries: Number of popular tables to fetch
        :return: A List of popular tables instances
        """
        popular_query_params = {'typeName': 'Table',
                                'sortBy': 'popularityScore',
                                'sortOrder': 'DESCENDING',
                                'excludeDeletedEntities': True,
                                'limit': num_entries}
        search_results = self._driver.search_basic.create(data=popular_query_params)
        return self._serialize_popular_tables(search_results.entities)

    def get_latest_updated_ts(self) -> int:
        date = None

        for metrics in self._driver.admin_metrics:
            try:
                date = self._parse_date(metrics.general.get('stats', {}).get('Notification:lastMessageProcessedTime'))
            except AttributeError:
                pass

        date = date or 0

        return date

    def get_tags(self) -> List:
        """
        Fetch all the classification entity definitions from atlas  as this
        will be used to generate the autocomplete on the table detail page
        :return: A list of TagDetail Objects
        """
        tags = []
        for metrics in self._driver.admin_metrics:
            tag_stats = metrics.tag
            for tag, count in tag_stats["tagEntities"].items():
                tags.append(
                    TagDetail(
                        tag_name=tag,
                        tag_count=count
                    )
                )
        return tags

    def get_badges(self) -> List:
        # Not implemented
        return []

    def _get_resources_followed_by_user(self, user_id: str, resource_type: str) \
            -> List[Union[PopularTable, DashboardSummary]]:
        """
        ToDo (Verdan): Dashboard still needs to be implemented.
        Helper function to get the resource, table, dashboard etc followed by a user.
        :param user_id: User ID of a user
        :param resource_type: Type of a resource that returns, could be table, dashboard etc.
        :return: A list of PopularTable, DashboardSummary or any other resource.
        """
        params = {
            'typeName': self.BOOKMARK_TYPE,
            'offset': '0',
            'limit': '1000',
            'excludeDeletedEntities': True,
            'entityFilters': {
                'condition': 'AND',
                'criterion': [
                    {
                        'attributeName': self.QN_KEY,
                        'operator': 'contains',
                        'attributeValue': f'.{user_id}.bookmark'
                    },
                    {
                        'attributeName': self.BOOKMARK_ACTIVE_KEY,
                        'operator': 'eq',
                        'attributeValue': 'true'
                    }
                ]
            },
            'attributes': ['count', self.QN_KEY, self.ENTITY_URI_KEY]
        }
        # Fetches the bookmark entities based on filters
        search_results = self._driver.search_basic.create(data=params)

        resources = []
        for record in search_results.entities:
            table_info = self._extract_info_from_uri(table_uri=record.attributes[self.ENTITY_URI_KEY])
            res = self._parse_bookmark_qn(record.attributes[self.QN_KEY])
            resources.append(PopularTable(
                database=table_info['entity'],
                cluster=res['cluster'],
                schema=res['db'],
                name=res['table']))
        return resources

    def _get_resources_owned_by_user(self, user_id: str, resource_type: str) \
            -> List[Union[PopularTable, DashboardSummary, Any]]:
        """
        ToDo (Verdan): Dashboard still needs to be implemented.
        Helper function to get the resource, table, dashboard etc owned by a user.
        :param user_id: User ID of a user
        :param resource_type: Type of a resource that returns, could be table, dashboard etc.
        :return: A list of PopularTable, DashboardSummary or any other resource.
        """
        resources = list()
        if resource_type == ResourceType.Table.name:
            type_regex = "(.*)_table$"
        # elif resource_type == ResourceType.Dashboard.name:
        #     type_regex = "Dashboard"
        else:
            LOGGER.exception(f'Resource Type ({resource_type}) is not yet implemented')
            raise NotImplemented

        user_entity = self._driver.entity_unique_attribute(self.USER_TYPE, qualifiedName=user_id).entity

        if not user_entity:
            LOGGER.exception(f'User ({user_id}) not found in Atlas')
            raise NotFoundException(f'User {user_id} not found.')

        resource_guids = set()
        for item in user_entity[self.REL_ATTRS_KEY].get('owns') or list():
            if (item['entityStatus'] == Status.ACTIVE and
                    item['relationshipStatus'] == Status.ACTIVE and
                    re.compile(type_regex).match(item['typeName'])):
                resource_guids.add(item[self.GUID_KEY])

        params = {
            'typeName': self.TABLE_ENTITY,
            'excludeDeletedEntities': True,
            'entityFilters': {
                'condition': 'AND',
                'criterion': [
                    {
                        'attributeName': 'owner',
                        'operator': 'startsWith',
                        'attributeValue': user_id.lower()
                    }
                ]
            },
            'attributes': [self.GUID_KEY]
        }
        table_entities = self._driver.search_basic.create(data=params)
        for table in table_entities.entities:
            resource_guids.add(table.guid)

        if resource_guids:
            entities = extract_entities(self._driver.entity_bulk(guid=list(resource_guids), ignoreRelationships=True))
            if resource_type == ResourceType.Table.name:
                resources = self._serialize_popular_tables(entities)
        else:
            LOGGER.info(f'User ({user_id}) does not own any "{resource_type}"')

        return resources

    def get_dashboard_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) \
            -> Dict[str, List[DashboardSummary]]:
        pass

    def get_table_by_user_relation(self, *, user_email: str, relation_type: UserResourceRel) -> Dict[str, Any]:
        tables = list()
        if relation_type == UserResourceRel.follow:
            tables = self._get_resources_followed_by_user(user_id=user_email,
                                                          resource_type=ResourceType.Table.name)
        elif relation_type == UserResourceRel.own:
            tables = self._get_resources_owned_by_user(user_id=user_email,
                                                       resource_type=ResourceType.Table.name)

        return {'table': tables}

    def get_frequently_used_tables(self, *, user_email: str) -> Dict[str, List[PopularTable]]:
        user = self._driver.entity_unique_attribute(self.USER_TYPE, qualifiedName=user_email).entity

        readers_guids = []
        for user_reads in user['relationshipAttributes'].get('entityReads'):
            entity_status = user_reads['entityStatus']
            relationship_status = user_reads['relationshipStatus']

            if entity_status == Status.ACTIVE and relationship_status == Status.ACTIVE:
                readers_guids.append(user_reads['guid'])

        readers = extract_entities(self._driver.entity_bulk(guid=readers_guids, ignoreRelationships=True))

        _results = {}
        for reader in readers:
            entity_uri = reader.attributes.get(self.ENTITY_URI_KEY)
            count = reader.attributes.get('count')

            if count:
                details = self._extract_info_from_uri(table_uri=entity_uri)

                _results[count] = dict(cluster=details.get('cluster'),
                                       name=details.get('name'),
                                       schema=details.get('db'),
                                       database=details.get('entity'))

        sorted_counts = sorted(_results.keys())

        results = []
        for count in sorted_counts:
            data: dict = _results.get(count, dict())
            table = PopularTable(**data)

            results.append(table)

        return {'table': results}

    def add_resource_relation_by_user(self, *,
                                      id: str,
                                      user_id: str,
                                      relation_type: UserResourceRel,
                                      resource_type: ResourceType) -> None:

        if resource_type is not ResourceType.Table:
            raise NotImplemented('resource type {} is not supported'.format(resource_type))

        entity = self._get_bookmark_entity(entity_uri=id, user_id=user_id)
        entity.entity[self.ATTRS_KEY][self.BOOKMARK_ACTIVE_KEY] = True
        entity.update()

    def delete_resource_relation_by_user(self, *,
                                         id: str,
                                         user_id: str,
                                         relation_type: UserResourceRel,
                                         resource_type: ResourceType) -> None:
        if resource_type is not ResourceType.Table:
            raise NotImplemented('resource type {} is not supported'.format(resource_type))

        entity = self._get_bookmark_entity(entity_uri=id, user_id=user_id)
        entity.entity[self.ATTRS_KEY][self.BOOKMARK_ACTIVE_KEY] = False
        entity.update()

    def _parse_date(self, date: int) -> Optional[int]:
        try:
            date_str = str(date)
            date_trimmed = date_str[:10]

            assert len(date_trimmed) == 10

            return int(date_trimmed)
        except Exception:
            return None

    def _get_readers(self, entity: EntityUniqueAttribute, top: Optional[int] = 15) -> List[Reader]:
        _readers = entity.get('relationshipAttributes', dict()).get('readers', list())

        guids = [_reader.get('guid') for _reader in _readers
                 if _reader.get('entityStatus', 'INACTIVE') == Status.ACTIVE
                 and _reader.get('relationshipStatus', 'INACTIVE') == Status.ACTIVE]

        if not guids:
            return []

        readers = extract_entities(self._driver.entity_bulk(guid=guids, ignoreRelationships=False))

        _result = []

        for _reader in readers:
            read_count = _reader.attributes['count']

            if read_count >= int(app.config['POPULAR_TABLE_MINIMUM_READER_COUNT']):
                reader_qn = _reader.relationshipAttributes['user']['displayText']
                reader_details = self._get_user_details(reader_qn)
                reader = Reader(user=User(**reader_details), read_count=read_count)

                _result.append(reader)

        result = sorted(_result, key=attrgetter('read_count'), reverse=True)[:top]

        return result

    def _get_programmatic_descriptions(self, parameters: dict) -> List[ProgrammaticDescription]:
        programmatic_descriptions: Dict[str, ProgrammaticDescription] = {}

        for source, text in parameters.items():
            use_parameter = True

            for regex_filter in app.config['PROGRAMMATIC_DESCRIPTIONS_EXCLUDE_FILTERS']:
                pattern = re.compile(regex_filter)

                if pattern.match(source):
                    use_parameter = False
                    break

            if use_parameter:
                source = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", source).lower()
                programmatic_descriptions[source] = ProgrammaticDescription(source=source, text=text)

        result = dict(sorted(programmatic_descriptions.items()))

        return list(result.values())

    def get_dashboard(self,
                      dashboard_uri: str,
                      ) -> DashboardDetailEntity:
        pass

    def get_dashboard_description(self, *,
                                  id: str) -> Description:
        pass

    def put_dashboard_description(self, *,
                                  id: str,
                                  description: str) -> None:
        pass

    def get_resources_using_table(self, *,
                                  id: str,
                                  resource_type: ResourceType) -> Dict[str, List[DashboardSummary]]:
        return {}
