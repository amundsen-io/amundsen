# Overview

Amundsen's data preview feature requires that developers create a custom implementation of `base_preview_client` for requesting that data. This feature assists with data discovery by providing the end user the option to view a sample of the actual resource data so that they can verify whether or not they want to transition into exploring that data, or continue their search.

[Redash](https://github.com/getredash/redash) is an open-source business intelligence tool that can be used for data exploration. This document provides some insight into how to configure Amundsen's frontend application to leverage Redash for data previews.

## Implementation

You will need to complete the following steps to use Redash to serve your Amundsen data preview:

1. Create a query template in Redash
2. Generate an API key in Redash for Authentication
3. Create a custom `RedashPreviewClient` class
4. Update your `setup.py` and re-install the Amundsen frontend

### 1. Creating a query template in Redash

In order for Amundsen to execute a query through Redash the query must already exist and be saved in Redash. Redash allows queries to be built using parameters and Amundsen uses these parameters to inject the `{schema}.{table}` into the query. When defining a new query the following SQL should be used:

```sql
select {{ SELECT_FIELDS }}
from {{ SCHEMA_NAME }}.{{ TABLE_NAME }}
{{ WHERE_CLAUSE }}
limit {{ RCD_LIMIT }}
```

Visit the [Redash documentation on query parameters](https://redash.io/help/user-guide/querying/query-parameters) for more information on how query templating works.

### 2. Generate an API key in Redash for Authentication

Redash uses API keys for authentication. While there are two types of API keys that Redash supports (User API keys and Query specific API keys), the Amundsen integration requires a User API key. The Query API keys do not support the dynamic templating that is required to build the queries.

The API key used by Amundsen must have access to query the underlying table in Redash. By default, only a single API key is required for your Redash Preview Client in Amundsen. However, you may have different databases in Redash that require different access. The Redash Preview Client allows you to dynamically select which API key to use for authentication in the event you want more fine-grained control over your data preview access.

To select an API key on the fly based off of the database, cluster, schema and table that is being queried, override the `_get_query_api_key` function (see [using parameters](#using-params-to-lookup-resources)] below for an example).

### 3. Create a custom `RedashPreviewClient` class

The file [`base_redash_preview_client`](https://github.com/lyft/amundsenfrontendlibrary/tree/master/amundsen_application/base/base_redash_preview_client.py) provides two examples for implementing the Redash preview client.

- One [simple implementation](../../amundsen_application/base/base_redash_preview_client.py#L38) that only implements the minimal requirements: a User API key and a way to look up which Redash query ID to execute
- One [complex implementation](../../amundsen_application/base/base_redash_preview_client.py#L61) which uses a different API key per query, increases the # of records returned to 100, reduces the max cache time in Redash to 1 hour, provides custom field masking in the query and creates custom where clauses for specific tables to filter the correct data returned to the preview client.

#### Using params to lookup resources

Several of the functions in `BaseRedashPreviewClient` have a single input: **params** and expect a single output (e.g. a query ID, query API key, custom where clause, etc.). These params are a dictionary that contain the following fields:

```json
{
    "database": "snowflake",
    "cluster": "ca_covid",
    "schema": "open_data",
    "tableName": "statewide_cases"
}
```

It is expected that these values can generally be used to uniquely reference your resources. For example, if you have two databases `snowflake.ca_covid` and `snowflake.marketing` the implementation to find the correct query ID may look like:

```python
    ...

    def get_redash_query_id(self, params: Dict) -> Optional[int]:
        SOURCE_DB_QUERY_MAP = {
            'snowflake.open_data': 1,
            'snowflake.marketing': 27,
        }
        database = params['database']
        cluster = params['cluster']
        db_cluster_key = f'{database}.{cluster}'
        return SOURCE_DB_QUERY_MAP.get(db_cluster_key)

```

This same paradigm applies to the all funcitons with the same input signature: `get_redash_query_id`, `_get_query_api_key`, `get_select_fields`, and `get_where_clause`.

### 4. Update setup.py and reinstall Amundsen

In the `setup.py` at the root of this repo, add a `[preview_client]` group and point the `table_preview_client_class` to your custom class.

```python
entry_points="""
    ...

    [preview_client]
    table_preview_client_class = amundsen_application.base.examples.example_redash_preview_client:RedashSimplePreviewClient
"""
```

Run `python3 setup.py install` in your virtual environment and restart the application for the entry point changes to take effect.
