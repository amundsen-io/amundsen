from http import HTTPStatus

from flask import request
from flask_restful import Resource, reqparse

from amundsen_common.models.feature import FeatureSchema

from metadata_service.entity.resource_type import ResourceType
from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client


class FeatureDetailAPI(Resource):
    """
    FeatureDetail API
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/feature/detail_get.yml')
    def get(self, feature_uri: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            feature = self.client.get_feature(feature_uri=feature_uri)
            schema = FeatureSchema()
            return schema.dump(feature), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'feature_uri {} does not exist'.format(feature_uri)}, HTTPStatus.NOT_FOUND


class FeatureLineageAPI(Resource):
    # TODO get
    pass


class FeatureStatsAPI(Resource):
    # TODO get
    pass


class FeatureGenerationCodeAPI(Resource):
    # TODO get
    pass


class FeatureSampleAPI(Resource):
    # TODO get
    pass


class FeatureOwnerAPI(Resource):
    # TODO put
    # TODO delete
    pass


class FeatureDescriptionAPI(Resource):
    # TODO get
    # TODO put
    pass


class FeatureTagAPI(Resource):
    """
    Only for user tags not owner tags
    """
    # TODO put
    # TODO delete
    pass


class FeatureBadgeAPI(Resource):
    # TODO put
    # TODO delete
    pass


