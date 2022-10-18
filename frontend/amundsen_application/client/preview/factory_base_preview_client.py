
from typing import Dict

from amundsen_application.base.base_superset_preview_client import BasePreviewClient


class FactoryBasePreviewClient(BasePreviewClient):

    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        pass