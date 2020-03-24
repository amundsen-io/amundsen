from jira import JIRA, JIRAError, Issue
from typing import List

from flask import current_app as app

from amundsen_application.base.base_issue_tracker_client import BaseIssueTrackerClient
from amundsen_application.proxy.issue_tracker_clients.issue_exceptions import IssueConfigurationException
from amundsen_application.models.data_issue import DataIssue
from amundsen_application.models.issue_results import IssueResults

import urllib.parse
import logging

SEARCH_STUB = 'text ~ "{table_key}" AND resolution = Unresolved order by createdDate DESC'
# this is provided by jira as the type of a bug
ISSUE_TYPE_ID = 1
ISSUE_TYPE_NAME = 'Bug'


class JiraClient(BaseIssueTrackerClient):

    def __init__(self, issue_tracker_url: str,
                 issue_tracker_user: str,
                 issue_tracker_password: str,
                 issue_tracker_project_id: int,
                 issue_tracker_max_results: int) -> None:
        self.jira_url = issue_tracker_url
        self.jira_user = issue_tracker_user
        self.jira_password = issue_tracker_password
        self.jira_project_id = issue_tracker_project_id
        self.jira_max_results = issue_tracker_max_results
        self._validate_jira_configuration()
        self.jira_client = self.get_client()

    def get_client(self) -> JIRA:
        """
        Get the Jira client properly formatted prepared for hitting JIRA
        :return: A Jira client.
        """
        return JIRA(
            server=self.jira_url,
            basic_auth=(self.jira_user, self.jira_password)
        )

    def get_issues(self, table_uri: str) -> IssueResults:
        """
        Runs a query against a given Jira project for tickets matching the key
        Returns open issues sorted by most recently created.
        :param table_uri: Table Uri ie databasetype://database/table
        :return: Metadata of matching issues
        """
        try:
            issues = self.jira_client.search_issues(SEARCH_STUB.format(
                table_key=table_uri),
                maxResults=self.jira_max_results)
            returned_issues = [self._get_issue_properties(issue=issue) for issue in issues]
            return IssueResults(issues=returned_issues,
                                remaining=self._get_remaining_issues(total=issues.total),
                                remaining_url=self._generate_remaining_issues_url(table_uri, returned_issues))
        except JIRAError as e:
            logging.exception(str(e))
            raise e

    def create_issue(self, table_uri: str, title: str, description: str) -> DataIssue:
        """
        Creates an issue in Jira
        :param description: Description of the Jira issue
        :param table_uri: Table Uri ie databasetype://database/table
        :param title: Title of the Jira ticket
        :return: Metadata about the newly created issue
        """
        try:
            if app.config['AUTH_USER_METHOD']:
                user_email = app.config['AUTH_USER_METHOD'](app).email
                # We currently cannot use the email directly because of the following issue:
                # https://community.atlassian.com/t5/Answers-Developer-Questions/JIRA-Rest-API-find-JIRA-user-based-on-user-s-email-address/qaq-p/532715
                jira_id = user_email.split('@')[0]
            else:
                raise Exception('AUTH_USER_METHOD must be configured to set the JIRA issue reporter')

            issue = self.jira_client.create_issue(fields=dict(project={
                'id': self.jira_project_id
            }, issuetype={
                'id': ISSUE_TYPE_ID,
                'name': ISSUE_TYPE_NAME,
            }, summary=title,
                description=(f'{description} '
                             f'\n Reported By: {user_email} '
                             f'\n Table Key: {table_uri} [PLEASE DO NOT REMOVE]'),
                reporter={'name': jira_id}))
            return self._get_issue_properties(issue=issue)
        except JIRAError as e:
            logging.exception(str(e))
            raise e

    def _validate_jira_configuration(self) -> None:
        """
        Validates that all properties for jira configuration are set. Returns a list of missing properties
        to return if they are missing
        :return: String representing missing Jira properties, or an empty string.
        """
        missing_fields = []
        if not self.jira_url:
            missing_fields.append('ISSUE_TRACKER_URL')
        if not self.jira_user:
            missing_fields.append('ISSUE_TRACKER_USER')
        if not self.jira_password:
            missing_fields.append('ISSUE_TRACKER_PASSWORD')
        if not self.jira_project_id:
            missing_fields.append('ISSUE_TRACKER_PROJECT_ID')
        if not self.jira_max_results:
            missing_fields.append('ISSUE_TRACKER_MAX_RESULTS')

        if missing_fields:
            raise IssueConfigurationException(
                f'The following config settings must be set for Jira: {", ".join(missing_fields)} ')

    @staticmethod
    def _get_issue_properties(issue: Issue) -> DataIssue:
        """
        Maps the jira issue object to properties we want in the UI
        :param issue: Jira issue to map
        :return: JiraIssue
        """
        return DataIssue(issue_key=issue.key,
                         title=issue.fields.summary,
                         url=issue.permalink())

    def _get_remaining_issues(self, total: int) -> int:
        """
        Calculates how many issues are not being displayed, so the FE can determine whether to
        display a message about issues remaining
        :param total: number from the result set representing how many issues were found in all
        :return: int - 0, or how many issues remain
        """
        return 0 if total < self.jira_max_results else total - self.jira_max_results

    def _generate_remaining_issues_url(self, table_uri: str, issues: List[DataIssue]) -> str:
        """
        Way to get the full list of jira tickets
        SDK doesn't return a query
        :param table_uri: table uri from the ui
        :param issues: list of jira issues, only needed to grab a ticket name
        :return: url to the full list of issues in jira
        """
        if not issues or len(issues) == 0:
            return ''
        # jira expects a ticket key in the query to default to, so pick the first one
        first_issue_key = issues[0].issue_key
        search_query = urllib.parse.quote(SEARCH_STUB.format(table_key=table_uri))
        return f'{self.jira_url}/browse/{first_issue_key}?jql={search_query}'
