# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
from http import HTTPStatus
import json
from requests.exceptions import ConnectionError, ReadTimeout
from typing import Tuple

from amundsen_common.models.api import health_check
from flask import current_app as app

from amundsen_application.api.utils.request_utils import request_metadata, request_search


def run_healthcheck() -> Tuple[str, int]:
    search_url = app.config['SEARCHSERVICE_BASE'] + '/healthcheck'
    metadata_url = app.config['METADATASERVICE_BASE'] + '/healthcheck'

    try:
        search_health_resp = request_search(url=search_url, method='GET')
        if search_health_resp.status_code == HTTPStatus.OK:
            search_health = health_check.HealthCheck(**search_health_resp.json())
        else:
            search_checks = {'search_service': {'status': 'Could not get health from search'}}
            search_health = health_check.HealthCheck(status=health_check.FAIL, checks=search_checks)
    except (ConnectionError, ReadTimeout):
        search_checks = {'search_service': {'status': 'Unable to connect.'}}
        search_health = health_check.HealthCheck(status=health_check.FAIL, checks=search_checks)

    try:
        metadata_health_resp = request_metadata(url=metadata_url, method='GET')
        if metadata_health_resp.status_code == HTTPStatus.OK:
            metadata_health = health_check.HealthCheck(**metadata_health_resp.json())
        else:
            metadata_checks = {'metadata_service': {'status': 'Could not get health from metadata'}}
            metadata_health = health_check.HealthCheck(status=health_check.FAIL, checks=metadata_checks)
    except (ConnectionError, ReadTimeout):
        metadata_checks = {'metadata_service': {'status': 'Unable to connect.'}}
        metadata_health = health_check.HealthCheck(status=health_check.FAIL, checks=metadata_checks)

    if search_health.status == health_check.FAIL or metadata_health.status == health_check.FAIL:
        frontend_health_status = health_check.FAIL
    else:
        frontend_health_status = health_check.OK
    frontend_checks = {'search_health': search_health.checks, 'metadata_health': metadata_health.checks}
    frontend_health = health_check.HealthCheck(status=frontend_health_status, checks=frontend_checks)

    return json.dumps(frontend_health.dict()), frontend_health.get_http_status()
