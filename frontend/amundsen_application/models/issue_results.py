# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from amundsen_application.models.data_issue import DataIssue
from typing import Dict, List, Optional


class IssueResults:
    def __init__(self,
                 issues: List[DataIssue],
                 total: int,
                 all_issues_url: str,
                 open_issues_url: Optional[str] = '',
                 closed_issues_url: Optional[str] = '',
                 open_count: Optional[int] = 0) -> None:
        """
        Returns an object representing results from an issue tracker.
        :param issues: Issues in the issue tracker matching the requested table
        :param total: How many issues in all are associated with this table
        :param all_issues_url: url to the all issues in the issue tracker
        :param open_issues_url: url to the open issues in the issue tracker
        :param closed_issues_url: url to the closed issues in the issue tracker
        :param open_count: How many open issues are associated with this table
        """
        self.issues = issues
        self.total = total
        self.all_issues_url = all_issues_url
        self.open_issues_url = open_issues_url
        self.closed_issues_url = closed_issues_url
        self.open_count = open_count

    def serialize(self) -> Dict:
        return {'issues': [issue.serialize() for issue in self.issues],
                'total': self.total,
                'all_issues_url': self.all_issues_url,
                'open_issues_url': self.open_issues_url,
                'closed_issues_url': self.closed_issues_url,
                'open_count': self.open_count}
