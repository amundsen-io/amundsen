# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import List

from amundsen_application.models.data_issue import DataIssue
from amundsen_application.models.issue_results import IssueResults


class BaseIssueTrackerClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_issues(self, table_uri: str) -> IssueResults:
        """
        Gets issues from the issue tracker
        :param table_uri: Table Uri ie databasetype://database/table
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def create_issue(self,
                     table_uri: str,
                     title: str,
                     description: str,
                     owner_ids: List[str],
                     frequent_user_ids: List[str],
                     priority_level: str,
                     project_key: str,
                     table_url: str) -> DataIssue:
        """
        Given a title, description, and table key, creates a ticket in the configured project
        Automatically places the table_uri in the description of the ticket.
        Returns the ticket information, including URL.
        :param description: User provided description for the jira ticket
        :param owner_ids: List of user ids that represent the owners of the table
        :param frequent_user_ids: List of user ids that represent the frequent users of the table
        :param priority_level: Priority level for the ticket
        :param project_key: Issue tracking project key to specify where the ticket should be created
        :param table_uri: Table URI ie databasetype://database/table
        :param title: Title of the ticket
        :param table_url: Link to access the table
        :return: A single ticket
        """
        raise NotImplementedError  # pragma: no cover
