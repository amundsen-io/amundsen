# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from mock import MagicMock
from pyhocon import ConfigFactory

from databuilder.transformer.base_transformer import ChainedTransformer


class TestChainedTransformer(unittest.TestCase):

    def test_init_not_called(self) -> None:

        mock_transformer1 = MagicMock()
        mock_transformer2 = MagicMock()
        chained_transformer = ChainedTransformer(transformers=[mock_transformer1, mock_transformer2])

        config = ConfigFactory.from_dict({})
        chained_transformer.init(conf=config)

        chained_transformer.transform(
            {
                'foo': 'bar'
            }
        )

        mock_transformer1.init.assert_not_called()
        mock_transformer1.transform.assert_called_once()
        mock_transformer2.init.assert_not_called()
        mock_transformer2.transform.assert_called_once()

    def test_init_called(self) -> None:

        mock_transformer1 = MagicMock()
        mock_transformer1.get_scope.return_value = 'foo'
        mock_transformer2 = MagicMock()
        mock_transformer2.get_scope.return_value = 'bar'
        chained_transformer = ChainedTransformer(transformers=[mock_transformer1, mock_transformer2],
                                                 is_init_transformers=True)

        config = ConfigFactory.from_dict({})
        chained_transformer.init(conf=config)

        chained_transformer.transform(
            {
                'foo': 'bar'
            }
        )

        mock_transformer1.init.assert_called_once()
        mock_transformer1.transform.assert_called_once()
        mock_transformer2.init.assert_called_once()
        mock_transformer2.transform.assert_called_once()
