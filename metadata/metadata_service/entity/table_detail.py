from typing import Iterable, Optional


class User:
    def __init__(self, *,
                 email: str,
                 first_name: str =None,
                 last_name: str =None) -> None:
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self) -> str:
        return 'User(email={!r}, first_name={!r}, last_name={!r})'.format(self.email, self.first_name, self.last_name)


class Reader:
    def __init__(self, *,
                 user: User,
                 read_count: int) -> None:
        self.user = user
        self.read_count = read_count

    def __repr__(self) -> str:
        return 'Reader(user={!r}, read_count={!r})'.format(self.user, self.read_count)


class Tag:
    def __init__(self, *,
                 tag_type: str,
                 tag_name: str) -> None:
        self.tag_name = tag_name
        self.tag_type = tag_type

    def __repr__(self) -> str:
        return 'Tag(tag_name={!r}, tag_type={!r})'.format(self.tag_name,
                                                          self.tag_type)


class Watermark:
    def __init__(self, *,
                 watermark_type: str =None,
                 partition_key: str =None,
                 partition_value: str =None,
                 create_time: str =None) -> None:
        self.watermark_type = watermark_type
        self.partition_key = partition_key
        self.partition_value = partition_value
        self.create_time = create_time

    def __repr__(self) -> str:
        return 'Watermark(watermark_type={!r}, ' \
               'partition_key={!r}, ' \
               'partition_value={!r}, ' \
               'create_time={!r}))'.format(self.watermark_type,
                                           self.partition_key,
                                           self.partition_value,
                                           self.create_time)


class Statistics:
    def __init__(self, *,
                 stat_type: str,
                 stat_val: str =None,
                 start_epoch: int =None,
                 end_epoch: int =None) -> None:
        self.stat_type = stat_type
        self.stat_val = stat_val
        self.start_epoch = start_epoch
        self.end_epoch = end_epoch

    def __repr__(self) -> str:
        return 'Statistics(stat_type={!r}, ' \
               'stat_val={!r},' \
               'start_epoch={!r},' \
               'end_epoch={!r})'.format(self.stat_type,
                                        self.stat_val,
                                        self.start_epoch,
                                        self.end_epoch)


class Column:
    def __init__(self, *,
                 name: str,
                 description: Optional[str],
                 col_type: str,
                 sort_order: int,
                 stats: Iterable[Statistics] =()) -> None:
        self.name = name
        self.description = description
        self.col_type = col_type
        self.sort_order = sort_order
        self.stats = stats

    def __repr__(self) -> str:
        return 'Column(name={!r}, description={!r}, col_type={!r}, sort_order={!r}, stats={!r})'\
            .format(self.name,
                    self.description,
                    self.col_type,
                    self.sort_order,
                    self.stats)


class Application:
    def __init__(self, *,
                 application_url: str,
                 description: str,
                 id: str,
                 name: str) -> None:
        self.application_url = application_url
        self.description = description
        self.name = name
        self.id = id

    def __repr__(self) -> str:
        return 'Application(application_url={!r}, description={!r}, name={!r}, id={!r})'\
            .format(self.application_url, self.description, self.name, self.id)


class Source:
    def __init__(self, *,
                 source_type: str,
                 source: str) -> None:
        self.source_type = source_type
        self.source = source

    def __repr__(self) -> str:
        return 'Source(source_type={!r}, ' \
               'source={!r})'.format(self.source_type,
                                     self.source)


class Table:
    def __init__(self, *,
                 database: str,
                 cluster: str,
                 schema: str,
                 name: str,
                 tags: Iterable[Tag] =(),
                 table_readers: Iterable[Reader] = (),
                 description: Optional[str] = None,
                 columns: Iterable[Column],
                 owners: Iterable[User] = (),
                 watermarks: Iterable[Watermark] = (),
                 table_writer: Optional[Application] = None,
                 last_updated_timestamp: Optional[int],
                 source: Optional[Source] = None,
                 is_view: Optional[bool] = None,
                 ) -> None:

        self.database = database
        self.cluster = cluster
        self.schema = schema
        self.name = name
        self.tags = tags
        self.table_readers = table_readers
        self.description = description
        self.columns = columns
        self.owners = owners
        self.watermarks = watermarks
        self.table_writer = table_writer
        self.last_updated_timestamp = last_updated_timestamp
        self.source = source
        self.is_view = is_view or False

    def __repr__(self) -> str:
        return """Table(database={!r}, cluster={!r}, schema={!r}, name={!r}, tags={!r}, table_readers={!r},
                        description={!r}, columns={!r}, owners={!r}, watermarks={!r}, table_writer={!r},
                        last_updated_timestamp={!r}, source={!r}, is_view={!r})"""\
            .format(self.database, self.cluster,
                    self.schema, self.name, self.tags,
                    self.table_readers, self.description,
                    self.columns, self.owners, self.watermarks,
                    self.table_writer, self.last_updated_timestamp,
                    self.source, self.is_view)
