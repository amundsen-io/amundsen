<p align="center">
  <img
    src="https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/logos/amundsen_logo_on_light.svg?sanitize=true"
    alt="Amundsen"
    width="1000"
  />
</p>

<p align="center">
  <a href="https://github.com/amundsen-io/amundsen/blob/master/LICENSE">
    <img src="https://img.shields.io/:license-Apache%202-blue.svg" />
  </a>
  <a href="https://github.com/amundsen-io/amundsen/blob/master/CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" />
  </a>
  <a href="https://github.com/amundsen-io/amundsen/pulse">
    <img src="https://img.shields.io/github/commit-activity/w/amundsen-io/amundsen.svg" />
  </a>
  <a href="https://twitter.com/amundsenio">
    <img src="https://img.shields.io/twitter/follow/amundsenio?label=Follow&style=social" />
  </a>
  <a href="https://join.slack.com/t/amundsenworkspace/shared_invite/enQtNTk2ODQ1NDU1NDI0LTc3MzQyZmM0ZGFjNzg5MzY1MzJlZTg4YjQ4YTU0ZmMxYWU2MmVlMzhhY2MzMTc1MDg0MzRjNTA4MzRkMGE0Nzk">
    <img src="https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social" alt="Slack" />
  </a>
</p>

Amundsen is a data discovery and metadata engine for improving the productivity of data analysts, data scientists and engineers when interacting with data. It does that today by indexing data resources (tables, dashboards, streams, etc.) and powering a page-rank style search based on usage patterns (e.g. highly queried tables show up earlier than less queried tables). Think of it as Google search for data. The project is named after Norwegian explorer [Roald Amundsen](https://en.wikipedia.org/wiki/Roald_Amundsen), the first person to discover the South Pole.

<img
  src="https://raw.githubusercontent.com/lfai/artwork/master/lfai/horizontal/color/lfai-color.png"
  alt="LF AI"
  width="200"
/>

Amundsen is hosted by the [LF AI Foundation](https://lfdl.io)(LF AI). It includes three microservices, one data ingestion library and one common library.

- [amundsenfrontendlibrary](https://github.com/amundsen-io/amundsenfrontendlibrary#amundsen-frontend-service): Frontend service which is a Flask application with a React frontend. <img src="https://img.shields.io/github/commit-activity/w/amundsen-io/amundsenfrontendlibrary.svg" />
- [amundsensearchlibrary](https://github.com/amundsen-io/amundsensearchlibrary#amundsen-search-service): Search service, which leverages Elasticsearch for search capabilities, is used to power frontend metadata searching. <img src="https://img.shields.io/github/commit-activity/w/amundsen-io/amundsensearchlibrary.svg" />
- [amundsenmetadatalibrary](https://github.com/amundsen-io/amundsenmetadatalibrary#amundsen-metadata-service): Metadata service, which leverages Neo4j or Apache Atlas as the persistent layer, to provide various metadata. <img src="https://img.shields.io/github/commit-activity/w/amundsen-io/amundsenmetadatalibrary.svg" />
- [amundsendatabuilder](https://github.com/amundsen-io/amundsendatabuilder#amundsen-databuilder): Data ingestion library for building metadata graph and search index.
Users could either load the data with [a python script](https://github.com/amundsen-io/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py) with the library
or with an [Airflow DAG](https://github.com/amundsen-io/amundsendatabuilder/tree/master/example/dags) importing the library. <img src="https://img.shields.io/github/commit-activity/w/amundsen-io/amundsendatabuilder.svg" />
- [amundsencommon](https://github.com/amundsen-io/amundsencommon): Amundsen Common library holds common codes among microservices in Amundsen. <img src="https://img.shields.io/github/commit-activity/w/amundsen-io/amundsencommon.svg" />

## Homepage
- https://www.amundsen.io/

## Documentation
- https://www.amundsen.io/amundsen/

## Requirements
- Python = 3.6 or 3.7
- Node = v10 or v12 (v14 may have compatibility issues)
- npm >= 6

## User Interface

Please note that the mock images only served as demonstration purpose.

- **Landing Page**: The landing page for Amundsen including 1. search bars; 2. popular used tables;

    ![](https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/landing_page.png)

- **Search Preview**: See inline search results as you type

    ![](https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/search_preview.png)

- **Table Detail Page**: Visualization of a Hive / Redshift table

    ![](https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/table_detail_page_with_badges.png)

- **Column detail**: Visualization of columns of a Hive / Redshift table which includes an optional stats display

    ![](https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/column_details.png)

- **Data Preview Page**: Visualization of table data preview which could integrate with [Apache Superset](https://github.com/apache/incubator-superset) or other Data Visualization Tools.

    ![](https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/data_preview.png)

## Get Involved in the Community

Want help or want to help?
Use the button in our [header](https://github.com/amundsen-io/amundsen#readme) to join our slack channel. Contributions are also more than welcome! As explained in [CONTRIBUTING.md](https://github.com/amundsen-io/amundsen/blob/master/CONTRIBUTING.md) there are many ways to contribute, it does not all have to be code with new features and bug fixes, also documentation, like FAQ entries, bug reports, blog posts sharing experiences etc. all help move Amundsen forward.

## Getting Started

Please visit the Amundsen installation documentation for a [quick start](https://github.com/amundsen-io/amundsen/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker) to bootstrap a default version of Amundsen with dummy data.

## Architecture Overview

Please visit [Architecture](https://github.com/amundsen-io/amundsen/blob/master/docs/architecture.md#architecture) for Amundsen architecture overview.

## Supported Entities
- Tables (from Databases)
- People (from HR systems)
- Dashboards

## Supported Integrations

### Table Connectors
- [Amazon Athena](https://aws.amazon.com/athena/)
- [Amazon Glue](https://aws.amazon.com/glue/) and anything built over it (like Databricks Delta - which is a work in progress).
- [Amazon Redshift](https://aws.amazon.com/redshift/)
- [Apache Cassandra](https://cassandra.apache.org/)
- [Apache Druid](https://druid.apache.org/)
- [Apache Hive](https://hive.apache.org/)
- CSV
- [Google BigQuery](https://cloud.google.com/bigquery)
- [IBM DB2](https://www.ibm.com/analytics/db2)
- [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server/default.aspx)
- [MySQL](https://www.mysql.com/)
- [Oracle](https://www.oracle.com/index.html) (through dbapi or sql_alchemy)
- [PostgreSQL](https://www.postgresql.org/)
- [Presto](https://prestosql.io/)
- [Snowflake](https://www.snowflake.com/)

Amundsen can also connect to any database that provides `dbapi` or `sql_alchemy` interface (which most DBs provide).

### Dashboard Connectors
- [Mode Analytics](https://mode.com/)
- [Redash](https://redash.io/)
- [Tableau](https://tableau.com/)

### ETL Orchestration
- [Apache Airflow](https://airflow.apache.org/)

### BI Viz Tool
- [Apache Superset](https://superset.incubator.apache.org/)


## Installation

Please visit [Installation guideline](https://github.com/amundsen-io/amundsen/blob/master/docs/installation.md) on how to install Amundsen.

## Roadmap

Please visit [Roadmap](https://github.com/amundsen-io/amundsen/blob/master/docs/roadmap.md#amundsen-roadmap) if you are interested in Amundsen upcoming roadmap items.

## Blog Posts and Interviews

- [Amundsen - Lyft's data discovery & metadata engine](https://eng.lyft.com/amundsen-lyfts-data-discovery-metadata-engine-62d27254fbb9) (April 2019)
- [Software Engineering Daily podcast on Amundsen](https://softwareengineeringdaily.com/2019/04/16/lyft-data-discovery-with-tao-feng-and-mark-grover/) (April 2019)
- [How Lyft Drives Data Discovery](https://youtu.be/WVjss62XIG0) (July 2019)
- [Data Engineering podcast on Solving Data Discovery At Lyft](https://www.dataengineeringpodcast.com/amundsen-data-discovery-episode-92/) (Aug 2019)
- [Open Sourcing Amundsen: A Data Discovery And Metadata Platform](https://eng.lyft.com/open-sourcing-amundsen-a-data-discovery-and-metadata-platform-2282bb436234) (Oct 2019)
- [Adding Data Quality into Amundsen with Programmatic Descriptions](https://technology.edmunds.com/2020/05/27/Adding-Data-Quality-into-Amundsen-with-Programmatic-Descriptions/) by [Sam Shuster](https://github.com/samshuster) from [Edmunds.com](https://www.edmunds.com/) (May 2020)
- [Facilitating Data discovery with Apache Atlas and Amundsen](https://medium.com/wbaa/facilitating-data-discovery-with-apache-atlas-and-amundsen-631baa287c8b) by [Mariusz Górski](https://github.com/mgorsk1) from [ING](https://www.ing.com/Home.htm) (June 2020)
- [Using Amundsen to Support User Privacy via Metadata Collection at Square](https://developer.squareup.com/blog/using-amundsen-to-support-user-privacy-via-metadata-collection-at-square/) by [Alyssa Ransbury](https://github.com/alran) from [Square](https://squareup.com/) (July 14, 2020)
- [Amundsen Joins LF AI as New Incubation Project](https://lfai.foundation/blog/2020/08/11/amundsen-joins-lf-ai-as-new-incubation-project/) (Aug 11, 2020)

## Talks

- Disrupting Data Discovery {[slides](https://www.slideshare.net/taofung/strata-sf-amundsen-presentation), [recording](https://www.youtube.com/watch?v=m1B-ptm0Rrw)} (Strata SF, March 2019)
- Amundsen: A Data Discovery Platform from Lyft {[slides](https://www.slideshare.net/taofung/data-council-sf-amundsen-presentation)} (Data Council SF, April 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/markgrover/disrupting-data-discovery)} (Strata London, May 2019)
- ING Data Analytics Platform (Amundsen is mentioned) {[slides](https://static.sched.com/hosted_files/kccnceu19/65/ING%20Data%20Analytics%20Platform.pdf), [recording](https://www.youtube.com/watch?v=8cE9ppbnDPs&t=465) } (Kubecon Barcelona, May 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/PhilippeMizrahi/meetup-sf-amundsen), [recording](https://www.youtube.com/watch?v=NgeCOVjSJ7A)} (Making Big Data Easy SF, May 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/TamikaTannis/neo4j-graphtour-santa-monica-2019-amundsen-presentation-173073727), [recording](https://www.youtube.com/watch?v=Gr3-RfWn49A)} (Neo4j Graph Tour Santa Monica, September 2019)
- Disrupting Data Discovery {[slides](https://www.slideshare.net/secret/56EPbcvswqyH90)} (IDEAS SoCal AI & Data Science Conference, Oct 2019)
- Data Discovery with Amundsen by [Gerard Toonstra](https://twitter.com/radialmind) from Coolblue {[slides](https://docs.google.com/presentation/d/1rkrP8ZobkLPZbwisrLWTdPN5I52SgVGM1eqAFDJXj2A/edit?usp=sharing)} and {[talk](https://www.youtube.com/watch?v=T54EO1MuE7I&list=PLqYhGsQ9iSEq7fDvXcd67iVzx5nsf9xnK&index=17)}  (BigData Vilnius 2019)
- Towards Enterprise Grade Data Discovery and Data Lineage with Apache Atlas and Amundsen by [Verdan Mahmood](https://github.com/verdan) and Marek Wiewiorka from ING {[slides](https://docs.google.com/presentation/d/1FixTTNd1dt_f3PAKhL1KLOeOLsIQq0iFvQA6qlpjIg0/edit#slide=id.p1), [talk](https://bigdatatechwarsaw.eu/agenda/)} (Big Data Technology Warsaw Summit 2020)
- Airflow @ Lyft (which covers how we integrate Airflow and Amundsen) by [Tao Feng](https://github.com/feng-tao) {[slides](https://www.slideshare.net/taofung/airflow-at-lyft-airflow-summit2020) and [website](https://airflowsummit.org/sessions/how-airbnb-twitter-lyft-use-airflow/)} (Airflow Summit 2020)
- Data DAGs with lineage for fun and for profit by [Bolke de Bruin](https://github.com/bolkedebruin) {[website](https://airflowsummit.org/sessions/data-dags-with-lineage/)} (Airflow Summit 2020)

## Related Articles
- [How LinkedIn, Uber, Lyft, Airbnb and Netflix are Solving Data Management and Discovery for Machine Learning Solutions](https://towardsdatascience.com/how-linkedin-uber-lyft-airbnb-and-netflix-are-solving-data-management-and-discovery-for-machine-9b79ee9184bb)
- [Data Discovery in 2020](https://medium.com/@torokyle/data-discovery-in-2020-3c907383caa0)
- [4 Data Trends to Watch in 2020](https://medium.com/memory-leak/4-data-trends-to-watch-in-2020-491707902c09)
- [Work-Bench Snapshot: The Evolution of Data Discovery & Catalog](https://medium.com/work-bench/work-bench-snapshot-the-evolution-of-data-discovery-catalog-2f6c0425616b)
- [Future of Data Engineering](https://www.infoq.com/presentations/data-engineering-pipelines-warehouses/)
- [Governance and Discovery](https://www.oreilly.com/radar/governance-and-discovery/)
- [A Data Engineer’s Perspective On Data Democratization](https://towardsdatascience.com/a-data-engineers-perspective-on-data-democratization-a8aed10f4253?source=friends_link&sk=63638570d03e4145265932c12af33f9d)
- [Graph Technology Landscape 2020](https://graphaware.com/graphaware/2020/02/17/graph-technology-landscape-2020.html)
- [In-house Data Discovery platforms](https://datastrategy.substack.com/p/in-house-data-discovery-platforms)
- [Linux Foundation AI Foundation Landscape](https://landscape.lfai.foundation/)
- [Lyft’s Amundsen: Data-Discovery with Built-In Trust](https://thenewstack.io/lyfts-amundsen-data-discovery-with-built-in-trust/)
- [How to find and organize your data from the command-line](https://towardsdatascience.com/how-to-find-and-organize-your-data-from-the-command-line-852a4042b2be)
- [Data Discovery Platform at Bagelcode](https://medium.com/bagelcode/data-discovery-platform-at-bagelcode-b58a622d17fd)

## Community meetings
Community meetings are held on the first Thursday of every month at 9 AM Pacific, Noon Eastern, 6 PM Central European Time. [Link to join](https://meet.google.com/mqz-ndck-jmj)

### Upcoming meetings & notes
You can the exact date for the next meeting and the agenda a few weeks before the meeting in [this doc](https://docs.google.com/document/d/1bsJWNt1GBFmV-aRbHFuYgMFnMgIIvAmbhsvDatb0Vis).

Notes from all past meetings are available [here](https://docs.google.com/document/d/1bsJWNt1GBFmV-aRbHFuYgMFnMgIIvAmbhsvDatb0Vis).

## Who uses Amundsen?

Here is the list of organizations that are using Amundsen today. If your organization uses Amundsen, please file a PR and update this list.

Currently **officially** using Amundsen:

1. [Asana](https://asana.com/)
1. [Bagelcode](https://site.bagelcode.com/)
1. [Bang & Olufsen](https://www.bang-olufsen.com/en)
1. [Cameo](https://www.cameo.com)
1. [Cimpress Technology](https://cimpress.com)
1. [Coles Group](https://www.colesgroup.com.au/home/)
1. [Data Sprints](https://datasprints.com/)
1. [Dcard](https://www.dcard.tw/)
1. [Devoted Health](https://www.devoted.com/)
1. [Edmunds](https://www.edmunds.com/)
1. [Everfi](https://everfi.com/)
1. [ING](https://www.ing.com/Home.htm)
1. [iRobot](https://www.irobot.com)
1. [LMC](https://www.lmc.eu/cs/)
1. [Lyft](https://www.lyft.com/)
1. [Merlin](https://merlinjobs.com)
1. [PicPay](https://picpay.com.br)
1. [PUBG](https://careers.pubg.com/)
1. [Remitly](https://www.remitly.com/)
1. [Square](https://squareup.com/us/en)
1. [Workday](https://www.workday.com/en-us/homepage.html)

# License
[Apache 2.0 License.](/LICENSE)
