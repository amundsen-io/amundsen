from datetime import datetime  # noqa: F401


class FileMetadata(object):

    def __init__(self,
                 path,  # type: str
                 last_updated,  # type: datetime
                 size  # type: int
                 ):
        # type: (...) -> None
        self.path = path
        self.last_updated = last_updated
        self.size = size

    def __repr__(self):
        # type: () -> str
        return """FileMetadata(path={!r}, last_updated={!r}, size={!r})""" \
            .format(self.path, self.last_updated, self.size)
