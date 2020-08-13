# Amundsen Deployment Guide

Amundsen allows for considerable flexibility and configurability of deployment. This document is a step-by-step guide to get a fully customized enterprise deployment of Amundsen.

Intended audience: engineers at organizations intending to install Amundsen, possibly with multiple individuals responsible for its maintenance. If you're an individual evaluating Amundsen, read the [installation guide instead](../installation.md), it will be much simpler.



The structure of this guide is:
* **Source Control:** getting a git repository set up that contains your custom code
* **Basic install of services:** Running the core services running on your infrastructure
* **Ingestion configuration:** Configuring Databuilder to connect to other parts of your infrastructure.
* **Configuration of services:** Configuring the front-end for your organization
* **Security:** Enabling authentication
* **Ops:** Backup and Restore, Monitoring, Upgrades


Note: this guide is being actively developed, and will have some rough edges. If you run into trouble, please post on the #troubleshooting channel in Slack!

# Install
## Source Control

All Amundsen installs require some code configuration, thus it's impossible to deploy premade packages. This guide describes how to set up a repository to allow for this without losing your sanity: [source control guide](./source_control.md)

All other steps of this guide assume you're using this organization of git.


## Basic install of services

We recommend deploying via Docker. We've included Kubernetes files to make this easier.

TODO: recommend forking docker-compose into custom/ , since we don't want the vendored version. 


### databuilder

databuilder is a library, not a service. It does not handle scheduling on its own, thus you're responsible for orchestrating its runs. Airflow is a popular method of deploying, but you could also do a simple cron.

TODO: link to describing doing an Airflow deploy (should live in Databuilder repo) of a dummy extractor

### Front-end

TODO: describe how to build a plain dockerfile without modifications, include in Docker compose


### neo4j

TODO: desribe docker deploy for this, how to debug


### metadata and search

TODO: describe docker for this, should be light


## Configuration of services

### Databuilder

###

# Ops

## Backup

You need to back-up your primary data store:
* [Read the guide for Neo4j](./backup_neo4j.md)
* Atlas is out-of-scope, but you should back it up per that project's recommendations

You do not need to back-up ElasticSearch for durability: its content can be generated from the primary data store easily (TODO: is this actually true? If so, include doc for how to do this)


## Upgrades

TODO:
* Databuilder - upgrade pip package
* metadata and search - update docker-compose image
* frontend - pull code from remote repo, rebuild


TODO: how to coordinate versions?


## Monitoring

TODO
