# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from jira import JIRA, JIRAError, Issue, User as JiraUser
from typing import Any, List

from flask import current_app as app

from amundsen_application.api.metadata.v0 import USER_ENDPOINT
from amundsen_application.api.utils.request_utils import request_metadata
from amundsen_application.base.base_issue_tracker_client import BaseIssueTrackerClient
from amundsen_application.proxy.issue_tracker_clients.issue_exceptions import IssueConfigurationException
from amundsen_application.models.data_issue import DataIssue, Priority
from amundsen_application.models.issue_results import IssueResults
from amundsen_application.models.user import load_user
from amundsen_common.models.user import User

import urllib.parse
import logging

SEARCH_STUB_ALL_ISSUES = ('text ~ "\\"Table Key: {table_key} [PLEASE DO NOT REMOVE]\\"" '
                          'and (resolution = unresolved or (resolution != unresolved and updated > -30d)) '
                          'order by resolution DESC, priority DESC, createdDate DESC')
SEARCH_STUB_OPEN_ISSUES = ('text ~ "\\"Table Key: {table_key} [PLEASE DO NOT REMOVE]\\"" '
                           'and resolution = unresolved '
                           'order by priority DESC, createdDate DESC')
SEARCH_STUB_CLOSED_ISSUES = ('text ~ "\\"Table Key: {table_key} [PLEASE DO NOT REMOVE]\\"" '
                             'and resolution != unresolved '
                             'order by priority DESC, createdDate DESC')
# this is provided by jira as the type of a bug
ISSUE_TYPE_ID = 1
ISSUE_TYPE_NAME = 'Bug'


