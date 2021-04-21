
# Amundsen Models

## Overview

These are the python classes that live in [databuilder/models/](../databuilder/models/).

Models represent the data structures that live in either neo4j (if the model extends Neo4jSerializable) or in elasticsearch.

Models that extend Neo4jSerializable have methods to create:
- the nodes
- the relationships

In this way, amundsendatabuilder pipelines can create python objects that can then be loaded into neo4j / elastic search
without developers needing to know the internals of the neo4j schema. 

-----

## The Models

### [TableMetadata](../databuilder/models/table_metadata.py)

*What datasets does my org have?*

#### Description
This corresponds to a dataset in amundsen and is the core building block.
In addition to ColumnMetadata, tableMetadata is one of the first datasets you should extract as
almost everything else depends on these being populated. 

#### Extraction
In general, for Table and Column Metadata, you should be able to use one of the pre-made extractors
in the [extractor package](../databuilder/extractor)


### [Watermark](../databuilder/models/watermark.py)

*What is the earliest data that this table has? What is the latest data?*
This is NOT the same as when the data was last updated.

#### Description
Corresponds to the earliest and latest date that a dataset has. Only makes
sense if the dataset is timeseries data.
For example, a given table may have data from 2019/01/01 -> 2020/01/01
In that case the low watermark is 2019/01/01 and the high watermark is 2020/01/01.

#### Extraction
Depending on the datastore of your dataset, you would extract this by:
- a query on the minimum and maximum partition (hive)
- a query for the minimum and maximum record of a given timestamp column


### [ColumnUsageModel](../databuilder/models/column_usage_model.py)

*How many queries is a given column getting? By which users?*

Has query counts per a given column per a user. This can help identify 
#### Description
who uses given datasets so people can contact them if they have questions
on how to use a given dataset or if a dataset is changing. It is also used as a 
search boost so that the most used tables are put to the top of the search results.

For more traditional databases, there should be system tables where you can obtain 
#### Extraction
these sorts of usage statistics.

In other cases, you may need to use audit logs which could require a custom solution.

Finally, for none traditional data lakes, getting this information exactly maybe difficult and you may need to rely
on a heuristic.

### [User](../databuilder/models/user.py)

*What users are there out there? Which team is this user on?*

#### Description
Represents all of the metadata for a user at your company.
This is required if you are going to be having authentication turned on.

#### Extraction
TODO

### [TableColumnStats](../databuilder/models/table_stats.py)

* What are the min/max values for this column? How many nulls are in this column? *

#### Description
This represents statistics on the column level (this is not for table level metrics).
The idea is that different companies will want to track different things about different columns, so this is highly
customizable.
It also will probably require a distributed cluster in order to calculate these regularly and in general is
probably the least accessible metrics to get at without a custom solution.

#### Extraction
The idea here would be to implement something that does the following:
For each table you care about:
For each column you care about:
Calculate statistics that you care about such as min/max/average etc.

### [Application](../databuilder/models/application.py)

* What job/application is writing to this table? *

#### Description
This is used to provide users a way to find out what job/application is responsible for writing to this dataset.
Currently the model assumes the application has to be in airflow, but in theory it could be generalized to other orchestration frameworks.

#### Extraction
TODO

### [Table Owner](../databuilder/models/table_owner.py)

* What team or user owns this dataset? *

#### Description
A dataset can have one or more owners. These owners are used when requesting table descriptions or could be just a useful
point of contact for a user inquiring about how to use a dataset.

#### Extraction
Although the main point of entry for owners is through the WebUI, you could in theory
extract this information based on who created a given table. 


### [Table Source](../databuilder/models/table_source.py)

* Where is the source code for the application that writes to this dataset? *

#### Description
Generally there is going to be code that your company owns that describes how a dataset is created.
This model is what represents the link and type of repository to this source code so it is available to users.

#### Extraction
You will need a github/gitlab/your repository crawler in order to populate this automatically.
The idea there would be to search for a given table name or something else that is a unique identifier such that you can be confident
that the source correctly matches to this table.

### [TableLastUpdated](../databuilder/models/table_last_updated.py)

* When was the last time this data was updated? Is this table stale or deprecated? *

#### Description
This value is used to describe the last time the table had datapoints inserted into it.
It is a very useful value as it can help users identify if there are tables that are no longer being updated.

