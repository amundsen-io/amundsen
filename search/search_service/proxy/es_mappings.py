# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from elasticsearch_dsl import Document, Date, Keyword, Text, normalizer, Long

column_names_normalizer = normalizer(name_or_instance='column_names_normalizer',
                                     type='custom',
                                     filter=['lowercase'])
lowercase_normalizer = normalizer(name_or_instance='lowercase_normalizer',
                                  type='custom',
                                  char_filter=[],
                                  filter=['lowercase', 'asciifolding'])
feature_lowercase_normalizer = normalizer(name_or_instance='lowercase_normalizer',
                                          type='custom',
                                          char_filter=[],
                                          filter=['lowercase', 'asciifolding'])


class Table(Document):
    name = Text(fields={'raw': Keyword()}, analyzer='simple')
    schema = Text(fields={'raw': Keyword()}, analyzer='simple')
    display_name = Keyword()
    last_updated_timestamp = Date(format='epoch_second')
    description = Text(analyzer='simple')
    column_names = Text(fields={'raw': Keyword(normalizer=column_names_normalizer)},
                        analyzer='simple')
    column_descriptions = Text(analyzer='simple')
    tags = Keyword()
    badges = Keyword()
    cluster = Text(fields={'raw': Keyword()}, analyzer='simple')
    database = Text(fields={'raw': Keyword()}, analyzer='simple')
    key = Keyword()
    total_usage = Long()
    unique_usage = Long()
    programmatic_descriptions = Text(analyzer='simple')


class Dashboard(Document):
    group_name = Text(fields={'raw': Keyword(normalizer=lowercase_normalizer)}, analyzer='simple')
    name = Text(fields={'raw': Keyword(normalizer=lowercase_normalizer)}, analyzer='simple')
    description = Text(fields={'raw': Keyword()}, analyzer='simple')
    group_description = Text(fields={'raw': Keyword()}, analyzer='simple')
    query_names = Text(fields={'raw': Keyword()}, analyzer='simple')
    chart_names = Text(fields={'raw': Keyword()}, analyzer='simple')
    tags = Keyword()
    badges = Keyword()


class User(Document):
    email = Text(fields={'raw': Keyword()}, analyzer='simple')
    first_name = Text(fields={'raw': Keyword()}, analyzer='simple')
    last_name = Text(fields={'raw': Keyword()}, analyzer='simple')
    full_name = Text(fields={'raw': Keyword()}, analyzer='simple')
    total_read = Long()
    total_own = Long()
    total_follow = Long()


class Feature(Document):
    feature_group = Text(fields={'raw': Keyword(normalizer=feature_lowercase_normalizer)},
                         analyzer='simple')
    feature_name = Text(fields={'raw': Keyword(normalizer=feature_lowercase_normalizer)},
                        analyzer='simple')
    version = Keyword(normalizer=feature_lowercase_normalizer)
    key = Keyword()
    total_usage = Long()
    status = Keyword()
    entity = Keyword()
    description = Text()
    availability = Text(fields={'raw': Keyword()}, analyzer='simple')
    tags = Keyword()
    badges = Keyword()
    last_updated_timestamp = Date(format='epoch_second')
