from amundsen_application.models.data_issue import DataIssue
from typing import List, Dict


class IssueResults:
    def __init__(self,
                 issues: List[DataIssue],
                 remaining: int,
                 remaining_url: str) -> None:
        """
        Returns an object representing results from an issue tracker.
        :param issues: Issues in the issue tracker matching the requested table
        :param remaining: How many issues remain in the issue tracker and are not displayed
        :param remaining_url: url to the remaining issues in the issue tracker
        """
        self.issues = issues
        self.remaining = remaining
        self.remaining_url = remaining_url

    def serialize(self) -> Dict:
        return {'issues': [issue.serialize() for issue in self.issues],
                'remaining': self.remaining,
                'remaining_url': self.remaining_url}
