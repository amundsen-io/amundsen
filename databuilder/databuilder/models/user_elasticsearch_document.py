import json
from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class UserESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document for user
    """
    def __init__(self,
                 elasticsearch_index,  # type: str
                 elasticsearch_type,   # type: str
                 email,  # type: str
                 first_name,  # type: str
                 last_name,  # type: str
                 name,  # type: str
                 github_username,  # type: str
                 team_name,  # type: str
                 employee_type,  # type: str
                 manager_email,  # type: str
                 slack_id,  # type: str
                 is_active,  # type: bool
                 total_read,  # type: int
                 total_own,  # type: int
                 total_follow,  # type: int
                 ):
        # type: (...) -> None
        self.elasticsearch_index = elasticsearch_index
        self.elasticsearch_type = elasticsearch_type
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.name = name
        self.github_username = github_username
        self.team_name = team_name
        self.employee_type = employee_type
        self.manager_email = manager_email
        self.slack_id = slack_id
        self.is_active = is_active
        self.total_read = total_read
        self.total_own = total_own
        self.total_follow = total_follow

    def to_json(self):
        # type: () -> str
        """
        Convert object to json for elasticsearch bulk upload
        Bulk load JSON format is defined here:
        https://www.elastic.co/guide/en/elasticsearch/reference/6.2/docs-bulk.html
        :return:
        """
        index_row = dict(index=dict(_index=self.elasticsearch_index,
                                    _type=self.elasticsearch_type))
        data = json.dumps(index_row) + "\n"

        # convert rest of the object
        obj_dict = {k: v for k, v in sorted(self.__dict__.items())
                    if k not in ['elasticsearch_index', 'elasticsearch_type']}
        data += json.dumps(obj_dict) + "\n"

        return data
