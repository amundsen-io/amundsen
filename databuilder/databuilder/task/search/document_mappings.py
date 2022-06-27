# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict

from elasticsearch_dsl import (
    Date, Document, Keyword, MetaField, RankFeatures, Text, analysis, token_filter, tokenizer,
)

POSITIONS_OFFSETS = "with_positions_offsets"


class Tokenizer:
    # separate tokens on all non-alphanumeric characters and whitespace
    alphanum_tokenizer = tokenizer("alphanum_tokenizer",
                                   type="pattern",
                                   pattern="[^a-zA-Z0-9]")


class Filter:
    english_stop = token_filter("english_stop", type="stop", stopwords="_english_")

    # uses default porter stemmer
    english_stemmer = token_filter("english_stemmer", type="stemmer", language="english")

    english_possessive_stemmer = token_filter("english_possessive_stemmer",
                                              type="stemmer",
                                              language="possessive_english")


class Analyzer:
    # tokenizes and makes the tokens lowercase
    general_analyzer = analysis.analyzer("general_analyzer",
                                         tokenizer=Tokenizer.alphanum_tokenizer,
                                         filter=["lowercase"])

    # provides light stemming for english tokens
    stemming_analyzer = analysis.analyzer("stemming_analyzer",
                                          tokenizer=Tokenizer.alphanum_tokenizer,
                                          filter=["lowercase", "kstem"])

    # uses grammar based tokenization before analysis (e.g. "it's fine" -> ["it's", "fine"])
    english_analyzer = analysis.analyzer("english_analyzer",
                                         tokenizer=tokenizer("standard_tokenizer",
                                                             type="standard"),
                                         filter=[Filter.english_possessive_stemmer,
                                                 "lowercase",
                                                 Filter.english_stop,
                                                 Filter.english_stemmer])

    # tokenizes for words and numbers, removing all other characters before analysis
    # (e.g. "it's fine" -> ["it", "s", "fine"] or "hello_word" -> ["hello", "world"])
    alphanum_analyzer = analysis.analyzer("alphanum_analyzer",
                                          tokenizer=Tokenizer.alphanum_tokenizer,
                                          filter=[Filter.english_possessive_stemmer,
                                                  "lowercase",
                                                  Filter.english_stop,
                                                  Filter.english_stemmer])


class Subfield:
    # combinations of field types and analyzers for additional index time analysis

    keyword = Keyword()

    alphanumeric = Text(analyzer=Analyzer.alphanum_analyzer,
                        term_vector=POSITIONS_OFFSETS)

    alphanumeric_multi = Text(multi=True,
                              analyzer=Analyzer.alphanum_analyzer,
                              term_vector=POSITIONS_OFFSETS)

    general = Text(analyzer=Analyzer.general_analyzer,
                   term_vector=POSITIONS_OFFSETS)

    general_multi = Text(multi=True,
                         analyzer=Analyzer.general_analyzer,
                         term_vector=POSITIONS_OFFSETS)

    @staticmethod
    def get_ngram_subfield(field_name: str,
                           multi: bool = False,
                           min_shingle_size: int = 2,
                           max_shingle_size: int = 5,
                           token_separator: str = ' ') -> Text:

        # using shingle token filter for word level ngrams
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-shingle-tokenfilter.html
        shingle_filter = token_filter(f"shingle_filter_{field_name}",
                                      type="shingle",
                                      output_unigrams=True,
                                      min_shingle_size=min_shingle_size,
                                      max_shingle_size=max_shingle_size,
                                      token_separator=token_separator)

        ngram_analyzer = analysis.analyzer(f"ngram_analyzer_{field_name}",
                                           tokenizer=Tokenizer.alphanum_tokenizer,
                                           filter=[shingle_filter])

        return Text(multi=multi,
                    analyzer=ngram_analyzer,
                    term_vector=POSITIONS_OFFSETS)


# Resource Mappings

# Note: the current analyzers don't support tokenizing on camelcase text, if this is a requirement extend
# these classes and write a custom analyzer
# https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-pattern-analyzer.html


class SearchableResource(Document):
    # For better understanding of field type rationale read "Mapping unstructured content"
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/keyword.html#wildcard-field-type
    key = Text(required=True,
               fields={"keyword": Subfield.keyword},
               analyzer=Analyzer.general_analyzer,
               term_vector=POSITIONS_OFFSETS)
    name = Text(required=True,
                fields={
                    "keyword": Subfield.keyword,
                    "general": Subfield.general,
                    "ngram": Subfield.get_ngram_subfield(
                        field_name="resource_name",
                        max_shingle_size=8
                    )
                },
                analyzer=Analyzer.stemming_analyzer,
                term_vector=POSITIONS_OFFSETS)
    description = Text(analyzer=Analyzer.english_analyzer,
                       fields={
                           "alphanumeric": Subfield.alphanumeric,
                           "general": Subfield.general
                       },
                       term_vector=POSITIONS_OFFSETS)
    badges = Text(multi=True,
                  fields={"keyword": Subfield.keyword},
                  analyzer=Analyzer.general_analyzer,
                  term_vector=POSITIONS_OFFSETS)
    tags = Text(multi=True,
                fields={"keyword": Subfield.keyword},
                analyzer=Analyzer.general_analyzer,
                term_vector=POSITIONS_OFFSETS)
    usage = RankFeatures()
    last_updated_timestamp = Date()
    resource_type = Keyword(required=True)

    class Meta:
        meta = MetaField({'version': 2})


