from typing import Any, Iterable, Mapping, Union

from flasgger import swag_from
from flask_restful import Resource, reqparse

from metadata_service.api.badge import BadgeCommon
from metadata_service.api.tag import TagCommon
from metadata_service.proxy import get_proxy_client


class FeatureDetailAPI(Resource):
    """
    FeatureDetail API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/feature/detail_get.yml')
    def get(self, feature_uri: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureLineageAPI(Resource):

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/table/lineage_get.yml')
    def get(self, feature_uri: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureStatsAPI(Resource):

    # TODO integrate stats source for FE
    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/feature/detail_get.yml')
    def get(self, feature_uri: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureGenerationCodeAPI(Resource):

    # TODO use Query common model
    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/feature/detail_get.yml')
    def get(self, feature_uri: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureSampleAPI(Resource):

    # TODO use DataSample common model
    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/feature/detail_get.yml')
    def get(self, feature_uri: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureOwnerAPI(Resource):

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/table/owner_put.yml')
    def put(self, table_uri: str, owner: str) -> Iterable[Union[Mapping, int, None]]:
        pass

    @swag_from('swagger_doc/table/owner_delete.yml')
    def delete(self, table_uri: str, owner: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureDescriptionAPI(Resource):

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/common/description_get.yml')
    def get(self, id: str) -> Iterable[Any]:
        pass

    @swag_from('swagger_doc/common/description_put.yml')
    def put(self, id: str) -> Iterable[Any]:
        pass


class FeatureTagAPI(Resource):
    """
    Only for user tags not owner tags
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('tag_type', type=str, required=False, default='default')

        self._tag_common = TagCommon(client=self.client)

    @swag_from('swagger_doc/tag/tag_put.yml')
    def put(self, id: str, tag: str) -> Iterable[Union[Mapping, int, None]]:
        pass

    @swag_from('swagger_doc/tag/tag_delete.yml')
    def delete(self, id: str, tag: str) -> Iterable[Union[Mapping, int, None]]:
        pass


class FeatureBadgeAPI(Resource):

    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category', type=str, required=True)

        self._badge_common = BadgeCommon(client=self.client)

    @swag_from('swagger_doc/badge/badge_put.yml')
    def put(self, id: str, badge: str) -> Iterable[Union[Mapping, int, None]]:
        pass

    @swag_from('swagger_doc/badge/badge_delete.yml')
    def delete(self, id: str, badge: str) -> Iterable[Union[Mapping, int, None]]:
        pass
