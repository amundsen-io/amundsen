# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

import six
from typing import Dict, Set, Any, Union  # noqa: F401

NODE_KEY = 'KEY'
NODE_LABEL = 'LABEL'
NODE_REQUIRED_HEADERS = {NODE_LABEL, NODE_KEY}

RELATION_START_KEY = 'START_KEY'
RELATION_START_LABEL = 'START_LABEL'
RELATION_END_KEY = 'END_KEY'
RELATION_END_LABEL = 'END_LABEL'
RELATION_TYPE = 'TYPE'
RELATION_REVERSE_TYPE = 'REVERSE_TYPE'
RELATION_REQUIRED_HEADERS = {RELATION_START_KEY, RELATION_START_LABEL,
                             RELATION_END_KEY, RELATION_END_LABEL,
                             RELATION_TYPE, RELATION_REVERSE_TYPE}

LABELS = {NODE_LABEL, RELATION_START_LABEL, RELATION_END_LABEL}
TYPES = {RELATION_TYPE, RELATION_REVERSE_TYPE}


@six.add_metaclass(abc.ABCMeta)
class Neo4jCsvSerializable(object):
    """
    A Serializable abstract class asks subclass to implement next node or
    next relation in dict form so that it can be serialized to CSV file.

    Any model class that needs to be pushed to Neo4j should inherit this class.
    """

    def __init__(self):
        # type: () -> None
        pass

    @abc.abstractmethod
    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        """
        Creates dict where keys represent header in CSV and value represents
        row in CSV file. Should the class could have different types of
        nodes that it needs to serialize, it just needs to provide dict with
        different header -- the one who consumes this class figures it out and
        serialize to different file.

        Node is Neo4j's term of Vertex in Graph. More information on
        https://neo4j.com/docs/developer-manual/current/introduction/
        graphdb-concepts/
        :return: a dict or None if no more record to serialize
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        """
        Creates dict where keys represent header in CSV and value represents
        row in CSV file. Should the class could have different types of
        relations that it needs to serialize, it just needs to provide dict
        with different header -- the one who consumes this class figures it
        out and serialize to different file.

        Relationship is Neo4j's term of Edge in Graph. More information on
        https://neo4j.com/docs/developer-manual/current/introduction/
        graphdb-concepts/
        :return: a dict or None if no more record to serialize
        """
        raise NotImplementedError

    def next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        """
        Provides node(vertex) in dict form.
        Note that subsequent call can create different header (dict.keys())
        which implicitly mean that it needs to be serialized in different
        CSV file (as CSV is in fixed header)
        :return: Non-nested dict where key is CSV header and each value
        is a column
        """
        node_dict = self.create_next_node()
        if not node_dict:
            return None

        self._validate(NODE_REQUIRED_HEADERS, node_dict)
        return node_dict

    def next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        """
        Provides relation(edge) in dict form.
        Note that subsequent call can create different header (dict.keys())
        which implicitly mean that it needs to be serialized in different
        CSV file (as CSV is in fixed header)
        :return: Non-nested dict where key is CSV header and each value
        is a column
        """
        relation_dict = self.create_next_relation()
        if not relation_dict:
            return None

        self._validate(RELATION_REQUIRED_HEADERS, relation_dict)
        return relation_dict

    def _validate(self, required_set, val_dict):
        # type: (Set[str], Dict[str, Any]) -> None
        """
        Validates dict that represents CSV header and a row.
         - Checks if it has required headers for either Node or Relation
         - Checks value of LABEL if only first character is upper case
         - Checks value of TYPE if it's all upper case characters

        :param required_set:
        :param val_dict:
        :return:
        """
        required_count = 0
        for header_col, val_col in \
                ((header_col, val_col) for header_col, val_col
                 in six.iteritems(val_dict) if header_col in required_set):
            required_count += 1

            if header_col in LABELS:
                if not val_col.istitle():
                    raise RuntimeError(
                        'LABEL should only have upper case character on its '
                        'first one: {}'.format(val_col))
            elif header_col in TYPES:
                if not val_col == val_col.upper():
                    raise RuntimeError(
                        'TYPE needs to be upper case: '.format(val_col))

        if required_count != len(required_set):
            raise RuntimeError(
                'Required header missing. Required: {} , Header: {}'.format(
                    required_set, val_dict.keys()))
