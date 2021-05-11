from http import HTTPStatus

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
    def get(self, table_uri: str) -> Iterable[Union[Mapping, int, None]]:
        try:
            table = self.client.get_table(table_uri=table_uri)
            schema = FeatureSchema()
            return schema.dump(table), HTTPStatus.OK

        except NotFoundException:
            return {'message': 'table_uri {} does not exist'.format(table_uri)}, HTTPStatus.NOT_FOUND
