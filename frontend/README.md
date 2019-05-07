# Amundsen

[![PyPI version](https://badge.fury.io/py/amundsen-frontend.svg)](https://badge.fury.io/py/amundsen-frontend)
[![Build Status](https://api.travis-ci.com/lyft/amundsenfrontendlibrary.svg?branch=master)](https://travis-ci.com/lyft/amundsenfrontendlibrary)
[![Coverage Status](https://img.shields.io/codecov/c/github/lyft/amundsenfrontendlibrary/master.svg)](https://codecov.io/github/lyft/amundsenfrontendlibrary?branch=master)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://bit.ly/2FVq37z)

Amundsen is a metadata driven application for improving the productivity of data analysts, data scientists and engineers when interacting with data. It does that today by indexing data resources (tables, dashboards, streams, etc.) and powering a page-rank style search based on usage patterns (e.g. highly queried tables show up earlier than less queried tables). Think of it as Google search for data. The project is named after Norwegian explorer [Roald Amundsen](https://en.wikipedia.org/wiki/Roald_Amundsen), the first person to discover South Pole.

It includes three microservices and a data ingestion library.
- [amundsenfrontendlibrary](https://github.com/lyft/amundsenfrontendlibrary): Frontend service which is a Flask application with a React frontend.
- [amundsensearchlibrary](https://github.com/lyft/amundsensearchlibrary): Search service, which leverages Elasticsearch for search capabilities, is used to power frontend metadata searching.
- [amundsenmetadatalibrary](https://github.com/lyft/amundsenmetadatalibrary): Metadata service, which leverages Neo4j or Apache Atlas as the persistent layer, to provide various metadata.
- [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder): Data ingestion library for building metadata graph and search index. 
Users could either load the data with [a python script](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py) with the library
or with an [Airflow DAG](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/sample_dag.py) importing the library.


## Requirements
- Python >= 3.4
- Node = v8.x.x or v10.x.x (v11.x.x has compatibility issues)
- npm >= 6.x.x

## User Interface

Please note that the mock images only served as demonstration purpose.

- **Landing Page**: The landing page for Amundsen including 1. search bars; 2. popular used tables;
    
    ![](docs/img/landing_page.png)
    
- **Table Detail Page**: Visualization of a Hive / Redshift table
    
    ![](docs/img/table_detail_page.png)
    
- **Column detail**: Visualization of columns of a Hive / Redshift table which includes an optional stats display
    
    ![](docs/img/column_details.png)
    
- **Data Preview Page**: Visualization of table data preview which could integrate with [Apache Superset](https://github.com/apache/incubator-superset)
    
    ![](docs/img/data_preview.png)

## Get Involved in the Community

Want help or want to help? 
Use the button in our [header](https://github.com/lyft/amundsenfrontendlibrary#amundsen) to join our slack channel. Please join our [mailing list](https://groups.google.com/forum/#!forum/amundsen-dev) as well.

## Getting started

Please visit the Amundsen documentation for help with [installing Amundsen](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docs/installation.md#install-standalone-application-directly-from-the-source) 
and getting a [quick start](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker) with dummy data 
or an [overview of the architecture](docs/architecture.md).

## Architecture Overview

Please visit [Architecture](docs/architecture.md) for Amundsen architecture overview.

## Installation

Please visit [Installation guideline](docs/installation.md) on how to install Amundsen.

## Configuration

Please visit [Configuration doc](docs/configuration.md) on how to configure Amundsen various enviroment settings(local vs production).

## Developer Guidelines

Please visit [Developer guidelines](docs/developer_guide.md) if you want to build Amundsen in your local environment.

## Roadmap

Please visit [Roadmap](docs/roadmap.md) if you are interested in Amundsen upcoming roadmap items.

## Publications
- [Disrupting Data Discovery](https://www.slideshare.net/taofung/strata-sf-amundsen-presentation) (Strata SF 2019)
- [Amundsen - Lyft's data discovery & metadata engine](https://eng.lyft.com/amundsen-lyfts-data-discovery-metadata-engine-62d27254fbb9) (Lyft engineering blog)
- [Amundsen: A Data Discovery Platform from Lyft](https://www.slideshare.net/taofung/data-council-sf-amundsen-presentation) (Data council 19 SF)
- [Software Engineering Daily podcast on Amundsen](https://softwareengineeringdaily.com/2019/04/16/lyft-data-discovery-with-tao-feng-and-mark-grover/) (April 2019)
- [Disrupting Data Discovery](https://www.slideshare.net/markgrover/disrupting-data-discovery) (Strata London 2019)

# License
[Apache 2.0 License.](/LICENSE)
