import logging

from flask import Response
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.models.user import load_user

LOGGER = logging.getLogger(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/current_user', methods=['GET'])
def current_user() -> Response:
    if (app.config['CURRENT_USER_METHOD']):
        user = app.config['CURRENT_USER_METHOD'](app)
    else:
        user = load_user({'display_name': '*'})

    return user.to_json()
