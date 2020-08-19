# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from typing import Union, Dict, Any, Iterable

from databuilder.models.neo4j_csv_serde import (
    NODE_KEY, NODE_LABEL, RELATION_START_KEY, RELATION_START_LABEL,
    RELATION_END_KEY, RELATION_END_LABEL, RELATION_TYPE,
    RELATION_REVERSE_TYPE)
from databuilder.models.neo4j_csv_serde import Neo4jCsvSerializable


class TestSerialize(unittest.TestCase):

    def test_serialize(self) -> None:
        actors = [Actor('Tom Cruise'), Actor('Meg Ryan')]
        cities = [City('San Diego'), City('Oakland')]
        movie = Movie('Top Gun', actors, cities)

        actual = []
        node_row = movie.next_node()
        while node_row:
            actual.append(node_row)
            node_row = movie.next_node()

        expected = [
            {'name': 'Top Gun', 'KEY': 'movie://Top Gun', 'LABEL': 'Movie'},
            {'name': 'Top Gun', 'KEY': 'actor://Tom Cruise', 'LABEL': 'Actor'},
            {'name': 'Top Gun', 'KEY': 'actor://Meg Ryan', 'LABEL': 'Actor'},
            {'name': 'Top Gun', 'KEY': 'city://San Diego', 'LABEL': 'City'},
            {'name': 'Top Gun', 'KEY': 'city://Oakland', 'LABEL': 'City'}
        ]
        self.assertEqual(expected, actual)

        actual = []
        relation_row = movie.next_relation()
        while relation_row:
            actual.append(relation_row)
            relation_row = movie.next_relation()

        expected = [
            {'END_KEY': 'actor://Tom Cruise', 'START_LABEL': 'Movie',
             'END_LABEL': 'Actor', 'START_KEY': 'movie://Top Gun',
             'TYPE': 'ACTOR', 'REVERSE_TYPE': 'ACTED_IN'},
            {'END_KEY': 'actor://Meg Ryan', 'START_LABEL': 'Movie',
             'END_LABEL': 'Actor', 'START_KEY': 'movie://Top Gun',
             'TYPE': 'ACTOR', 'REVERSE_TYPE': 'ACTED_IN'},
            {'END_KEY': 'city://San Diego', 'START_LABEL': 'Movie',
             'END_LABEL': 'City', 'START_KEY': 'city://Top Gun',
             'TYPE': 'FILMED_AT', 'REVERSE_TYPE': 'APPEARS_IN'},
            {'END_KEY': 'city://Oakland', 'START_LABEL': 'Movie',
             'END_LABEL': 'City', 'START_KEY': 'city://Top Gun',
             'TYPE': 'FILMED_AT', 'REVERSE_TYPE': 'APPEARS_IN'}
        ]
        self.assertEqual(expected, actual)


class Actor(object):
    LABEL = 'Actor'
    KEY_FORMAT = 'actor://{}'

    def __init__(self, name: str) -> None:
        self.name = name


class City(object):
    LABEL = 'City'
    KEY_FORMAT = 'city://{}'

    def __init__(self, name: str) -> None:
        self.name = name


class Movie(Neo4jCsvSerializable):
    LABEL = 'Movie'
    KEY_FORMAT = 'movie://{}'
    MOVIE_ACTOR_RELATION_TYPE = 'ACTOR'
    ACTOR_MOVIE_RELATION_TYPE = 'ACTED_IN'
    MOVIE_CITY_RELATION_TYPE = 'FILMED_AT'
    CITY_MOVIE_RELATION_TYPE = 'APPEARS_IN'

    def __init__(self,
                 name: str,
                 actors: Iterable[Actor],
                 cities: Iterable[City]) -> None:
        self._name = name
        self._actors = actors
        self._cities = cities
        self._node_iter = iter(self.create_nodes())
        self._relation_iter = iter(self.create_relation())

    def create_next_node(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Union[Dict[str, Any], None]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    def create_nodes(self) -> Iterable[Dict[str, Any]]:
        result = [{NODE_KEY: Movie.KEY_FORMAT.format(self._name),
                   NODE_LABEL: Movie.LABEL,
                   'name': self._name}]

        for actor in self._actors:
            result.append({NODE_KEY: Actor.KEY_FORMAT.format(actor.name),
                           NODE_LABEL: Actor.LABEL,
                           'name': self._name})

        for city in self._cities:
            result.append({NODE_KEY: City.KEY_FORMAT.format(city.name),
                           NODE_LABEL: City.LABEL,
                           'name': self._name})
        return result

    def create_relation(self) -> Iterable[Dict[str, Any]]:
        result = []
        for actor in self._actors:
            result.append({RELATION_START_KEY:
                           Movie.KEY_FORMAT.format(self._name),
                           RELATION_START_LABEL: Movie.LABEL,
                           RELATION_END_KEY:
                           Actor.KEY_FORMAT.format(actor.name),
                           RELATION_END_LABEL: Actor.LABEL,
                           RELATION_TYPE: Movie.MOVIE_ACTOR_RELATION_TYPE,
                           RELATION_REVERSE_TYPE:
                           Movie.ACTOR_MOVIE_RELATION_TYPE
                           })

        for city in self._cities:
            result.append({RELATION_START_KEY:
                           City.KEY_FORMAT.format(self._name),
                           RELATION_START_LABEL: Movie.LABEL,
                           RELATION_END_KEY:
                           City.KEY_FORMAT.format(city.name),
                           RELATION_END_LABEL: City.LABEL,
                           RELATION_TYPE: Movie.MOVIE_CITY_RELATION_TYPE,
                           RELATION_REVERSE_TYPE:
                           Movie.CITY_MOVIE_RELATION_TYPE
                           })
        return result


if __name__ == '__main__':
    unittest.main()
