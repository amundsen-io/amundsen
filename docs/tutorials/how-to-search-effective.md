# Getting Stated with Amundsen Search

The goal of this tutorial is to provide more context into the search service. This will explain how the service functions out of the box as well as how to customize it.

## Overview

In order for search to function metadata for all searchable resources is indexed into Elasticsearch with a databuilder task and then Elasticsearch is queried via the search service. In Elasticsearch there are two main concepts that are fundamental to understanding how search works, [mappings](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) and [search queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html). Mappings define how fields are indexed into Elasticsearch by specifying the types of fields and how text fields are analyzed. The queries should then be written with the mapping in mind since there certain field types are required to perform certain types of queries efficiently.

## Indexing Search Metadata to Elastc

By default, [search_metadata_to_elasticsearch_task](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/search_metadata_to_elasticsearch_task.py)

** 2 opts for customization **