class JiraClient(BaseIssueTrackerClient):

    def __init__(self, issue_labels: List[str],
                 issue_tracker_url: str,
                 issue_tracker_user: str,
                 issue_tracker_password: str,
                 issue_tracker_project_id: int,
                 issue_tracker_max_results: int) -> None:
        self.issue_labels = issue_labels
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
            issues = self.jira_client.search_issues(SEARCH_STUB_ALL_ISSUES.format(
                table_key=table_uri),
                maxResults=self.jira_max_results)

            # Call search_issues for only 1 open/closed issue just to get the total values from the response. The
            # total count from all issues may not be accurate if older closed issues are excluded from the response
            open_issues = self.jira_client.search_issues(SEARCH_STUB_OPEN_ISSUES.format(
                table_key=table_uri),
                maxResults=1)
            closed_issues = self.jira_client.search_issues(SEARCH_STUB_CLOSED_ISSUES.format(
                table_key=table_uri),
                maxResults=1)

            returned_issues = self._sort_issues(issues)
            return IssueResults(issues=returned_issues,
                                total=open_issues.total + closed_issues.total,
                                all_issues_url=self._generate_issues_url(SEARCH_STUB_ALL_ISSUES,
                                                                         table_uri,
                                                                         open_issues.total + closed_issues.total),
                                open_issues_url=self._generate_issues_url(SEARCH_STUB_OPEN_ISSUES,
                                                                          table_uri,
                                                                          open_issues.total),
                                closed_issues_url=self._generate_issues_url(SEARCH_STUB_CLOSED_ISSUES,
                                                                            table_uri,
                                                                            closed_issues.total),
                                open_count=open_issues.total)
        except JIRAError as e:
            logging.exception(str(e))
            raise e

    def create_issue(self,
                     table_uri: str,
                     title: str,
                     description: str,
                     priority_level: str,
                     table_url: str,
                     **kwargs: Any) -> DataIssue:
        """
        Creates an issue in Jira
        :param description: Description of the Jira issue
        :param priority_level: Priority level for the ticket
        :param table_uri: Table Uri ie databasetype://database/table
        :param title: Title of the Jira ticket
        :param table_url: Link to access the table
        :param owner_ids: List of table owners user ids
        :param frequent_user_ids: List of table frequent users user ids
        :param project_key: Jira project key to specify where the ticket should be created
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

            reporter = {'name': jira_id}

            # Detected by the jira client based on API version & deployment.
            if self.jira_client.deploymentType == 'Cloud':
                try:
                    user = self.jira_client._fetch_pages(JiraUser, None, "user/search", 0, 1, {'query': user_email})[0]
                    reporter = {'accountId': user.accountId}
                except IndexError:
                    raise Exception('Could not find the reporting user in our Jira installation.')

            issue_type_id = ISSUE_TYPE_ID
            if app.config['ISSUE_TRACKER_ISSUE_TYPE_ID']:
                issue_type_id = app.config['ISSUE_TRACKER_ISSUE_TYPE_ID']

            project_key = kwargs.get('project_key', None)
            proj_key = 'key' if project_key else 'id'
            proj_value = project_key if project_key else self.jira_project_id

            reporting_user = self._get_users_from_ids([user_email])
            owners = self._get_users_from_ids(kwargs.get('owner_ids', []))
            frequent_users = self._get_users_from_ids(kwargs.get('frequent_user_ids', []))

            reporting_user_str = self._generate_reporting_user_str(reporting_user)
            owners_description_str = self._generate_owners_description_str(owners)
            frequent_users_description_str = self._generate_frequent_users_description_str(frequent_users)
            all_users_description_str = self._generate_all_table_users_description_str(owners_description_str,
                                                                                       frequent_users_description_str)

            issue = self.jira_client.create_issue(fields=dict(project={
                proj_key: proj_value
            }, issuetype={
                'id': issue_type_id,
                'name': ISSUE_TYPE_NAME,
            }, labels=self.issue_labels,
                summary=title,
                description=(f'{description} '
                             f'\n *Reported By:* {reporting_user_str if reporting_user_str else user_email} '
                             f'\n *Table Key:* {table_uri} [PLEASE DO NOT REMOVE] '
                             f'\n *Table URL:* {table_url} '
                             f'{all_users_description_str}'),
                priority={
                    'name': Priority.get_jira_severity_from_level(priority_level)
            }, reporter=reporter))

            self._add_watchers_to_issue(issue_key=issue.key, users=owners + frequent_users)

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
                         url=issue.permalink(),
                         status=issue.fields.status.name,
                         priority=Priority.from_jira_severity(issue.fields.priority.name))

    def _generate_issues_url(self, search_stub: str, table_uri: str, issueCount: int) -> str:
        """
        Way to get list of jira tickets
        SDK doesn't return a query
        :param search_stub: search stub for type of query to build
        :param table_uri: table uri from the ui
        :param issueCount: number of jira issues associated to the search
        :return: url to a list of issues in jira
        """
        if issueCount == 0:
            return ''
        search_query = urllib.parse.quote(search_stub.format(table_key=table_uri))
        return f'{self.jira_url}/issues/?jql={search_query}'

    def _sort_issues(self, issues: List[Issue]) -> List[DataIssue]:
        """
        Sorts issues by resolution, first by unresolved and then by resolved. Also maps the issues to
        the object used by the front end. Doesn't include closed issues that are older than 30 days.
        :param issues: Issues returned from the JIRA API
        :return: List of data issues
        """
        open = []
        closed = []
        for issue in issues:
            data_issue = self._get_issue_properties(issue)
            if not issue.fields.resolution:
                open.append(data_issue)
            else:
                closed.append(data_issue)
        return open + closed

    @staticmethod
    def _get_users_from_ids(user_ids: List[str]) -> User:
        """
        Calls get_user metadata API with a user id to retrieve user details.
        :param user_ids: List of strings representing user ids
        :return: List of User objects
        """
        users = []
        for user_id in user_ids:
            url = '{0}{1}/{2}'.format(app.config['METADATASERVICE_BASE'], USER_ENDPOINT, user_id)
            response = request_metadata(url=url)
            if response.status_code == HTTPStatus.OK:
                user = load_user(response.json())
                if user:
                    users.append(user)
        return users

    def _generate_reporting_user_str(self, reporting_user: List[User]) -> str:
        """
        :param reporting_user: List containing a user representing the reporter of the issue
        or an empty list if the reporter's information could not be retrieved
        :return: String of reporting user's information to display in the description
        """
        if not reporting_user:
            return ''
        user = reporting_user[0]
        if user.is_active and user.profile_url:
            return (f'[{user.full_name if user.full_name else user.email}'
                    f'|{user.profile_url}]')
        else:
            return user.email

    def _generate_owners_description_str(self, owners: List[User]) -> str:
        """
        Build a list of table owner information to add to the description of the ticket
        :param owners: List of users representing owners of the table
        :return: String of owners to append in the description
        """
        owners_description_str = '\n Table Owners:' if owners else ''
        user_details_list = []
        inactive_user_details_list = []
        for user in owners:
            if user.is_active and user.profile_url:
                user_details_list.append((f'[{user.full_name if user.full_name else user.email}'
                                          f'|{user.profile_url}] '))
                continue
            else:
                inactive_user_details = f'{user.full_name if user.full_name else user.email}'

            # Append relevant alumni and manager information if the user is a person and inactive
            if not user.is_active and user.full_name:
                inactive_user_details += ' (Alumni) '
                if user.manager_fullname:
                    inactive_user_details += f'\u2022 Manager: {user.manager_fullname} '
            inactive_user_details_list.append(inactive_user_details)
        return '\n '.join(filter(None, [owners_description_str,
                                        '\n '.join(user_details_list),
                                        '\n '.join(inactive_user_details_list)]))

    def _generate_frequent_users_description_str(self, frequent_users: List[User]) -> str:
        """
        Build a list of table frequent user information to add to the description of the ticket; this list will leave
        out inactive frequent users
        :param frequent_users: List of users representing frequent users of the table
        :return: String of frequent users to append in the description
        """
        frequent_users_description_str = '\n Frequent Users: ' if frequent_users else ''
        user_details_list = []
        for user in frequent_users:
            if user.is_active and user.profile_url:
                user_details_list.append((f'[{user.full_name if user.full_name else user.email}'
                                          f'|{user.profile_url}]'))
        return frequent_users_description_str + ', '.join(user_details_list) if user_details_list else ''

    def _generate_all_table_users_description_str(self, owners_str: str, frequent_users_str: str) -> str:
        """
        Takes the generated owners and frequent users information and packages it up into one string for appending
        to the ticket description
        :param owners_str: Owner information
        :param frequent_users_str: Frequent user information
        :return: String including all table users (owners and frequent users) information to append to the description
        """
        table_users_description_title = ''
        if owners_str and frequent_users_str:
            table_users_description_title = '\n\n *Owners and Frequent Users (added as Watchers):* '
        elif owners_str:
            table_users_description_title = '\n\n *Owners (added as Watchers):* '
        elif frequent_users_str:
            table_users_description_title = '\n\n *Frequent Users (added as Watchers):* '
        return table_users_description_title + owners_str + frequent_users_str

    def _add_watchers_to_issue(self, issue_key: str, users: List[User]) -> None:
        """
        Given an issue key and a list of users, add those users as watchers to the issue if they are active
        :param issue_key: key representing an issue
        :param users: list of users to add as watchers to the issue
        """
        for user in users:
            if user.is_active:
                try:
                    # Detected by the jira client based on API version & deployment.
                    if self.jira_client.deploymentType == 'Cloud':
                        jira_user = self.jira_client._fetch_pages(JiraUser, None, "user/search", 0, 1,
                                                                  {'query': user.email})[0]
                        self.jira_client.add_watcher(issue=issue_key, watcher=jira_user.accountId)
                    else:
                        self.jira_client.add_watcher(issue=issue_key, watcher=user.email.split("@")[0])
                except (JIRAError, IndexError):
                    logging.warning('Could not add user {user_email} as a watcher on the issue.'
                                    .format(user_email=user.email))
