# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


class PrestoQueryLogs:
    """
    Presto Query logs model.
    Sql result has one row per presto query.
    """

    def __init__(self,
                 user: str,
                 query_text: str,
                 occurred_at: str
                 ) -> None:
        self.user = user
        self.query_text = query_text
        self.occurred_at = occurred_at
