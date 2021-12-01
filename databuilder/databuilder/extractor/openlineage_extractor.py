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
    CLUSTER_NAME = 'cluster_name'
    OL_DATASET_NAMESPACE_OVERRIDE = 'namespace_override'
    # Openlineage values key's, which will be used to extract data from an OpenLineage event
    OL_INPUTS_KEY = 'inputs_key'
    OL_OUTPUTS_KEY = 'outputs_key'
    OL_DATASET_NAMESPACE_KEY = 'namespace_key'
    OL_DATASET_DATABASE_KEY = 'database_key'
    OL_DATASET_NAME_KEY = 'dataset_name_key'
    # iterator that will deliver OpenLineage events (lines of NDJSON file)
    OL_EVENTS_ITERATOR = 'ol_events_iterator'

    """
    An Extractor that creates Table Lineage between two tables based on OpenLineage event
    """

    def init(self, conf: ConfigTree) -> None:
        """
        :param conf:
        """
        self.conf = conf
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
        self._lines_iter = conf.get(OpenLineageTableLineageExtractor.OL_EVENTS_ITERATOR, default=None)
        self._generate_TableLineage_events()

    def _extract_dataset_info(self, openlineage_event: Any) -> Iterator[Dict]:
        """
        Yield input/output dict in form of amundsen table keys
        """

        for event in openlineage_event:
            try:
                process_id = event['run']['runId']
                in_and_outs = ((inputs, outputs)
                               for inputs in event[self.ol_inputs_key]
                               for outputs in event[self.ol_outputs_key])
                for row in in_and_outs:
                    yield {'input': self._amundsen_dataset_key(row[0]),
                           'output': self._amundsen_dataset_key(row[1]),
                           'process_id': process_id}
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

    def _generate_TableLineage_events(self) -> Any:
        """
        method set iterator with TableLineage objects based on lines iterator.
        It assumes that each line is a complete json(ndjson)
        """

        lineage_event = (json.loads(line) for line in self._lines_iter)

        table_lineage = (TableLineage(table_key=lineage['input'],
                                      downstream_deps=[lineage['output']],
                                      process_id=lineage['process_id'])

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
            return None
        except Exception as e:
            raise e

    def get_scope(self) -> str:
        return 'extractor.openlineage_tablelineage'
