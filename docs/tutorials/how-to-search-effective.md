# Getting Stated with Amundsen Search

The goal of this tutorial is to provide more context into the search service. This will explain how the service functions out of the box as well as how to customize it.

## Overview

In order for search to function metadata for all searchable resources is indexed into Elasticsearch with a databuilder task and then Elasticsearch is queried via the search service.

## Indexing Search Metadata to Elastc

The [search_metadata_to_elasticsearch_task](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/search_metadata_to_elasticsearch_task.py)

** 2 opts for customization **
