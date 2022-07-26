# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


import json
from typing import Any, Dict

from pyhocon import ConfigTree

from databuilder.models.elasticsearch_document import ElasticsearchDocument
from databuilder.transformer.base_transformer import Transformer


class ModelToDictTransformer(Transformer):
    """
    Transforms model into dictionary.
    For now we are passing it to SearchMetadatatoElasticasearchTask as transformer to
    convert TableESDocument's and UserESDocument's properties to dictionary.
    """

    def init(self, conf: ConfigTree) -> None:
        pass

    def transform(self, record: ElasticsearchDocument) -> Dict[str, Any]:
        """
        Return properties of a ElasticsearchDocument instance (EX: TableESDocument)
        as a dictionary.
        """
        return json.loads(record.to_json())

    def get_scope(self) -> str:
        return 'transformer.model_to_dict'
