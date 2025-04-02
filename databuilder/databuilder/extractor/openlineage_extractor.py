# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import (
    Any, Dict, Iterator,
)

from pyhocon import ConfigTree

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
        self._load_openlineage_event()

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

    def _load_openlineage_event(self) -> Any:

        self.input_file = open(self.table_lineage_file_location, 'r')

        lineage_event = (json.loads(line) for line in self.input_file)

        table_lineage = (TableLineage(table_key=lineage['input'],
                                      downstream_deps=[lineage['output']])

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
            self.input_file.close()
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.openlineage_tablelineage'