class Table(SearchableResource):
    # overwrite table name because it requires a different ngram subfield
    name = Text(required=True,
                fields={
                    "keyword": Subfield.keyword,
                    "general": Subfield.general,
                    "ngram": Subfield.get_ngram_subfield(
                        field_name="table_name",
                        max_shingle_size=8,
                        token_separator="_"
                    )
                },
                analyzer=Analyzer.stemming_analyzer,
                term_vector=POSITIONS_OFFSETS)
    columns = Text(multi=True,
                   fields={
                       "keyword": Subfield.keyword,
                       "general": Subfield.general_multi,
                       "ngram": Subfield.get_ngram_subfield(
                           field_name="table_columns",
                           multi=True,
                           token_separator="_")
                   },
                   term_vector=POSITIONS_OFFSETS,
                   analyzer=Analyzer.stemming_analyzer)
    display_name = Text(required=True,
                        fields={"keyword": Subfield.keyword},
                        analyzer=Analyzer.general_analyzer,
                        term_vector=POSITIONS_OFFSETS)
    database = Text(required=True,
                    fields={
                        "keyword": Subfield.keyword
                    },
                    analyzer=Analyzer.general_analyzer,
                    term_vector=POSITIONS_OFFSETS)
    cluster = Text(required=True,
                   fields={
                       "keyword": Subfield.keyword
                   },
                   analyzer=Analyzer.general_analyzer,
                   term_vector=POSITIONS_OFFSETS)
    schema = Text(required=True,
                  fields={
                      "keyword": Subfield.keyword,
                      "general": Subfield.general
                  },
                  analyzer=Analyzer.stemming_analyzer,
                  term_vector=POSITIONS_OFFSETS)
    column_descriptions = Text(multi=True,
                               fields={
                                   "alphanumeric": Subfield.alphanumeric_multi,
                                   "general": Subfield.general_multi
                               },
                               analyzer=Analyzer.english_analyzer,
                               term_vector=POSITIONS_OFFSETS)


class Dashboard(SearchableResource):
    group_name = Text(required=True,
                      fields={
                          "keyword": Subfield.keyword,
                          "general": Subfield.general
                      },
                      analyzer=Analyzer.stemming_analyzer,
                      term_vector=POSITIONS_OFFSETS)
    group_description = Text(analyzer=Analyzer.english_analyzer,
                             term_vector=POSITIONS_OFFSETS)
    query_names = Text(multi=True,
                       fields={
                           "keyword": Subfield.keyword,
                           "general": Subfield.general_multi,
                           "ngram": Subfield.get_ngram_subfield(
                               field_name="dashboard_query",
                               multi=True
                           )
                       },
                       analyzer=Analyzer.stemming_analyzer,
                       term_vector=POSITIONS_OFFSETS)
    chart_names = Text(multi=True,
                       fields={
                           "keyword": Subfield.keyword,
                           "general": Subfield.general_multi,
                           "ngram": Subfield.get_ngram_subfield(
                               field_name="dashboard_chart",
                               multi=True
                           )
                       },
                       analyzer=Analyzer.stemming_analyzer,
                       term_vector=POSITIONS_OFFSETS)


class Feature(SearchableResource):
    feature_group = Text(required=True,
                         fields={
                             "keyword": Subfield.keyword,
                             "general": Subfield.general_multi
                         },
                         analyzer=Analyzer.stemming_analyzer,
                         term_vector=POSITIONS_OFFSETS)
    version = Keyword(required=True)
    status = Keyword()
    entity = Text(multi=True,
                  fields={"keyword": Subfield.keyword},
                  analyzer=Analyzer.general_analyzer,
                  term_vector=POSITIONS_OFFSETS)
    availability = Keyword()


class User(SearchableResource):
    # key is email
    # name is full name, no separate first and last name
    # total read, total own, total follow goes under usage metrics
    first_name = Text(required=True,
                      fields={
                          "keyword": Keyword(),
                          "general": Subfield.general
                      },
                      analyzer=Analyzer.stemming_analyzer,
                      term_vector=POSITIONS_OFFSETS)
    last_name = Text(required=True,
                     fields={
                         "keyword": Keyword(),
                         "general": Subfield.general
                     },
                     analyzer=Analyzer.stemming_analyzer,
                     term_vector=POSITIONS_OFFSETS)


RESOURCE_TO_MAPPING: Dict[str, Document] = {
    'table': Table,
    'dashboard': Dashboard,
    'feature': Feature,
    'user': User,
    'base': SearchableResource,
}
