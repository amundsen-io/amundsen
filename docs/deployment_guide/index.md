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

All other steps of this guide assume you're using this git schema.


## Basic install of services

We recommend deploying via Docker. We've included Kubernetes files to make this easier. Read the 

## Ingestion configuration

TODO: Airflow

## Configuration of services

# Ops

## Backup

You need to back-up your primary data store:
* [Read the guide for Neo4j](./backup_neo4j.md)
* Atlas is out-of-scope, but you should back it up per that project's recommendations

You do not need to back-up ElasticSearch for durability: its content can be generated from the primary data store easily.


## Upgrades

TODO 

## Monitoring

TODO
