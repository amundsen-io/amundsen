# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class UserESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document for user
    """

    def __init__(self,
                 email,  # type: str
                 first_name,  # type: str
                 last_name,  # type: str
                 full_name,  # type: str
                 github_username,  # type: str
                 team_name,  # type: str
                 employee_type,  # type: str
                 manager_email,  # type: str
                 slack_id,  # type: str
                 role_name,  # type: str
                 is_active,  # type: bool
                 total_read,  # type: int
                 total_own,  # type: int
                 total_follow,  # type: int
                 ):
        # type: (...) -> None
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name
        self.github_username = github_username
        self.team_name = team_name
        self.employee_type = employee_type
        self.manager_email = manager_email
        self.slack_id = slack_id
        self.role_name = role_name
        self.is_active = is_active
        self.total_read = total_read
        self.total_own = total_own
        self.total_follow = total_follow
