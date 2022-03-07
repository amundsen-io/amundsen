import logging
from amundsen_common.models.user import UserSchema

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client
from config import NeptuneConfig
from typing import Dict

LOGGER = logging.getLogger(__name__)


def get_user_from_flask(user_id: str) -> Dict:
    # TODO: extract user details from Flask session if possible
    # Right now, it just passes the user_id (email)
    LOGGER.info(f"get_user_from_flask: {user_id}")
    print(f"get_user_from_flask: {user_id}")
    return {"user_id": user_id}


def get_user_details(user_id: str) -> Dict:
    client = get_proxy_client()
    schema = UserSchema()

    LOGGER.info(f"get_user_details_start: {user_id}")

    try:
        user = schema.dump(client.get_user(id=user_id))
        if not user:
            raise NotFoundException
        LOGGER.info(f"Found user: {user}")
        # This function is available for Neptune
        return user
    except NotFoundException:
        LOGGER.info("User not found in the database. Trying to create one...")

    try:
        user_info = get_user_from_flask(user_id=user_id)

        user = schema.load(user_info)
        new_user, is_created = client.create_update_user(user=user)
        LOGGER.info(f"get_user_details_success: {new_user}")
        return schema.dump(new_user)

    except Exception as ex:
        LOGGER.exception(str(ex), exc_info=True)
        return {
            "email": user_id,
            "user_id": user_id
        }


class FlaskUserConfig(NeptuneConfig):
    LOGGER.info("Starting app with FlaskUserConfig")
    print("Starting app with FlaskUserConfig")
    USER_DETAIL_METHOD = get_user_details
