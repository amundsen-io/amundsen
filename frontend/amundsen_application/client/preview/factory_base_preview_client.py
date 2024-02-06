
from typing import Dict
from abc import abstractmethod

from amundsen_application.base.base_preview_client import BasePreviewClient


class FactoryBasePreviewClient(BasePreviewClient):

    @abstractmethod
    def is_supported_preview_source(self, params: Dict, optionalHeaders: Dict = None) -> bool:
        pass