# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from flask import current_app as app
from amundsen_application.models.user import load_user, User
from amundsen_application.api.utils.request_utils import request_metadata

USER_ENDPOINT = '/user'


def get_test_user(app: app, user_id: str) -> User:  # type: ignore

    url = '{0}{1}/{2}'.format(app.config['METADATASERVICE_BASE'], USER_ENDPOINT, user_id)
    response = request_metadata(url=url)
    status_code = response.status_code
   
    return load_user(response.json())
