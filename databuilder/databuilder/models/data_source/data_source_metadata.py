from typing import (
    Iterator, Optional, Dict
)
from enum import Enum
from abc import ABC, abstractmethod
import re

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable


def convert_to_uri_safe_str(input_string: str) -> str:
    return re.sub(r'\W+', '_', input_string).lower()


class DataProvider(GraphSerializable):

    DATA_PROVIDER_NODE_LABEL = 'Data_Provider'
    DATA_PROVIDER_NODE_KEY = "data_provider://{name}"
    DATA_PROVIDER_NODE_ATTR_NAME = 'name'
    DATA_PROVIDER_NODE_ATTR_WEBSITE = 'website'
    # Should be broken out to a Description node
    DATA_PROVIDER_NODE_ATTR_DESC = 'desc'


    def __init__(self,
                 name: str,
                 website: str,
                 desc: str
                 ) -> None:

        self.name = name
        self.website = website
        self.desc = desc

        self._node_iter = self._create_node_iterator()

    def __repr__(self) -> str:
        return f'DataProvider({self.get_key()!r}, {self.name!r}, {self.website!r}, {self.desc!r})'

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        pass

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        yield GraphNode(
            key=self.get_key(),
            label=self.DATA_PROVIDER_NODE_LABEL,
            attributes={
                self.DATA_PROVIDER_NODE_ATTR_NAME: self.name,
                self.DATA_PROVIDER_NODE_ATTR_WEBSITE: self.website,
                self.DATA_PROVIDER_NODE_ATTR_DESC: self.desc
            }
        )

    def get_name_for_uri(self) -> str:
        return convert_to_uri_safe_str(self.name)

    def get_key(self) -> str:
        return self.DATA_PROVIDER_NODE_KEY.format(name=self.get_name_for_uri())


class DataChannel(GraphSerializable):

    class DataChannelType(Enum):
        DATA_FEED = 'data_feed'
        DATA_SHARE = 'data_share'
        API = 'api'
        SFTP = 'sftp'


    DATA_CHANNEL_NODE_LABEL = 'Data_Channel'
    DATA_CHANNEL_NODE_KEY = "{data_provider_name}://{name}/{type}"
    DATA_CHANNEL_NODE_ATTR_NAME = 'name'
    DATA_CHANNEL_NODE_ATTR_TYPE = 'type'
    DATA_CHANNEL_NODE_ATTR_URL = 'url'
    # Should be broken out to a Description node
    DATA_CHANNEL_NODE_ATTR_DESC = 'desc'
    DATA_CHANNEL_NODE_ATTR_LICENSE = 'license'

    DATA_CHANNEL_RELATION_TYPE = 'DATA_CHANNEL'
    DATA_CHANNEL_OF_RELATION_TYPE = 'DATA_CHANNEL_OF'


    def __init__(self,
                 name: str,
                 type: DataChannelType,
                 url: str,
                 desc: str,
                 license: str,
                 data_provider: DataProvider
                 ) -> None:

        self.name = name
        self.type = type
        self.url = url
        self.desc = desc
        self.license = license

        self.data_provider = data_provider

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()

    def __repr__(self) -> str:
        return f'DataChannel({self.get_key()!r}, {self.name!r}, {self.type.value!r}, {self.url!r}, {self.desc!r}, {self.license!r})'

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        yield GraphNode(
            key=self.get_key(),
            label=self.DATA_CHANNEL_NODE_LABEL,
            attributes={
                self.DATA_CHANNEL_NODE_ATTR_NAME: self.name,
                self.DATA_CHANNEL_NODE_ATTR_TYPE: self.type.value,
                self.DATA_CHANNEL_NODE_ATTR_URL: self.url,
                self.DATA_CHANNEL_NODE_ATTR_DESC: self.desc,
                self.DATA_CHANNEL_NODE_ATTR_LICENSE: self.license
            }
        )

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=self.data_provider.get_key(),
            start_key=DataProvider.DATA_PROVIDER_NODE_LABEL,
            end_label=self.DATA_CHANNEL_NODE_LABEL,
            end_key=self.get_key(),
            type=self.DATA_CHANNEL_RELATION_TYPE,
            reverse_type=self.DATA_CHANNEL_OF_RELATION_TYPE,
            attributes={}
        )

    def get_key(self) -> str:
        return self.DATA_CHANNEL_NODE_KEY.format(data_provider_name=self.data_provider.get_name_for_uri(),
                                                    name=convert_to_uri_safe_str(self.name),
                                                    type=self.type.value)


