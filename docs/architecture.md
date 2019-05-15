# Architecture

The following diagram shows the overall architecture for Amundsen.
![](img/Amundsen_Architecture.png)

The frontend service serves as web UI portal for users interaction. 
It is Flask-based web app which representation layer is built with React with Redux, Bootstrap, Webpack, and Babel.

The search service leverages Elasticsearch's search functionality and 
provides a RESTful API to serve search requests from the frontend service. 
Currently only [table resources](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/models/elasticsearch_document.py) are indexed and searchable.
The search index is built with the [elasticsearch publisher](https://github.com/lyft/amundsendatabuilder/blob/master/databuilder/publisher/elasticsearch_publisher.py).

The metadata service currently uses a Neo4j proxy to interact with Neo4j graph db and serves frontend service's metadata. 
The metadata is represented as a graph model:
![](img/graph_model.png)
The above diagram shows how metadata is modeled in Amundsen. 
Amundsen provides a [data ingestion library](https://github.com/lyft/amundsendatabuilder) for building the metadata. At Lyft, we build the metadata once a day 
using an Airflow DAG([example](https://github.com/lyft/amundsendatabuilder/blob/master/example/dags/sample_dag.py)).