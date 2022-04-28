# Amundsen Search V2

The goal of this tutorial is to explain what search v2 offers, how to transition into using `v2/search` out of the box as well as how to customize it ahead of deprecation of the old elasticsearch proxy.

## Overview

Amundsen search v2 supports [fuzziness](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness), word [stemming](https://www.elastic.co/guide/en/elasticsearch/reference/8.1/stemming.html), and [boosted search ranking](https://www.elastic.co/guide/en/elasticsearch/reference/8.1/query-dsl-rank-feature-query.html) based on usage. In order for search to function, metadata for all searchable resources configured is indexed into Elasticsearch with a databuilder task and then Elasticsearch is queried via the search service. In Elasticsearch there are two main concepts that are fundamental to understanding how search works, [mappings](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) and [search queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html). Mappings define how fields are indexed into Elasticsearch by specifying the types of fields and how text fields are analyzed. The queries should then be written with the mapping in mind since there certain field types are required to perform certain types of queries efficiently.

## Transitioning to Search V2

Search v2 is accessible by using the endpoint `/v2/search` on the search service. In order to ensure a smooth transition from our previous search functionality to a version which supports these new features follow these steps:

### Index Metadata to Elasticsearch Using New Mappings
1. Bump to `amundsen-databuilder >= 6.7.5`
2. Configure [SearchMetadatatoElasticsearchTask](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/search_metadata_to_elasticsearch_task.py)
    - Make sure to configure it using a different index alias. So for example if previously the configuration for writing new ES indices was **(A)** for this task **(B)** must be configured instead for each resource.
        **(A)** `ELASTICSEARCH_ALIAS_CONFIG_KEY → table_search_index`
        **(B)** `ELASTICSEARCH_ALIAS_CONFIG_KEY → new_table_search_index`
    - This way the previous index is preserved and the new index aliases have the [new mappings](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/document_mappings.py) that enable all of the functionality mentioned above.
    - Note this task will use the mappings already provided in this file and default queries to extract metadata from neo4j. Elasticsearch mappings can be customized by extending the mapping classes and configuring the task to use the custom mapping via `MAPPING_CLASS`
Queries to extract metadata from neo4j can be customized and configured through `CYPHER_QUERY_CONFIG_KEY`.
3. Run the task.
4. Verify that your ES mappings match the [new mapping definitions](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/document_mappings.py) by running this directly on Elasticsearch.
    - `GET new_table_search_index`

### Configuring the Search Service
1. Bump to `amundsen-search >= 4.0.0`
2. Configure the [Elasticsearch PROXY_CLIENT_KEY to use ELASTICSEARCH_V2](https://github.com/amundsen-io/amundsen/blob/main/search/search_service/config.py#L18), which is enabled by default in the latest version of search unless configured differently.
    - You can customize the search query by providing a custom client. You can cereate one client by extending the class from `es_search_proxy.py` (ex: `class MyESClient(ElasticsearchProxy):`) and overwritting any of the functions provided to change the query.
### Using the latest version of Frontend
1. Make sure you are using `amundsen-frontend >= 4.0.0` which calls `/v2/search`. 