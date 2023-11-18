# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Any
from enum import Enum

from amundsen_application.models.data_issue import DataIssue
from amundsen_application.models.issue_results import IssueResults

class IssueType(Enum):
    STANDARD = "standard"
    TABLE = "table"
    DASHBOARD = "dashboard"

    def get_issue_type(issue_type: str):
        if IssueType.TABLE.value == issue_type:
            return IssueType.TABLE
        elif IssueType.DASHBOARD.value == issue_type:
            return IssueType.DASHBOARD
        else:
            return IssueType.STANDARD


class BaseIssueTrackerClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_issues(self, uri: str) -> IssueResults:
        """
        Gets issues from the issue tracker
        :param table_uri: Table Uri ie databasetype://database/table
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def create_issue(self,
                     issue_type: IssueType,
                     title: str,
                     description: str,
                     priority_level: str,
                     **kwargs: Any) -> DataIssue:
        """
        Creates an issue by type.  Additional type specific args can be found in kwargs.
        Returns the ticket information, including URL.
        :param issue_type: The type of issue
        :param description: User provided description for the jira ticket
        :param priority_level: Priority level for the ticket
        :param title: Title of the ticket
        :param kwargs: IssueType specific args
        :return: A single ticket
        """
        raise NotImplementedError  # pragma: no cover


