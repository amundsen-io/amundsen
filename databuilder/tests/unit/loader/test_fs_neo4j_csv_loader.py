# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import collections
import csv
import logging
import os
import unittest
from os import listdir
from os.path import isfile, join

from pyhocon import ConfigFactory
from typing import Dict, Iterable, Any, Callable

from databuilder.job.base_job import Job
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from tests.unit.models.test_neo4j_csv_serde import Movie, Actor, City
from operator import itemgetter


class TestFsNeo4jCSVLoader(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        prefix = '/var/tmp/TestFsNeo4jCSVLoader'
        self._conf = ConfigFactory.from_dict(
            {FsNeo4jCSVLoader.NODE_DIR_PATH: '{}/{}'.format(prefix, 'nodes'),
             FsNeo4jCSVLoader.RELATION_DIR_PATH: '{}/{}'
             .format(prefix, 'relationships'),
             FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR: True})

    def tearDown(self) -> None:
        Job.closer.close()

    def test_load(self) -> None:
        actors = [Actor('Tom Cruise'), Actor('Meg Ryan')]
        cities = [City('San Diego'), City('Oakland')]
        movie = Movie('Top Gun', actors, cities)

        loader = FsNeo4jCSVLoader()
        loader.init(self._conf)
        loader.load(movie)
        loader.close()

        expected_node_path = '{}/../resources/fs_neo4j_csv_loader/nodes'\
            .format(os.path.join(os.path.dirname(__file__)))
        expected_nodes = self._get_csv_rows(expected_node_path, itemgetter('KEY'))
        actual_nodes = self._get_csv_rows(self._conf.get_string(FsNeo4jCSVLoader.NODE_DIR_PATH),
                                          itemgetter('KEY'))
        self.assertEqual(expected_nodes, actual_nodes)

        expected_rel_path = \
            '{}/../resources/fs_neo4j_csv_loader/relationships' \
            .format(os.path.join(os.path.dirname(__file__)))
        expected_relations = self._get_csv_rows(expected_rel_path, itemgetter('START_KEY', 'END_KEY'))
        actual_relations = self._get_csv_rows(self._conf.get_string(FsNeo4jCSVLoader.RELATION_DIR_PATH),
                                              itemgetter('START_KEY', 'END_KEY'))
        self.assertEqual(expected_relations, actual_relations)

    def _get_csv_rows(self,
                      path: str,
                      sorting_key_getter: Callable) -> Iterable[Dict[str, Any]]:
        files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

        result = []
        for f in files:
            with open(f, 'r') as f_input:
                reader = csv.DictReader(f_input)
                for row in reader:
                    result.append(collections.OrderedDict(sorted(row.items())))

        return sorted(result, key=sorting_key_getter)


if __name__ == '__main__':
    unittest.main()
