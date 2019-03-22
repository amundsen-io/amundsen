from typing import Union, List, Dict, Any

from atlasclient.client import Atlas

from metadata_service.entity.popular_table import PopularTable
from metadata_service.entity.user_detail import User as UserEntity
from metadata_service.entity.table_detail import Table
from metadata_service.proxy import BaseProxy
from metadata_service.util import UserResourceRel


class AtlasProxy(BaseProxy):
    """
    Atlas Proxy client for the amundsen metadata
    """

    def __init__(self, *,
                 host: str,
                 port: int,
                 user: str = 'admin',
                 password: str = '') -> None:
        """
        Initiate the Apache Atlas client with the provided credentials
        """
        self._driver = Atlas(host=host, port=port, username=user, password=password)

    def get_user_detail(self, *, user_id: str) -> Union[UserEntity, None]:
        pass

    def get_table(self, *, table_uri: str) -> Table:
        pass

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
        return []

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
