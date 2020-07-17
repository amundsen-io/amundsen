# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

# JIRA SDK does not return priority beyond the name
PRIORITY_MAP = {
    'Blocker': 'P0',
    'Critical': 'P1',
    'Major': 'P2',
    'Minor': 'P3'
}


class DataIssue:
    def __init__(self,
                 issue_key: str,
                 title: str,
                 url: str,
                 status: str,
                 priority: str) -> None:
        self.issue_key = issue_key
        self.title = title
        self.url = url
        self.status = status
        if priority in PRIORITY_MAP:
            self.priority_display_name = PRIORITY_MAP[priority]
            self.priority_name = priority.lower()
        else:
            self.priority_display_name = None  # type: ignore
            self.priority_name = None  # type: ignore

    def serialize(self) -> dict:
        return {'issue_key': self.issue_key,
                'title': self.title,
                'url': self.url,
                'status': self.status,
                'priority_name': self.priority_name,
                'priority_display_name': self.priority_display_name}
