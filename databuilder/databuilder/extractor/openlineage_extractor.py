# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from os import path, walk
from typing import (
    Any, Dict, Generator, Iterator,
)

from pyhocon import ConfigTree
from urllib.parse import urlparse

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_lineage import TableLineage

LOGGER = logging.getLogger(__name__)


class OpenLineageTableLineageExtractor(Extractor):
    # Config keys
    TABLE_LINEAGE_FILE_LOCATION = 'table_lineage_file_location'
    CLUSTER_NAME = 'cluster_name'
    OL_DATASET_NAMESPACE_OVERRIDE = 'namespace_override'
    # Openlineage values key's, which will be used to extract data from an OpenLineage event
    OL_INPUTS_KEY = 'inputs_key'
    OL_OUTPUTS_KEY = 'outputs_key'
    OL_DATASET_NAMESPACE_KEY = 'namespace_key'
    OL_DATASET_DATABASE_KEY = 'database_key'
    OL_DATASET_NAME_KEY = 'dataset_name_key'
    BOTO3_S3_RESOURCE = 'boto3_s3_resource'

    """
    An Extractor that creates Table Lineage between two tables based on OpenLineage event
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
        self.table_lineage_file_location = conf.get_string(OpenLineageTableLineageExtractor.TABLE_LINEAGE_FILE_LOCATION)
        self.cluster_name = conf.get_string(OpenLineageTableLineageExtractor.CLUSTER_NAME)
        self.ol_inputs_key = conf.get_string(OpenLineageTableLineageExtractor.OL_INPUTS_KEY, default='inputs')
        self.ol_outputs_key = conf.get_string(OpenLineageTableLineageExtractor.OL_OUTPUTS_KEY, default='outputs')
        self.ol_namespace_key = conf.get_string(
            OpenLineageTableLineageExtractor.OL_DATASET_NAMESPACE_KEY, default='namespace')
        self.ol_database_key = conf.get_string(
            OpenLineageTableLineageExtractor.OL_DATASET_DATABASE_KEY, default='database')
        self.ol_dataset_name_key = conf.get_string(
            OpenLineageTableLineageExtractor.OL_DATASET_NAME_KEY, default='name')
        self.ol_namespace_override = conf.get_string(
            OpenLineageTableLineageExtractor.OL_DATASET_NAMESPACE_OVERRIDE, default=None)
        self.s3_resource = conf.get(OpenLineageTableLineageExtractor.BOTO3_S3_RESOURCE, default=None)
        self._load_openlineage_events()

    def _extract_dataset_info(self, openlineage_event: Any) -> Iterator[Dict]:
        """
        Yield input/output dict in form of amundsen table keys
        """

        for event in openlineage_event:
            try:
                in_and_outs = ((inputs, outputs)
                               for inputs in event[self.ol_inputs_key]
                               for outputs in event[self.ol_outputs_key])
                for row in in_and_outs:
                    yield {'input': self._amundsen_dataset_key(row[0]),
                           'output': self._amundsen_dataset_key(row[1])}
            except KeyError:
                LOGGER.error(f'Cannot extract valid input or output from Openlineage event \n {event} ')

    def _amundsen_dataset_key(self, dataset: Dict) -> str:
        """
        Generation of amundsen dataset key with optional namespace overriding.
        Amundsen dataset key format: <namespace>://<cluster_name>.<database>/<table>.
        If dataset name is represented in path form ie. ( /warehouse/database/table )
        only last part of such path will be extracted as dataset name
        """
        namespace = self.ol_namespace_override if self.ol_namespace_override else dataset[self.ol_namespace_key]
        return f'{namespace}://{self.cluster_name}.{dataset[self.ol_database_key]}' \
               f'/{dataset[self.ol_dataset_name_key].split("/")[-1]}'

    def _load_lineage_events_from_s3(self, files_prefix) -> Generator[str]:
        """
        Generator that walt through all files from s3 prefix
        path and yelds them line by line
        """
        try:
            src_bucket = self.s3_resource.Bucket(files_prefix.netloc)
        except AttributeError as e:
            raise Exception(f"You have to provide valid s3 resource object when using s3 paths \n {e} ")
        files = src_bucket.objects.filter(Prefix=files_prefix.path)
        for file in files:
            for line in map(lambda x: x.decode('utf-8'), file.get()['Body'].iter_lines()):
                yield line

    def _load_lineage_events_from_local_fs(self) -> Generator[str]:
        """
        Generator that walt through all files from local
        path and yelds them line by line
        """
        for file_path in self.absolute_fs_file_path():
            with open(file_path, 'r') as file:
                for line in file.readlines():
                    yield line

    def _load_openlineage_events(self) -> Any:
        """
        Prepare iterators with file lines and TableLineage events
        """
        file_url = urlparse(self.table_lineage_file_location)
        if file_url.scheme == 's3':
            self._lines_iter = iter(self._load_lineage_events_from_s3(file_url))
        else:
            self._lines_iter = iter(self._load_lineage_events_from_local_fs())
        self._generate_TableLineage_events()

    def _generate_TableLineage_events(self) -> Any:
        """
        method set iterator with TableLineage objects based on lines iterator.
        It assumes that each line is a complete json(ndjson)
        """

        lineage_event = (json.loads(line) for line in self._lines_iter)

        table_lineage = (TableLineage(table_key=lineage['input'],
                                      downstream_deps=[lineage['output']])

                         for lineage in self._extract_dataset_info(lineage_event))
        self._iter = table_lineage

    def absolute_fs_file_path(self) -> Generator[str]:
        """
        helper method for listing files from local directories
        """
        if path.isdir(self.table_lineage_file_location):
            for dirpath, _, filenames in walk(self.table_lineage_file_location):
                for f in filenames:
                    yield path.abspath(path.join(dirpath, f))
        else:
            yield self.table_lineage_file_location

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.openlineage_tablelineage'
