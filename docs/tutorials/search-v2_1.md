# New Amundsen Search

Amundsen Search now has a new API `v2` which supports searching all resources indexed in Amundsen and handles filtered and unfiltered search through the `/v2/search` endpoint as opposed to the old endpoints which were defined per resource. This new API also supports updating documents in Elasticsearch through `/v2/document`. The old endpoints relied on the `ElasticsearchProxy` proxy which doesn't support `v2`. The frontend service has been migrated to the `v2` API, so the old search proxy cannot be used with `amundsen-frontend >= 4.0.0`.
There is `ElasticsearchProxyV2` which supports `v2` and has feature parity with the old API. However this proxy doesn't include any enhancements beyond multi-valued filters with AND/OR logic because further enhancements (like search fuzziness, stemmings, highlighting, etc.)require new mappings to be created by databuilder.
Finally there is `ElasticsearchProxyV2_1`. This latets proxy supports all new search enhacements that rely on new Elasticsearch mappings and it's also accessible throught `/v2/search` and `/v2/document`. This proxy class is configured by default but it will fall back to `ElasticsearchProxyV2` if it cannot find the new mappings in Elasticsearch.

The goal of this tutorial is to explain what the new search functionality offers, how to transition into using `/v2/search` search service endpoint out of the box as well as how to customize it ahead of deprecation of the old search endpoints. The updated search service offers [fuzziness](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness), word [stemming](https://www.elastic.co/guide/en/elasticsearch/reference/8.1/stemming.html), and [boosted search ranking](https://www.elastic.co/guide/en/elasticsearch/reference/8.1/query-dsl-rank-feature-query.html) based on usage.

## Elasticsearch Context

In order for search to function, metadata for all searchable resources configured is indexed into Elasticsearch with a databuilder task and then Elasticsearch is queried via the search service. In Elasticsearch there are two main concepts that are fundamental to understanding how search works, [mappings](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) and [search queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html). Mappings define how fields are indexed into Elasticsearch by specifying the types of fields and how text fields are analyzed. The queries should then be written with the mapping in mind since there certain field types are required to perform certain types of queries efficiently.

## Transitioning to `/v2/search`

In order to ensure a smooth transition from our previous search functionality to a version which supports these new features follow these steps:

### Index Metadata to Elasticsearch Using New Mappings
1. Bump to `amundsen-databuilder >= 6.8.0`
2. Configure [SearchMetadatatoElasticsearchTask](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/search_metadata_to_elasticsearch_task.py)
    - Make sure to configure it using a different index alias. So for example if previously the configuration for writing new ES indices was **(A)** for this task **(B)** must be configured instead for each resource.
        **(A)** `ELASTICSEARCH_ALIAS_CONFIG_KEY → table_search_index`
        **(B)** `ELASTICSEARCH_ALIAS_CONFIG_KEY → table_search_index_v2_1`
    - This way the previous index is preserved and the new index aliases have the [new mappings](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/document_mappings.py) that enable all of the functionality mentioned above.
    - Note this task will use the mappings already provided in this file and default queries to extract metadata from neo4j. Elasticsearch mappings can be customized by extending the mapping classes and configuring the task to use the custom mapping via `MAPPING_CLASS`
Queries to extract metadata from neo4j can be customized and configured through `CYPHER_QUERY_CONFIG_KEY`.
3. Run the task.
4. Verify that your ES mappings match the [new mapping definitions](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/task/search/document_mappings.py) by running this directly on Elasticsearch.
    - `GET new_table_search_index`

### Configuring the Search Service

1. Bump to `amundsen-search >= 4.0.0`
2. Configure the [Elasticsearch ES_PROXY_CLIENT to use ELASTICSEARCH_V2_1](https://github.com/amundsen-io/amundsen/blob/main/search/search_service/config.py#L18), which is enabled by default in the latest version of search unless configured differently.
    - You can customize the search query by providing a custom client. You can create your own client by extending the class from `es_proxy_v2_1.py` (ex: `class MyESClient(ElasticsearchProxyV2_1):`) and overwritting any of the functions provided to change the query.
3. (OPTIONAL) If the alias your new mappings are indexed under differs from `{resource}_search_index_v2_1` make sure to configure the correct string template by adding `ES_ALIAS_TEMPLATE = 'my_{resource}_search_index_alias'` to the config with your custom alias name.

### Use the latest version of Frontend
1. Make sure you are using `amundsen-frontend >= 4.0.0` which calls the search service `/v2/search` endpoint. 