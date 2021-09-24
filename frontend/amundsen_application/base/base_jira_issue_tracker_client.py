# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
import logging
import requests

from flask import Response as FlaskResponse, make_response, jsonify
from http import HTTPStatus
from marshmallow import ValidationError
from requests import Response
from typing import Dict

from amundsen_application.base.base_issue_tracker_client import BaseIssueTrackerClient
from amundsen_application.models.data_issue import DataIssue
from amundsen_application.models.issue_results import IssueResults


class JiraIssueTrackerClient(BaseIssueTrackerClient):
    def __init__(self) -> None:
        self.token = app.config['ISSUE_TRACKER_API_TOKEN'] 
        self.url = app.config['ISSUE_TRACKER_URL']
        self.user = app.config['ISSUE_TRACKER_USER']
        self.headers = {}

    def get_issues(self, table_uri: str) -> IssueResults:
        try:
            response = requests.get(self.url+'/rest/api/latest/search?jql=project=DIP', auth=(self.user, self.token))
            issues = response.json()
            logging.info(issues['total'])
        except Exception as err:
            logging.error("Issue tracker get error " + str(err))


    def create_issue(self, table_uri: str, title: str, description: str, table_url: str) -> DataIssue:
        pass
