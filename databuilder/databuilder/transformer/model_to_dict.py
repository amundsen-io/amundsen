# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


from typing import Any, Dict

from pyhocon import ConfigTree

from databuilder.transformer.base_transformer import Transformer
from databuilder.models.elasticsearch_document import ElasticsearchDocument
import json


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
