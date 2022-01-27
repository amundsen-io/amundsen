# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List
from elasticsearch_dsl import Document, Text, Keyword, RankFeatures, Date, tokenizer, token_filter, Long, Index
from elasticsearch_dsl.analysis import analyzer, Analyzer


general_tokenizer = tokenizer("general_tokenizer",
                              type="char_group",
                              tokenize_on_chars=[
                                  "whitespace",
                                  "_",
                                  "-",
                                  "."
                              ])

stemming_analyzer = analyzer("stemming_analyzer",
                             tokenizer=general_tokenizer,
                             filter=["lowercase", "kstem"])

english_stop = token_filter("english_stop", type="stop", stopwords="_english_")
english_stemmer = token_filter("english_stemmer", type="stemmer", language="english")
english_possessive_stemmer = token_filter("english_possessive_stemmer", type="stemmer", language="possessive_english")

english_analyzer = analyzer("english_analyzer",
                            tokenizer=tokenizer("standard_tokenizer", type="standard"),
                            filter=[
                                english_possessive_stemmer,
                                "lowercase",
                                english_stop,
                                english_stemmer
                            ])

default_analyzers:List[Analyzer]  = [english_analyzer, stemming_analyzer]


class DefaultIndex(Index):
    def __init__(self, name, using="default", analyzers:List[Analyzer]=default_analyzers):
        super().__init__(name, using)
        for analyzer in analyzers:
            self.analyzer(analyzer)
        return self.create()


class SearchableResource(Document):
    key = Keyword(required=True)
    name = Keyword(required=True, analyzer=stemming_analyzer)
    description = Text(analyzer=english_analyzer)
    badges = Keyword(multi=True)
    tags = Keyword(multi=True)
    usage_metrics = RankFeatures(type=Long)
    last_updated_timestamp = Date()


class Table(SearchableResource):
    display_name = Keyword(required=True, analyzer=stemming_analyzer)
    database = Keyword(required=True)
    cluster = Keyword()
    schema = Keyword(required=True, analyzer=stemming_analyzer)
    columns = Keyword(multi=True, analyzer=stemming_analyzer)
    column_descriptions = Text(multi=True, analyzer=english_analyzer)


class Dashboard(SearchableResource):
    group_name = Keyword(required=True, analyzer=stemming_analyzer)
    group_description = Text(analyzer=english_analyzer)
    query_names = Text(multi=True, analyzer=stemming_analyzer)
    chart_names = Text(multi=True, analyzer=stemming_analyzer)


class Feature(SearchableResource):
    feature_group = Keyword(required=True, analyzer=stemming_analyzer)
    version = Keyword(required=True)
    status = Keyword()
    entity = Keyword(multi=True)
    availability = Text()
    

class User(SearchableResource):
    # key is email
    # name is full name, no separate first and last name
    # total read, total own, total follow goes under usage metrics
    pass

RESOURCE_TO_MAPPING: Dict[str, Document] = {
    'table': Table,
    'dashboard': Dashboard,
    'feature': Feature,
    'user': User,
    'base': SearchableResource,
}
