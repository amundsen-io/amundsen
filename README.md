<img
  src="docs/img/logos/amundsen_logo_on_light.svg"
  alt="Amundsen"
  width="500"
/>

[![License](http://img.shields.io/:license-Apache%202-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://join.slack.com/t/amundsenworkspace/shared_invite/enQtNTk2ODQ1NDU1NDI0LTc3MzQyZmM0ZGFjNzg5MzY1MzJlZTg4YjQ4YTU0ZmMxYWU2MmVlMzhhY2MzMTc1MDg0MzRjNTA4MzRkMGE0Nzk)

Amundsen is a metadata driven application for improving the productivity of data analysts, data scientists and engineers when interacting with data. It does that today by indexing data resources (tables, dashboards, streams, etc.) and powering a page-rank style search based on usage patterns (e.g. highly queried tables show up earlier than less queried tables). Think of it as Google search for data. The project is named after Norwegian explorer [Roald Amundsen](https://en.wikipedia.org/wiki/Roald_Amundsen), the first person to discover the South Pole.

It includes three microservices, one data ingestion library and one common library.
- [amundsenfrontendlibrary](https://github.com/lyft/amundsenfrontendlibrary#amundsen-frontend-service): Frontend service which is a Flask application with a React frontend.
- [amundsensearchlibrary](https://github.com/lyft/amundsensearchlibrary#amundsen-search-service): Search service, which leverages Elasticsearch for search capabilities, is used to power frontend metadata searching.
- [amundsenmetadatalibrary](https://github.com/lyft/amundsenmetadatalibrary#amundsen-metadata-service): Metadata service, which leverages Neo4j or Apache Atlas as the persistent layer, to provide various metadata.
- [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder#amundsen-databuilder): Data ingestion library for building metadata graph and search index.
Users could either load the data with [a python script](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py) with the library
or with an [Airflow DAG](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/sample_dag.py) importing the library.
- [amundsencommon](https://github.com/lyft/amundsencommon): Amundsen Common library holds common codes among microservices in Amundsen.


## Requirements
- Python >= 3.4 (AmundsenDatabuilder: Python >= 2.7.x)
- Node = v10 or v12 (v14 may have compatibility issues)
- npm >= 6

## User Interface

Please note that the mock images only served as demonstration purpose.

- **Landing Page**: The landing page for Amundsen including 1. search bars; 2. popular used tables;

    ![](docs/img/landing_page.png)

- **Search Preview**: See inline search results as you type

    ![](docs/img/search_preview.png)

- **Table Detail Page**: Visualization of a Hive / Redshift table

    ![](docs/img/table_detail_page_with_badges.png)

- **Column detail**: Visualization of columns of a Hive / Redshift table which includes an optional stats display

    ![](docs/img/column_details.png)

- **Data Preview Page**: Visualization of table data preview which could integrate with [Apache Superset](https://github.com/apache/incubator-superset)

    ![](docs/img/data_preview.png)

## Get Involved in the Community

Want help or want to help?
Use the button in our [header](https://github.com/lyft/amundsen#amundsen) to join our slack channel. Please join our [mailing list](https://groups.google.com/forum/#!forum/amundsen-dev) as well.

## Powered By

Here is the list of organizations that are using Amundsen today. If your organization uses Amundsen, please file a PR and update this list.

Currently **officially** using Amundsen:

1. [Bang & Olufsen](https://www.bang-olufsen.com/en)
1. [Cameo](https://www.cameo.com)
1. [Cimpress Technology](https://cimpress.com)
1. [Data Sprints](https://datasprints.com/)
1. [Edmunds](https://www.edmunds.com/)
1. [Everfi](https://everfi.com/)
1. [ING](https://www.ing.com/Home.htm)
1. [iRobot](https://www.irobot.com)
1. [LMC](https://www.lmc.eu/cs/)
1. [Lyft](https://www.lyft.com/)
1. [Merlin](https://merlinjobs.com)
1. [Remitly](https://www.remitly.com/)
1. [Square](https://squareup.com/us/en)
1. [Workday](https://www.workday.com/en-us/homepage.html)

## Getting Started

Please visit the Amundsen installation documentation for a [quick start](https://github.com/lyft/amundsen/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker) to bootstrap a default version of Amundsen with dummy data.

## Architecture Overview

Please visit [Architecture](docs/architecture.md#architecture) for Amundsen architecture overview.

## Supported connectors
Amundsen supports two kinds of "nodes" in its graph today:
- Tables (from Databases)
- People (from HR systems)

Amundsen can connect to any database that provides `dbapi` or `sql_alchemy` interface (which most DBs provide).
The databases we see most frequently used in the community are:
- Hive and anything that works with Hive metastore (Spark SQL, Presto, Athena, etc.)
- BigQuery
- PostgreSQL and anything that uses the same interface (Redshift)
- Snowflake
- Amazon Glue and anything built over it (like Databricks Delta - which is a work in progress).

## Installation

Please visit [Installation guideline](docs/installation.md) on how to install Amundsen.

## Roadmap

Please visit [Roadmap](docs/roadmap.md#amundsen-roadmap) if you are interested in Amundsen upcoming roadmap items.

## Blog Posts and Interviews

- [Amundsen - Lyft's data discovery & metadata engine](https://eng.lyft.com/amundsen-lyfts-data-discovery-metadata-engine-62d27254fbb9) (April 2019)
- [Software Engineering Daily podcast on Amundsen](https://softwareengineeringdaily.com/2019/04/16/lyft-data-discovery-with-tao-feng-and-mark-grover/) (April 2019)
- [How Lyft Drives Data Discovery](https://youtu.be/WVjss62XIG0) (July 2019)
- [Data Engineering podcast on Solving Data Discovery At Lyft](https://www.dataengineeringpodcast.com/amundsen-data-discovery-episode-92/) (Aug 2019)
- [Open Sourcing Amundsen: A Data Discovery And Metadata Platform](https://eng.lyft.com/open-sourcing-amundsen-a-data-discovery-and-metadata-platform-2282bb436234) (Oct 2019)

## Talks

- Disrupting Data Discovery {[slides](https://www.slideshare.net/taofung/strata-sf-amundsen-presentation), [video](https://www.youtube.com/watch?v=m1B-ptm0Rrw)} (Strata SF, March 2019)
- Amundsen: A Data Discovery Platform from Lyft {[slides](https://www.slideshare.net/taofung/data-council-sf-amundsen-presentation)} (Data Council SF, April 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/markgrover/disrupting-data-discovery)} (Strata London, May 2019)
- ING Data Analytics Platform (Amundsen is mentioned) {[slides](https://static.sched.com/hosted_files/kccnceu19/65/ING%20Data%20Analytics%20Platform.pdf), [video](https://www.youtube.com/watch?v=8cE9ppbnDPs&t=465) } (Kubecon Barcelona, May 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/PhilippeMizrahi/meetup-sf-amundsen), [video](https://www.youtube.com/watch?v=NgeCOVjSJ7A)} (Making Big Data Easy SF, May 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/TamikaTannis/neo4j-graphtour-santa-monica-2019-amundsen-presentation-173073727), [video](https://www.youtube.com/watch?v=Gr3-RfWn49A)} (Neo4j Graph Tour Santa Monica, September 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/secret/56EPbcvswqyH90)} (IDEAS SoCal AI & Data Science Conference, Oct 2019)
- Data Discovery with Amundsen by [Gerard Toonstra](https://twitter.com/radialmind) from Coolblue {[slides](https://docs.google.com/presentation/d/1rkrP8ZobkLPZbwisrLWTdPN5I52SgVGM1eqAFDJXj2A/edit?usp=sharing)} and {[talk](https://www.youtube.com/watch?v=T54EO1MuE7I&list=PLqYhGsQ9iSEq7fDvXcd67iVzx5nsf9xnK&index=17)}  (BigData Vilnius 2019)

## Community meetings
Join slack to find out about our next virtual community meetings. Notes:
- [2020/01/23](https://docs.google.com/document/d/1MT3qd_YjFiA17en94IEZcWaEgjdcaLhhZb-mX1UyWF8/edit#) {[video](https://www.youtube.com/watch?v=HV6ChWv4-ZQ)}
- [2019/11/05](https://docs.google.com/document/d/11CLWhyNHlNoOxs6Ee29UJz0m8yI3Xiw4tUNTFGx_vy4/edit#heading=h.8d2zgr1chrra)
- [2019/09/05](https://docs.google.com/document/d/1l2yIpoMmTGY022yuDHWWkSJVSuK25dYlwX0GWff6eQg/edit#)
- [2019/07/30](https://docs.google.com/document/d/1JzoLlXUGrwnGirlGUmNCHFhzMXYcR2KrUokLsRHKacs/edit#heading=h.3nxnevt7nz9)

# License
[Apache 2.0 License.](/LICENSE)