class DataLocation(GraphSerializable):

    class DataLocationType(Enum):
        FILESYSTEM = 'filesystem'
        AWS_S3 = 'aws_s3'
        SHAREPOINT = 'sharepoint'

    DATA_LOCATION_NODE_LABEL = 'Data_Location'
    DATA_LOCATION_ATTR_NAME = 'name'
    DATA_LOCATION_ATTR_TYPE = 'type'
    DATA_LOCATION_NODE_KEY = "{type}://{name}"

    DATA_LOCATION_RELATION_TYPE = 'DATA_LOCATION'
    DATA_LOCATION_OF_RELATION_TYPE = 'DATA_LOCATION_OF'


    def __init__(self,
                 name: str,
                 type: str,
                 data_channel: DataChannel
                 ) -> None:

        self.name = name
        self.type = type
        self.data_channel = data_channel

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()

    def __repr__(self) -> str:
        return f'Data_Location({self.name!r}, {self.type!r})'

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        yield GraphNode(
            key=self.get_key(),
            label=self.DATA_LOCATION_NODE_LABEL,
            attributes=self._get_node_attributes()
        )

    def _get_node_attributes(self) -> Dict[str,str]:
        return {
            self.DATA_LOCATION_ATTR_NAME: self.name,
            self.DATA_LOCATION_ATTR_TYPE: self.type
        }

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        yield GraphRelationship(
            start_label=DataChannel.DATA_CHANNEL_NODE_LABEL,
            start_key=self.data_channel.get_key(),
            end_label=self.DATA_LOCATION_NODE_LABEL,
            end_key=self.get_key(),
            type=self.DATA_LOCATION_RELATION_TYPE,
            reverse_type=self.DATA_LOCATION_OF_RELATION_TYPE,
            attributes={}
        )

    def get_key(self) -> str:
        return DataLocationType.DATA_LOCATION_NODE_KEY.format(
            name=convert_to_uri_safe_str(self.name),
            type=self.type)


class FilesystemDataLocation(DataLocation):

    FILESYSTEM_DATA_LOCATION_ATTR_DRIVE = "drive"
    DATA_LOCATION_NODE_KEY = f"{DataLocation.DATA_LOCATION_NODE_KEY}"+ "/{drive}"

    def __init__(self,
                 name: str,
                 data_channel: DataChannel,
                 drive: str
                 ) -> None:

        super().__init__(name=name, type='filesystem', data_channel=data_channel)

        self.drive = drive

    def _get_node_attributes(self) -> Dict[str,str]:
        return super()._get_node_attributes().update({
            self.FILESYSTEM_DATA_LOCATION_ATTR_DRIVE: self.drive
        })

    def get_key(self) -> str:
        return FilesystemDataLocation.DATA_LOCATION_NODE_KEY.format(
            name=convert_to_uri_safe_str(self.name),
            type=self.type,
            drive=convert_to_uri_safe_str(self.drive))


