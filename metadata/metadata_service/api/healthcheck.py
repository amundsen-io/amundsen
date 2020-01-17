from typing import Tuple
from flasgger import swag_from


@swag_from('swagger_doc/healthcheck_get.yml')
def healthcheck() -> Tuple[str, int]:
    return '', 200
