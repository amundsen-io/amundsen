# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from amundsen_application.models.data_issue import DataIssue
from typing import List, Dict


class IssueResults:
    def __init__(self,
                 issues: List[DataIssue],
                 total: int,
                 open_count: int,
                 all_issues_url: str,
                 open_issues_url: str,
                 closed_issues_url: str) -> None:
        """
        Returns an object representing results from an issue tracker.
        :param issues: Issues in the issue tracker matching the requested table
        :param total: How many issues in all are associated with this table
        :param open_count: How many open issues are associated with this table
        :param all_issues_url: url to the all issues in the issue tracker
        :param open_issues_url: url to the open issues in the issue tracker
        :param closed_issues_url: url to the closed issues in the issue tracker
        """
        self.issues = issues
        self.total = total
        self.open_count = open_count
        self.all_issues_url = all_issues_url
        self.open_issues_url = open_issues_url
        self.closed_issues_url = closed_issues_url

    def serialize(self) -> Dict:
        return {'issues': [issue.serialize() for issue in self.issues],
                'total': self.total,
                'open_count': self.open_count,
                'all_issues_url': self.all_issues_url,
                'open_issues_url': self.open_issues_url,
                'closed_issues_url': self.closed_issues_url}
