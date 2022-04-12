# Getting Stated with Amundsen Search

The goal of this tutorial is to provide more context into the search service. This will explain how the service functions out of the box as well as how to customize it.

## Overview

In order for search to function metadata for all searchable resources is indexed into Elasticsearch with a databuilder task and then Elasticsearch is queried via the search service. In Elasticsearch there are two main concepts that are fundamental to understanding how search works, [mappings](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) and [search queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html). Mappings define how fields are indexed into Elasticsearch by specifying the types of fields and how text fields are analyzed. The queries should then be written with the mapping in mind since there certain field types are required to perform certain types of queries efficiently.

## Indexing Search Metadata to Elastc

The [search_metadata_to_elasticsearch_task](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/search_metadata_to_elasticsearch_task.py) extracts metadata from your database of choice and publishes it to Elasticsearch. The [default mappings](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/document_mappings.py) defined here for each resource we support come with some standard [english language text analysis](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-lang-analyzer.html#english-analyzer) for fields like descriptions. They also support [text stemming](https://www.elastic.co/guide/en/elasticsearch/reference/current/stemming.html) which reduces works to their root to support finding similar terms like stemming the words `rides` or `rideable` to `ride` so all these words are indexed the same. Another field that can be pretty useful in search ranking is usage, which for every resource uses a [RankFeatures](https://www.elastic.co/guide/en/elasticsearch/reference/current/rank-features.html) numeric field.

### Metadata Query and Mappings Customization

There are 2 important customization which can be made on the metadata extraxction and indexing step. The first is the query used to extract metadata from the your database, and the second is the class which defines your mappings.
For the metadata query you can utilize the default queries and add extra fields by setting the given placeholder variables `publish_tag_filter`, `additional_field_match`, `usage_fields` and `additional_field_return` or just write a new query altogether configure your task using this new query. It is important that the field names defined here match fields in the mappings class.
The mapping class can be customized as well. You can either extend the existing classes to add or overwrite fields, add new analizers, subfields, change field types, etc. Or you can write an entirely new class which extends the [elasticsearch_dsl](https://elasticsearch-dsl.readthedocs.io/en/latest/#) library's `Document` class.


Note the query uses the analyzers defined on the mappings by default so for exampleit will stem the query term if the field being searched is stemmed.
** 2 opts for customization **
