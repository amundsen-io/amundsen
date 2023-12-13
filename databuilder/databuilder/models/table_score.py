from typing import List, Union
from datetime import datetime

from databuilder.models.score import Score
from databuilder.models.table_metadata import TableMetadata


class TableScore(Score):
    """
    Table Score model.
    """

    def __init__(self,
                 db_name: str,
                 schema: str,
                 table_name: str,
                 cluster: str,
                 score: float,
                 score_dt: datetime,
                 score_version: str
                 ) -> None:
        self.start_label = TableMetadata.TABLE_NODE_LABEL
        self.start_key = f'{db_name}://{cluster}.{schema}/{table_name}'

        Score.__init__(
            self,
            start_label=self.start_label,
            start_key=self.start_key,
            score=score,
            score_dt=score_dt,
            score_version=score_version
        )
