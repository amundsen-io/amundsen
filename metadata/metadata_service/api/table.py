from http import HTTPStatus
from typing import Iterable, Mapping, Union, Any

from flask_restful import Resource, fields, reqparse, marshal

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


user_fields = {
    'email': fields.String,
    'first_name': fields.String,  # Optional
    'last_name': fields.String  # Optional
}

table_reader_fields = {
    'reader': fields.Nested(user_fields, attribute='user'),
    'read_count': fields.Integer
}

column_stat_fields = {
    'stat_type': fields.String,
    'stat_val': fields.String,  # Optional
    'start_epoch': fields.Integer,  # Optional
    'end_epoch': fields.Integer,  # Optional

}

column_fields = {
    'name': fields.String,
    'description': fields.String,
    'type': fields.String(attribute='col_type'),
    'sort_order': fields.Integer,
    # Can be an empty list
    'stats': fields.List(fields.Nested(column_stat_fields))
}

watermark_fields = {
    'watermark_type': fields.String,
    'partition_key': fields.String,
    'partition_value': fields.String,
    'create_time': fields.String
}

tag_fields = {
    'tag_type': fields.String,
    'tag_name': fields.String
}

table_writer_fields = {
    'application_url': fields.String(attribute='application_url'),
    'name': fields.String,
    'id': fields.String,
    'description': fields.String  # Optional
}

source_fields = {
    'source_type': fields.String,
    'source': fields.String
}

table_detail_fields = {
    'database': fields.String,
    'cluster': fields.String,
    'schema': fields.String,
    'table_name': fields.String(attribute='name'),
    'table_description': fields.String(attribute='description'),  # Optional
    'tags': fields.List(fields.Nested(tag_fields)),  # Can be an empty list
    # Can be an empty list
    'table_readers': fields.List(fields.Nested(table_reader_fields)),
    # Can be an empty list
    'owners': fields.List(fields.Nested(user_fields)),
    # Can be an empty list
    'columns': fields.List(fields.Nested(column_fields)),
    # Can be an empty list
    'watermarks': fields.List(fields.Nested(watermark_fields)),
    'table_writer': fields.Nested(table_writer_fields),  # Optional
    'last_updated_timestamp': fields.Integer,  # Optional
    'source': fields.Nested(source_fields),  # Optional
    'is_view': fields.Boolean  # Optional
}


class TableDetailAPI(Resource):
    """
    TableDetail API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def get(self, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            table = self.client.get_table(table_uri=table_uri)
            return marshal(table, table_detail_fields), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'table_uri {} does not exist'.format(table_uri)}, HTTPStatus.NOT_FOUND


class TableOwnerAPI(Resource):
    """
    TableOwner API to add / delete owner info
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    def put(self, table_uri: str, owner: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            self.client.add_owner(table_uri=table_uri, owner=owner)
            return {'message': 'The owner {} for table_uri {} '
                               'is added successfully'.format(owner,
                                                              table_uri)}, HTTPStatus.OK
        except Exception as e:
            return {'message': 'The owner {} for table_uri {} '
                               'is not added successfully'.format(owner,
                                                                  table_uri)}, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, table_uri: str, owner: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            self.client.delete_owner(table_uri=table_uri, owner=owner)
            return {'message': 'The owner {} for table_uri {} '
                               'is deleted successfully'.format(owner,
                                                                table_uri)}, HTTPStatus.OK
        except Exception:
            return {'message': 'The owner {} for table_uri {} '
                               'is not deleted successfully'.format(owner,
                                                                    table_uri)}, HTTPStatus.INTERNAL_SERVER_ERROR


class TableDescriptionAPI(Resource):
    """
    TableDescriptionAPI supports PUT and GET operation to upsert table description
    """
    def __init__(self) -> None:
        self.client = get_proxy_client()

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('description', type=str, location='json')

        super(TableDescriptionAPI, self).__init__()

    def get(self, table_uri: str) -> Iterable[Any]:
        """
        Returns description in Neo4j endpoint
        """
        try:
            description = self.client.get_table_description(table_uri=table_uri)
            return {'description': description}, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'table_uri {} does not exist'.format(table_uri)}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR

    def put(self, table_uri: str, description_val: str) -> Iterable[Any]:
        """
        Updates table description
        :param table_uri:
        :param description_val:
        :return:
        """
        try:
            self.client.put_table_description(table_uri=table_uri, description=description_val)
            return None, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'table_uri {} does not exist'.format(table_uri)}, HTTPStatus.NOT_FOUND


class TableTagAPI(Resource):
    """
    TableTagAPI that supports GET, PUT and DELETE operation to add or delete tag
    on table
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('tag', type=str, location='json')
        super(TableTagAPI, self).__init__()

    def put(self, table_uri: str, tag: str) -> Iterable[Union[Mapping, int, None]]:
        """
        API to add a tag to existing table uri.

        :param table_uri:
        :param tag:
        :return:
        """
        try:
            self.client.add_tag(table_uri=table_uri, tag=tag)
            return {'message': 'The tag {} for table_uri {} '
                               'is added successfully'.format(tag,
                                                              table_uri)}, HTTPStatus.OK
        except NotFoundException:
            return \
                {'message': 'The tag {} for table_uri {} '
                            'is not added successfully'.format(tag,
                                                               table_uri)}, \
                HTTPStatus.NOT_FOUND

    def delete(self, table_uri: str, tag: str) -> Iterable[Union[Mapping, int, None]]:
        """
        API to remove a association between a given tag and a table.

        :param table_uri:
        :param tag:
        :return:
        """
        try:
            self.client.delete_tag(table_uri=table_uri, tag=tag)
            return {'message': 'The tag {} for table_uri {} '
                               'is deleted successfully'.format(tag,
                                                                table_uri)}, HTTPStatus.OK
        except NotFoundException:
            return \
                {'message': 'The tag {} for table_uri {} '
                            'is not deleted successfully'.format(tag,
                                                                 table_uri)}, \
                HTTPStatus.NOT_FOUND
