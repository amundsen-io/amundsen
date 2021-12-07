# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Union

from databuilder.models.follower import Follower
from databuilder.models.table_metadata import TableMetadata


class TableFollower(Follower):
    """
    Table follower model.
    """

    def __init__(self,
                 db_name: str,
                 schema: str,
                 table_name: str,
                 followers: Union[List, str],
                 cluster: str = 'gold',
                 ) -> None:
        self.start_label = TableMetadata.TABLE_NODE_LABEL
        self.start_key = f'{db_name}://{cluster}.{schema}/{table_name}'

        Follower.__init__(
            self,
            start_label=self.start_label,
            start_key=self.start_key,
            follower_emails=followers,
        )
