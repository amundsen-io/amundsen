# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from elasticsearch_dsl import Document, Text, Keyword, analyzer, RankFeatures, Date

class SearchableResource(Document):
    type = Keyword()  # resource type
    key = Keyword(required=True)
    name = Keyword(required=True)
    group = Keyword()  # schema, feature group, dashboard group TODO add analyzer
    source = Keyword()  # db or platform where the resource lives
    description = Text()  # TODO add custom analyzer
    usage_metrics = RankFeatures()  # TODO verify this is correct
    last_updated_timestamp = Date()
    badges = Keyword(multi=True)
    tags = Keyword(multi=True)
    searchable_metadata = Keyword(multi=True)  # TODO maybe for columns, entities, chart names, query names
