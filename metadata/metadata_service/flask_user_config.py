import logging
from amundsen_common.models.user import UserSchema

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client
from config import NeptuneConfig
from typing import Dict

LOGGER = logging.getLogger(__name__)


def prepare_user_info(user_id: str) -> Dict:
    """
    Prepare user info to be persisted into Neptune a the minimal set of fields:
    user_id: used for generating vertex id
    email: used for the mailto: link in the frontend
    full_name: necessary for indexing search results
    """
    return {
        "user_id": user_id,
        "email": user_id,
        "full_name": user_id
    }


def get_user_details(user_id: str) -> Dict:
    client = get_proxy_client()
    schema = UserSchema()

    try:
        user = schema.dump(client.get_user(id=user_id))
        if not user:
            raise NotFoundException(
                message=f"Could not find user_id: {user_id}"
            )
        LOGGER.info(f"Found user: {user}")
        return user
    except NotFoundException:
        LOGGER.info("User not found in the database. Trying to create one...")

    try:
        user_info = prepare_user_info(user_id=user_id)

        user = schema.load(user_info)
        client.create_update_user(user=user)
        new_user = client.get_user(id=user_id)
        if new_user:
            LOGGER.info(f"Successfully created new user: {new_user}")
        else:
            raise Exception(f"Failed to create new user from {user_id}")
        return schema.dump(new_user)

    except Exception as ex:
        LOGGER.exception(str(ex), exc_info=True)
        # Return the required information only
        return {
            "email": user_id,
            "user_id": user_id,
        }


class FlaskUserConfig(NeptuneConfig):
    USER_DETAIL_METHOD = get_user_details
