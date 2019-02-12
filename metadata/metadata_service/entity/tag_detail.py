class TagDetail:

    def __init__(self, *,
                 tag_name: str,
                 tag_count: int) -> None:
        self.tag_name = tag_name
        self.tag_count = tag_count

    def __repr__(self) -> str:
        return """Tag(tag_name={!r}, tag_count={!r})"""\
               .format(self.tag_name, self.tag_count)
