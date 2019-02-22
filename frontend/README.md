# Amundsen

Amundsen is a data discovery portal to make data more discoverable. The project named after Norwegian explorer [Roald Amundsen](https://en.wikipedia.org/wiki/Roald_Amundsen) collects and displays
metadata about various data resources such as Hive and Redshift tables.

It includes three microservices and a data ingestion library.
- [amundsenfrontendlibrary](https://github.com/lyft/amundsenfrontendlibrary): Frontend service which is a Flask application with a React frontend.
- [amundsensearchsearchlibrary](https://github.com/lyft/amundsensearchlibrary): Search service, which leverages Elasticsearch for search capabilities, is used to power frontend metadata searching.
- [amundsenmetadatalibrary](https://github.com/lyft/amundsenmetadatalibrary): Metadata service, which leverages Neo4j as the persistent layer, to provide various metadata.
- [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder): Data ingestion library for building metadata graph and search index. 
Users could either load the data with [a python script](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py) with the library
or with an [Airflow DAG](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/sample_dag.py) importing the library.


**TODO: Insert images and GIFs**

## Requirements
- Python >= 3.4

## Architecture Overview

[Architecture](docs/architecture.md)

## Installation

[Installation guideline](docs/installation.md)

## Configuration

[Configuration doc](docs/configuration.md)

## Developer Guide

[Developer guideline](docs/developer_guide.md)

## Roadmap

[Roadmap](docs/roadmap.md)

# License
[Apache 2.0 License.](/LICENSE)
