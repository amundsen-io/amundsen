# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict

from elasticsearch_dsl import (
    Date, Document, Keyword, RankFeatures, Text, analysis, token_filter, tokenizer,
)

general_tokenizer = tokenizer("general_tokenizer",
                                   type="pattern",
                                   pattern="[^a-zA-Z0-9]")

general_analyzer = analysis.analyzer("general_analyzer",
                                     tokenizer=general_tokenizer,
                                     filter=["lowercase"])

stemming_analyzer = analysis.analyzer("stemming_analyzer",
                                      tokenizer=general_tokenizer,
                                      filter=["lowercase", "kstem"])

english_stop = token_filter("english_stop", type="stop", stopwords="_english_")
english_stemmer = token_filter("english_stemmer", type="stemmer", language="english")
english_possessive_stemmer = token_filter("english_possessive_stemmer",
                                          type="stemmer",
                                          language="possessive_english")

# uses grammar based tokenization before analysis (e.g. "it's fine" -> ["it's", "fine"])
english_analyzer = analysis.analyzer("english_analyzer",
                                     tokenizer=tokenizer("standard_tokenizer",
                                                         type="standard"),
                                     filter=[english_possessive_stemmer,
                                             "lowercase",
                                             english_stop,
                                             english_stemmer])

# tokenizes for words and numbers, removing all other characters before analysis
# (e.g. "it's fine" -> ["it", "s", "fine"] or "hello_word" -> ["hello", "world"])
english_analizer_alphanumeric = analysis.analyzer("english_analyzer",
                                     tokenizer=general_tokenizer,
                                     filter=[english_possessive_stemmer,
                                             "lowercase",
                                             english_stop,
                                             english_stemmer])


class SearchableResource(Document):
# For better understanding of field type rationale read "Mapping unstructured content"
# https://www.elastic.co/guide/en/elasticsearch/reference/current/keyword.html#wildcard-field-type
    key = Text(required=True,
               fields={"keyword": Keyword()},
               analyzer=general_analyzer)
    name = Text(required=True,
                fields={"keyword": Keyword()},
                analyzer=stemming_analyzer)
    description = Text(analyzer=english_analyzer,
                       fields={"alphanumeric": Text(analyzer=english_analizer_alphanumeric)})
    badges = Text(multi=True,
                  fields={"keyword": Keyword()},
                  analyzer=general_analyzer)
    tags = Keyword(multi=True)
    usage = RankFeatures()  # values can be used to boost document search score
    last_updated_timestamp = Date()


class Table(SearchableResource):
    display_name = Text(required=True,
                        fields={"keyword": Keyword()},
                        analyzer=stemming_analyzer)
    database = Text(required=True,
                    fields={"keyword": Keyword()},
                    analyzer=general_analyzer)
    cluster = Text(required=True,
                   fields={"keyword": Keyword()},
                   analyzer=general_analyzer)
    schema = Text(required=True,
                  fields={"keyword": Keyword()},
                  analyzer=stemming_analyzer)
    columns = Text(multi=True,
                   fields={"keyword": Keyword()},
                   analyzer=stemming_analyzer)
    column_descriptions = Text(multi=True,
                               fields={"alphanumeric": Text(analyzer=english_analizer_alphanumeric)},
                               analyzer=english_analyzer)


class Dashboard(SearchableResource):
    group_name = Text(required=True,
                      fields={"keyword": Keyword()},
                      analyzer=stemming_analyzer)
    group_description = Text(analyzer=english_analyzer)
    query_names = Text(multi=True,
                       fields={"keyword": Keyword()},
                       analyzer=stemming_analyzer)
    chart_names = Text(multi=True,
                       fields={"keyword": Keyword()},
                       analyzer=stemming_analyzer)


class Feature(SearchableResource):
    feature_group = Text(required=True,
                         fields={"keyword": Keyword()},
                         analyzer=stemming_analyzer)
    version = Keyword(required=True)
    status = Keyword()
    entity = Text(multi=True,
                  fields={"keyword": Keyword()},
                  analyzer=general_analyzer)
    availability = Keyword()


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
