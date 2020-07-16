# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import tempfile
import unittest
from mock import patch

from pyhocon import ConfigTree, ConfigFactory  # noqa: F401
from typing import Any  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import Transformer


class TestJob(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        self.temp_dir_path = tempfile.mkdtemp()
        self.dest_file_name = '{}/superhero.json'.format(self.temp_dir_path)
        self.conf = ConfigFactory.from_dict(
            {'loader.superhero.dest_file': self.dest_file_name})

    def tearDown(self):
        # type: () -> None
        shutil.rmtree(self.temp_dir_path)

    def test_job(self):
        # type: () -> None

        with patch("databuilder.job.job.StatsClient") as mock_statsd:
            task = DefaultTask(SuperHeroExtractor(),
                               SuperHeroLoader(),
                               transformer=SuperHeroReverseNameTransformer())

            job = DefaultJob(self.conf, task)
            job.launch()

            expected_list = ['{"hero": "Super man", "name": "tneK kralC"}',
                             '{"hero": "Bat man", "name": "enyaW ecurB"}']
            with open(self.dest_file_name, 'r') as file:
                for expected in expected_list:
                    actual = file.readline().rstrip('\n')
                    self.assertEqual(expected, actual)
                self.assertFalse(file.readline())

        self.assertEqual(mock_statsd.call_count, 0)


class TestJobNoTransform(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        self.temp_dir_path = tempfile.mkdtemp()
        self.dest_file_name = '{}/superhero.json'.format(self.temp_dir_path)
        self.conf = ConfigFactory.from_dict(
            {'loader.superhero.dest_file': self.dest_file_name})

    def tearDown(self):
        # type: () -> None
        shutil.rmtree(self.temp_dir_path)

    def test_job(self):
        # type: () -> None
        task = DefaultTask(SuperHeroExtractor(), SuperHeroLoader())

        job = DefaultJob(self.conf, task)
        job.launch()

        expected_list = ['{"hero": "Super man", "name": "Clark Kent"}',
                         '{"hero": "Bat man", "name": "Bruce Wayne"}']
        with open(self.dest_file_name, 'r') as file:
            for expected in expected_list:
                actual = file.readline().rstrip('\n')
                self.assertEqual(expected, actual)
            self.assertFalse(file.readline())


class TestJobStatsd(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        self.temp_dir_path = tempfile.mkdtemp()
        self.dest_file_name = '{}/superhero.json'.format(self.temp_dir_path)
        self.conf = ConfigFactory.from_dict(
            {'loader.superhero.dest_file': self.dest_file_name,
             'job.is_statsd_enabled': True,
             'job.identifier': 'foobar'})

    def tearDown(self):
        # type: () -> None
        shutil.rmtree(self.temp_dir_path)

    def test_job(self):
        # type: () -> None
        with patch("databuilder.job.job.StatsClient") as mock_statsd:
            task = DefaultTask(SuperHeroExtractor(), SuperHeroLoader())

            job = DefaultJob(self.conf, task)
            job.launch()

            expected_list = ['{"hero": "Super man", "name": "Clark Kent"}',
                             '{"hero": "Bat man", "name": "Bruce Wayne"}']
            with open(self.dest_file_name, 'r') as file:
                for expected in expected_list:
                    actual = file.readline().rstrip('\n')
                    self.assertEqual(expected, actual)
                self.assertFalse(file.readline())

            self.assertEqual(mock_statsd.return_value.incr.call_count, 1)


class SuperHeroExtractor(Extractor):
    def __init__(self):
        # type: () -> None
        pass

    def init(self, conf):
        # type: (ConfigTree) -> None
        self.records = [SuperHero(hero='Super man', name='Clark Kent'),
                        SuperHero(hero='Bat man', name='Bruce Wayne')]
        self.iter = iter(self.records)

    def extract(self):
        # type: () -> Any
        try:
            return next(self.iter)
        except StopIteration:
            return None

    def get_scope(self):
        # type: () -> str
        return 'extractor.superhero'


class SuperHero:
    def __init__(self,
                 hero,
                 name):
        # type: (str, str) -> None
        self.hero = hero
        self.name = name

    def __repr__(self):
        # type: () -> str
        return "SuperHero(hero={0}, name={1})".format(self.hero, self.name)


class SuperHeroReverseNameTransformer(Transformer):
    def __init__(self):
        # type: () -> None
        pass

    def init(self, conf):
        # type: (ConfigTree) -> None
        pass

    def transform(self, record):
        # type: (Any) -> Any
        record.name = record.name[::-1]
        return record

    def get_scope(self):
        # type: () -> str
        return 'transformer.superhero'


class SuperHeroLoader(Loader):
    def init(self, conf):
        # type: (ConfigTree) -> None
        self.conf = conf
        dest_file_path = self.conf.get_string('dest_file')
        print('Loading to {}'.format(dest_file_path))
        self.dest_file_obj = open(self.conf.get_string('dest_file'), 'w')

    def load(self, record):
        # type: (Any) -> None
        str = json.dumps(record.__dict__, sort_keys=True)
        print('Writing record: {}'.format(str))
        self.dest_file_obj.write('{}\n'.format(str))
        self.dest_file_obj.flush()

    def get_scope(self):
        # type: () -> str
        return 'loader.superhero'


if __name__ == '__main__':
    unittest.main()