#### Extraction
There are some extractors available for this like [hive_table_last_updated_extractor](../databuilder/extractor/hive_table_last_updated_extractor.py)
that you can refer to. But you will need access to history that provides information on when the last data write happened on a given table.
If this data isn't available for your data source, you maybe able to approximate it by looking at the max of some timestamp column.  

## Dashboard models
Dashboard models are normalized which means that the model is separated so that it can be easily decoupled with how data is extracted. (If model is denormalized, all metadata is in model, then one extraction needs to able to pull all the data which makes extraction hard and complex) There's trade off in this decision of normalized design where it can be inefficient in the case that some ingestion can be done in one job for metadata source happen to provide all data it need. However, to make model flexible for most of metadata, it is normalized.  


### [DashboardMetadata](../databuilder/models/dashboard/dashboard_metadata.py)

#### Description
A baseline of Dashboard metadata that consists of  dashboard group name, dashboard group description, dashboard description, etc. This model needs to be ingested first as other model builds relation to this.

#### Extraction
[ModeDashboardExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_extractor.py)  


#### [DashboardOwner](../databuilder/models/dashboard/dashboard_owner.py)

#### Description
A model that encapsulate Dashboard's owner. Note that it does not create new user as it has insufficient information about user but it builds relation between User and Dashboard

#### Extraction
[ModeDashboardOwnerExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_owner_extractor.py)  
 

#### [DashboardTable](../databuilder/models/dashboard/dashboard_table.py)
A model that link Dashboard with the tables used in various charts of the dashboard. Note that it does not create new dashboard, table as it has insufficient information but it builds relation between Tables and Dashboard.

Supporting extractor: Currently there's no open sourced extractor for this. In Lyft, there's audit table that records SQL query, where it came from with identifier, along with tables that is used in SQL query. We basically query this table via [DBAPIExtractor](../databuilder/extractor/db_api_extractor.py)

#### [DashboardUsage](../databuilder/models/dashboard/dashboard_usage.py)

#### Description
A model that encapsulate Dashboard usage between Dashboard and User

#### Extraction
You can use [ModeDashboardUsageExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_usage_extractor.py) . However, currently Mode only provides accumulated view count where we need recent view counts (past 30, 60, or 90 days). To get recent view count, in Lyft, we use [ModeDashboardUsageExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_usage_extractor.py) to extract accumulated view count and [GenericLoader](https://github.com/amundsen-io/amundsendatabuilder/blob/master/databuilder/loader/generic_loader.py) to load its record (no publisher here and publisher is not mandatory in DefaultJob) as a event where event materialized as daily snapshot. Once it captures daily accumulated view count, ingest recent view count by querying the datastore. In Lyft, we query via [DBAPIExtractor](../databuilder/extractor/db_api_extractor.py) through Presto.  


#### [DashboardLastModifiedTimestamp](../databuilder/models/dashboard/dashboard_last_modified.py)

#### Description
A model that encapsulate Dashboard's last modified timestamp in epoch

#### Extraction
[ModeDashboardLastModifiedTimestampExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_last_modified_timestamp_extractor.py)   


#### [DashboardExecution](../databuilder/models/dashboard/dashboard_execution.py)
A model that encapsulate Dashboard's execution timestamp in epoch and execution state. Note that this model supports last_execution and last_successful_execution by using [different identifier](../databuilder/models/dashboard/dashboard_execution.py#L23) in the URI.

#### Extraction
[ModeDashboardExecutionsExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_executions_extractor.py) which extracts last_execution.

[ModeDashboardLastSuccessfulExecutionExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_last_successful_executions_extractor.py)  
 

#### [DashboardQuery](../databuilder/models/dashboard/dashboard_query.py)

#### Description
A model that encapsulate Dashboard's query information.

Supporting extractor: [ModeDashboardQueriesExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_queries_extractor.py)

#### [DashboardChart](../databuilder/models/dashboard/dashboard_chart.py)

#### Description
A model that encapsulate Dashboard's charts where chart is associated with query.

#### Extraction
[ModeDashboardChartsExtractor](../databuilder/extractor/dashboard/mode_analytics/mode_dashboard_charts_extractor.py)   
