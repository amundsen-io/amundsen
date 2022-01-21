# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from typing import Any

from elasticsearch import Elasticsearch
from mock import MagicMock
from pyhocon import ConfigFactory, ConfigTree

from databuilder import Scoped
from databuilder.extractor.es_metadata_extractor import ElasticsearchMetadataExtractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata


class TestElasticsearchIndexExtractor(unittest.TestCase):
    config_not_sorted = ConfigFactory.from_dict({
        'extractor.es_metadata.schema': 'schema_name',
        'extractor.es_metadata.cluster': 'cluster_name',
        'extractor.es_metadata.correct_sort_order': False,
        'extractor.es_metadata.client': Elasticsearch()})

    config_sorted = ConfigFactory.from_dict({
        'extractor.es_metadata.schema': 'schema_name',
        'extractor.es_metadata.cluster': 'cluster_name',
        'extractor.es_metadata.correct_sort_order': True,
        'extractor.es_metadata.client': Elasticsearch()})

    es_version_v6 = '6.0.0'

    es_version_v7 = '7.0.0'

    indices_v6 = {
        '.technical_index': {
            'mappings': {
                'doc': {
                    'properties': {
                        'keyword_property': {
                            'type': 'keyword'
                        },
                        'long_property': {
                            'type': 'long'
                        }
                    }
                }
            },
            'aliases': {
                'search_index': {}
            },
            'settings': {
                'number_of_replicas': 1
            }
        },
        'proper_index': {
            'mappings': {
                'doc': {
                    'properties': {
                        'keyword_property': {
                            'type': 'keyword'
                        },
                        'long_property': {
                            'type': 'long'
                        }
                    }
                }
            },
            'aliases': {
                'search_index': {}
            },
            'settings': {
                'number_of_replicas': 1
            }
        }
    }

    indices_v7 = {
        '.technical_index': {
            'mappings': {
                'properties': {
                    'keyword_property': {
                        'type': 'keyword'
                    },
                    'long_property': {
                        'type': 'long'
                    }
                }
            },
            'aliases': {
                'search_index': {}
            },
            'settings': {
                'number_of_replicas': 1
            }
        },
        'proper_index': {
            'mappings': {
                'properties': {
                    'keyword_property': {
                        'type': 'keyword'
                    },
                    'long_property': {
                        'type': 'long'
                    }
                }
            },
            'aliases': {
                'search_index': {}
            },
            'settings': {
                'number_of_replicas': 1
            }
        }
    }

    indices_hierarchical_v6 = {
        'proper_index': {
            'mappings': {
                'doc': {
                    'properties': {
                        'keyword': {
                            'properties': {
                                'inner': {
                                    'type': 'keyword'
                                }
                            }
                        },
                        'long': {
                            'properties': {
                                'inner': {
                                    'type': 'long'
                                }
                            }
                        }
                    }
                }
            },
            'aliases': {
                'search_index': {}
            },
            'settings': {
                'number_of_replicas': 1
            }
        }
    }

    indices_hierarchical_v7 = {
        'proper_index': {
            'mappings': {
                'properties': {
                    'keyword': {
                        'properties': {
                            'inner': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'long': {
                        'properties': {
                            'inner': {
                                'type': 'long'
                            }
                        }
                    }
                }
            },
            'aliases': {
                'search_index': {}
            },
            'settings': {
                'number_of_replicas': 1
            }
        }
    }

    def _get_extractor(self, config: ConfigTree) -> Any:
        extractor = ElasticsearchMetadataExtractor()
        extractor.init(Scoped.get_scoped_conf(conf=config, scope=extractor.get_scope()))

        return extractor

    def test_extractor_without_technical_data_es_v6(self) -> None:
        extractor = self._get_extractor(self.config_not_sorted)

        extractor._get_es_version = lambda: self.es_version_v6
        extractor.es.indices.get = MagicMock(return_value=self.indices_v6)

        expected = TableMetadata('elasticsearch', 'cluster_name', 'schema_name', 'proper_index',
                                 None, [ColumnMetadata('keyword_property', '', 'keyword', 0, []),
                                        ColumnMetadata('long_property', '', 'long', 0, [])], False, [])

        result = []

        while True:
            entry = extractor.extract()

            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(1, len(result))
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_extractor_without_technical_data_es_v7(self) -> None:
        extractor = self._get_extractor(self.config_not_sorted)

        extractor._get_es_version = lambda: self.es_version_v7
        extractor.es.indices.get = MagicMock(return_value=self.indices_v7)

        expected = TableMetadata('elasticsearch', 'cluster_name', 'schema_name', 'proper_index',
                                 None, [ColumnMetadata('keyword_property', '', 'keyword', 0, []),
                                        ColumnMetadata('long_property', '', 'long', 0, [])], False, [])

        result = []

        while True:
            entry = extractor.extract()

            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(1, len(result))
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_extractor_hierarchical_es_v6(self) -> None:
        extractor = self._get_extractor(self.config_not_sorted)

        extractor._get_es_version = lambda: self.es_version_v6
        extractor.es.indices.get = MagicMock(return_value=self.indices_hierarchical_v6)

        expected = TableMetadata('elasticsearch', 'cluster_name', 'schema_name', 'proper_index',
                                 None, [ColumnMetadata('keyword.inner', '', 'keyword', 0, []),
                                        ColumnMetadata('long.inner', '', 'long', 0, [])], False, [])

        result = []

        while True:
            entry = extractor.extract()

            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(1, len(result))
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_extractor_hierarchical_es_v7(self) -> None:
        extractor = self._get_extractor(self.config_not_sorted)

        extractor._get_es_version = lambda: self.es_version_v7
        extractor.es.indices.get = MagicMock(return_value=self.indices_hierarchical_v7)

        expected = TableMetadata('elasticsearch', 'cluster_name', 'schema_name', 'proper_index',
                                 None, [ColumnMetadata('keyword.inner', '', 'keyword', 0, []),
                                        ColumnMetadata('long.inner', '', 'long', 0, [])], False, [])

        result = []

        while True:
            entry = extractor.extract()

            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(1, len(result))
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_extractor_sorted_es_v6(self) -> None:
        extractor = self._get_extractor(self.config_sorted)

        extractor._get_es_version = lambda: self.es_version_v6
        extractor.es.indices.get = MagicMock(return_value=self.indices_v6)

        expected = TableMetadata('elasticsearch', 'cluster_name', 'schema_name', 'proper_index',
                                 None, [ColumnMetadata('keyword_property', '', 'keyword', 0, []),
                                        ColumnMetadata('long_property', '', 'long', 1, [])], False, [])

        result = []

        while True:
            entry = extractor.extract()

            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(1, len(result))
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_extractor_sorted_es_v7(self) -> None:
        extractor = self._get_extractor(self.config_sorted)

        extractor._get_es_version = lambda: self.es_version_v7
        extractor.es.indices.get = MagicMock(return_value=self.indices_v7)

        expected = TableMetadata('elasticsearch', 'cluster_name', 'schema_name', 'proper_index',
                                 None, [ColumnMetadata('keyword_property', '', 'keyword', 0, []),
                                        ColumnMetadata('long_property', '', 'long', 1, [])], False, [])

        result = []

        while True:
            entry = extractor.extract()

            if entry:
                result.append(entry)
            else:
                break

        self.assertEqual(1, len(result))
        self.assertEqual(expected.__repr__(), result[0].__repr__())