class AwsS3DataLocation(DataLocation):

    AWS_S3_DATA_LOCATION_ATTR_BUCKET = "bucket"
    DATA_LOCATION_NODE_KEY = f"{DataLocation.DATA_LOCATION_NODE_KEY}" + "/{bucket}"

    def __init__(self,
                 name: str,
                 data_channel: DataChannel,
                 bucket: str
                 ) -> None:

        super().__init__(name=name, type='aws_s3', data_channel=data_channel)

        self.bucket = bucket

    def _get_node_attributes(self) -> Dict[str,str]:
        return super()._get_node_attributes().update({
            self.AWS_S3_DATA_LOCATION_ATTR_BUCKET: self.bucket
        })

    def get_key(self) -> str:
        return AwsS3DataLocation.DATA_LOCATION_NODE_KEY.format(
            name=convert_to_uri_safe_str(self.name),
            type=self.type,
            bucket=convert_to_uri_safe_str(self.bucket))

class SharepointDataLocation(DataLocation):

    SHAREPOINT_DATA_LOCATION_ATTR_DOCUMENT_LIBRARY = "document_library"
    DATA_LOCATION_NODE_KEY = f"{DataLocation.DATA_LOCATION_NODE_KEY}" + "/{document_library}"

    def __init__(self,
                 name: str,
                 data_channel: DataChannel,
                 document_library: str
                 ) -> None:

        super().__init__(name=name, type='sharepoint', data_channel=data_channel)

        self.document_library = document_library

    def _get_node_attributes(self) -> Dict[str,str]:
        return super()._get_node_attributes().update({
            self.SHAREPOINT_DATA_LOCATION_ATTR_DOCUMENT_LIBRARY: self.document_library
        })

    def get_key(self) -> str:
        return SharepointDataLocation.DATA_LOCATION_NODE_KEY.format(
            name=convert_to_uri_safe_str(self.name),
            type=self.type,
            document_library=convert_to_uri_safe_str(self.bucket))


class File(GraphSerializable):

    FILE_NODE_LABEL = 'File'
    FILE_NODE_ATTR_NAME = 'name'
    FILE_NODE_ATTR_PATH = 'path'
    FILE_NODE_ATTR_DESC = 'desc'
    FILE_NODE_ATTR_TYPE = 'type'
    FILE_NODE_ATTR_IS_DIRECTORY= 'is_directory'

    FILE_RELATION_TYPE = 'FILE'
    FILE_OF_RELATION_TYPE = 'FILE_OF'

    def __init__(self,
                 name: str,
                 desc: str,
                 type: str,
                 path: str,
                 is_directory: bool,
                 data_location: DataLocation,
                 ) -> None:

        self.name = name
        self.desc = desc
        self.type = type
        self.path = path
        self.is_directory = is_directory

        self.data_location = data_location

        self._node_iter = self._create_node_iterator()
        self._relation_iter = self._create_relation_iterator()

    def __repr__(self) -> str:
        return f'File({self.name!r}, {self.desc!r}, {self.type!r}, {self.path!r}, {self.is_directory!r})'

    def create_next_node(self) -> Optional[GraphNode]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def _create_node_iterator(self) -> Iterator[GraphNode]:
        yield GraphNode(
            key=self.get_key(),
            label=self.FILE_NODE_LABEL,
            attributes={
                self.FILE_NODE_ATTR_NAME: self.name,
                self.FILE_NODE_ATTR_DESC: self.desc,
                self.FILE_NODE_ATTR_TYPE: self.type,
                self.FILE_NODE_ATTR_PATH: self.path,
                self.FILE_NODE_ATTR_IS_DIRECTORY: self.is_directory
            }
        )

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        if self.start_key and self.start_label:
            yield GraphRelationship(
                start_label=DataLocation.DATA_LOCATION_NODE_LABEL,
                start_key=self.data_location.get_key(),
                end_label=self.FILE_NODE_LABEL,
                end_key=self.get_key(),
                type=self.FILE_RELATION_TYPE,
                reverse_type=self.FILE_OF_RELATION_TYPE,
                attributes={}
            )

    def get_key(self) -> str:
        return f"{self.data_location.get_key()}/{convert_to_uri_safe_str(self.name)}"