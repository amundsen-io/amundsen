# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import csv
import logging
import os
import shutil
from csv import DictWriter

from pyhocon import ConfigTree, ConfigFactory
from typing import Dict, Any

from databuilder.job.base_job import Job
from databuilder.loader.base_loader import Loader
from databuilder.models.neo4j_csv_serde import NODE_LABEL, \
    RELATION_START_LABEL, RELATION_END_LABEL, RELATION_TYPE
from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable
from databuilder.utils.closer import Closer


LOGGER = logging.getLogger(__name__)


class FsNeo4jCSVLoader(Loader):
    """
    Write node and relationship CSV file(s) that can be consumed by
    Neo4jCsvPublisher.
    It assumes that the record it consumes is instance of Neo4jCsvSerializable
    """
    # Config keys
    NODE_DIR_PATH = 'node_dir_path'
    RELATION_DIR_PATH = 'relationship_dir_path'
    FORCE_CREATE_DIR = 'force_create_directory'
    SHOULD_DELETE_CREATED_DIR = 'delete_created_directories'

    _DEFAULT_CONFIG = ConfigFactory.from_dict({
        SHOULD_DELETE_CREATED_DIR: True,
        FORCE_CREATE_DIR: False
    })

    def __init__(self) -> None:
        self._node_file_mapping: Dict[Any, DictWriter] = {}
        self._relation_file_mapping: Dict[Any, DictWriter] = {}
        self._closer = Closer()

    def init(self, conf: ConfigTree) -> None:
        """
        Initializing FsNeo4jCsvLoader by creating directory for node files
        and relationship files. Note that the directory defined in
        configuration should not exist.
        :param conf:
        :return:
        """
        conf = conf.with_fallback(FsNeo4jCSVLoader._DEFAULT_CONFIG)

        self._node_dir = conf.get_string(FsNeo4jCSVLoader.NODE_DIR_PATH)
        self._relation_dir = \
            conf.get_string(FsNeo4jCSVLoader.RELATION_DIR_PATH)

        self._delete_created_dir = \
            conf.get_bool(FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR)
        self._force_create_dir = conf.get_bool(FsNeo4jCSVLoader.FORCE_CREATE_DIR)
        self._create_directory(self._node_dir)
        self._create_directory(self._relation_dir)

    def _create_directory(self, path: str) -> None:
        """
        Validate directory does not exist, creates it, register deletion of
        created directory function to Job.closer.
        :param path:
        :return:
        """
        if os.path.exists(path):
            if self._force_create_dir:
                LOGGER.info('Directory exist. Deleting directory {}'.format(path))
                shutil.rmtree(path)
            else:
                raise RuntimeError('Directory should not exist: {}'.format(path))

        os.makedirs(path)

        def _delete_dir() -> None:
            if not self._delete_created_dir:
                LOGGER.warn('Skip Deleting directory {}'.format(path))
                return

            LOGGER.info('Deleting directory {}'.format(path))
            shutil.rmtree(path)

        # Directory should be deleted after publish is finished
        Job.closer.register(_delete_dir)

    def load(self, csv_serializable: Neo4jCsvSerializable) -> None:
        """
        Writes Neo4jCsvSerializable into CSV files.
        There are multiple CSV files that this method writes.
        This is because there're not only node and relationship, but also it
        can also have different nodes, and relationships.

        Common pattern for both nodes and relations:
         1. retrieve csv row (a dict where keys represent a header,
         values represent a row)
         2. using this dict to get a appropriate csv writer and write to it.
         3. repeat 1 and 2

        :param csv_serializable:
        :return:
        """

        node_dict = csv_serializable.next_node()
        while node_dict:
            key = (node_dict[NODE_LABEL], len(node_dict))
            file_suffix = '{}_{}'.format(*key)
            node_writer = self._get_writer(node_dict,
                                           self._node_file_mapping,
                                           key,
                                           self._node_dir,
                                           file_suffix)
            node_writer.writerow(node_dict)
            node_dict = csv_serializable.next_node()

        relation_dict = csv_serializable.next_relation()
        while relation_dict:
            key2 = (relation_dict[RELATION_START_LABEL],
                    relation_dict[RELATION_END_LABEL],
                    relation_dict[RELATION_TYPE],
                    len(relation_dict))

            file_suffix = '{}_{}_{}'.format(key2[0], key2[1], key2[2])
            relation_writer = self._get_writer(relation_dict,
                                               self._relation_file_mapping,
                                               key2,
                                               self._relation_dir,
                                               file_suffix)
            relation_writer.writerow(relation_dict)
            relation_dict = csv_serializable.next_relation()

    def _get_writer(self,
                    csv_record_dict: Dict[str, Any],
                    file_mapping: Dict[Any, DictWriter],
                    key: Any,
                    dir_path: str,
                    file_suffix: str
                    ) -> DictWriter:
        """
        Finds a writer based on csv record, key.
        If writer does not exist, it's creates a csv writer and update the
        mapping.

        :param csv_record_dict:
        :param file_mapping:
        :param key:
        :param file_suffix:
        :return:
        """
        writer = file_mapping.get(key)
        if writer:
            return writer

        LOGGER.info('Creating file for {}'.format(key))

        file_out = open('{}/{}.csv'.format(dir_path, file_suffix), 'w', encoding='utf8')
        writer = csv.DictWriter(file_out, fieldnames=csv_record_dict.keys(),
                                quoting=csv.QUOTE_NONNUMERIC)

        def file_out_close() -> None:
            LOGGER.info('Closing file IO {}'.format(file_out))
            file_out.close()
        self._closer.register(file_out_close)

        writer.writeheader()
        file_mapping[key] = writer

        return writer

    def close(self) -> None:
        """
        Any closeable callable registered in _closer, it will close.
        :return:
        """
        self._closer.close()

    def get_scope(self) -> str:
        return "loader.filesystem_csv_neo4j"
