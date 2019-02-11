class PrestoQueryLogs:
    """
    Presto Query logs model.
    Sql result has one row per presto query.
    """
    def __init__(self,
                 user,  # type: str
                 query_text,  # type: str
                 occurred_at  # type: str
                 ):
        # type: (...) -> None
        self.user = user
        self.query_text = query_text
        self.occurred_at = occurred_at
