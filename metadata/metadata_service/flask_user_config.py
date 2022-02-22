import logging
from amundsen_common.models.user import UserSchema

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client
from config import LocalConfig
from typing import Dict

LOGGER = logging.getLogger(__name__)


def get_user_from_flask(user_id: str) -> Dict:
    # TODO: extract user details from Flask session if possible
    # Right now, it just passes the user_id (email)
    return {"user_id": user_id}


def get_user_details(user_id: str) -> Dict:
    client = get_proxy_client()
    schema = UserSchema()

    try:
        # This function is available for Neptune
        return schema.dump(client.get_user(id=user_id))
    except NotFoundException:
        LOGGER.info("User not found in the database. Trying to create one using oidc.get_user_detail")

    try:
        user_info = get_user_from_flask(user_id=user_id)

        user = schema.load(user_info)
        new_user, is_created = client.create_update_user(user=user)
        return schema.dump(new_user)

    except Exception as ex:
        LOGGER.exception(str(ex), exc_info=True)
        return {
            "email": user_id,
            "user_id": user_id
        }


class FlaskUserConfig(LocalConfig):
    USER_DETAIL_METHOD = get_user_details
