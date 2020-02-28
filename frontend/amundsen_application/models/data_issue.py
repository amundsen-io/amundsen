
class DataIssue:
    def __init__(self,
                 issue_key: str,
                 title: str,
                 url: str) -> None:
        self.issue_key = issue_key
        self.title = title
        self.url = url

    def serialize(self) -> dict:
        return {'issue_key': self.issue_key,
                'title': self.title,
                'url': self.url}
