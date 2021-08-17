# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any

from pyhocon import ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_lineage import TableLineage

LOGGER = logging.getLogger(__name__)


class OpenLineageTableLineageExtractor(Extractor):
    # Config keys
    TABLE_LINEAGE_FILE_LOCATION = 'table_lineage_file_location'
    CLUSTER_NAME = 'datalab'
    OL_INPUTS_KEY = 'inputs'
    OL_OUTPUTS_KEY = 'outputs'
    OL_DATASET_NAMESPACE_KEY = 'namespace'
    OL_DATASET_DATABASE_KEY = 'database'
    OL_DATASET_NAME_KEY = 'name'

    """
    An Extractor that creates Table Lineage between two tables
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
        self.ol_namespace_key = conf.get_string(OpenLineageTableLineageExtractor.OL_DATASET_NAMESPACE_KEY, default='namespace')
        self.ol_database_key = conf.get_string(OpenLineageTableLineageExtractor.OL_DATASET_DATABASE_KEY, default='database')
        self.ol_dataset_name_key = conf.get_string(OpenLineageTableLineageExtractor.OL_DATASET_NAME_KEY, default='name')
        self._load_openlineage_event()

    def _extract_dataset_info(self, openlineage_event):
        for event in openlineage_event:
            in_and_outs = ({'input': inputs, 'output': outputs} for inputs in event.get('inputs') for outputs in event.get('outputs'))
            for row in in_and_outs:
                yield row

    def _amundsen_dataset_key(self, dataset):
        return f'{dataset[self.ol_namespace_key]}://{self.cluster_name}.{dataset[self.ol_database_key]}' \
               f'/{dataset[self.ol_dataset_name_key].split("/")[-1]}'

    def _load_openlineage_event(self):

        self.file_inputs = open(self.table_lineage_file_location, 'r')
        lineage_event = (json.loads(line) for line in self.file_inputs)

        table_lineage = (TableLineage(table_key=self._amundsen_dataset_key(lineage['input']),
                                      downstream_deps=[self._amundsen_dataset_key(lineage['output'])])

                         for lineage in self._extract_dataset_info(lineage_event))

        self._iter = table_lineage

    def extract(self) -> Any:
        """
        Yield the csv result one at a time.
        convert the result to model if a model_class is provided
        """
        try:
            return next(self._iter)
        except StopIteration:
            self.file_inputs.close()
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.openlineage_tablelineage'
