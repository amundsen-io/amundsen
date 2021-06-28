# Query Metadata Guide

This document provides guidance on how to ingest query metadata and query composition metadata into Amundsen.

Query metadata and query composition metadata consists of four parts:

 1. `QueryMetadata`: This represents a query
 2. `QueryExecutionsMetadata`: This is an aggregation, representing the number of times a given query was executed wtihin an hour, day, week, etc.
 3. `QueryJoinMetadata`: Represents a join between two columns
 4. `QueryWhereMetadata`: Represents a whereclause used in a query, this may be associated to one or more columns and tables

The `QueryExecutionsMetadata`, `QueryJoinMetadata`, `QueryWhereMetadata` and `QueryMetadata` can be seen here:

![Query Assets](./assets/query-assets.png?raw=true "Query Assets")

Amundsen uses `QueryExecutionsMetadata` to determine time-sensitive relevance. As new `QueryExecutionsMetadata` are added and old ones are removed, Amundsen is able to continue to keep the most recent queries and the related joins and wheres relevant.

Since `QueryMetadata` can be related to `QueryExecutionsMetadata`, `QueryJoinMetadata` and `QueryWhereMetadata`, a single extractor is used to ingest these objects into Amundsen.
