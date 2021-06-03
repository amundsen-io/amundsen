# Atlas search investigation

There are several approaches to integrate searching within [Apache Atlas](https://atlas.apache.org/ "Apache Atlas"), we describe multiple options below:

## Use Data Builder to fill Elasticsearch from Atlas

Atlas search data extractor can be used to synchronize Atlas with Elasticsearch. This method requires you to:

- deploy Elasticsearch
- register a process that synchronizes the data between Atlas and Elasticsearch

We suggest using Elasticsearch as backend for Atlas janusgraph (it's possible with latest Atlas version) and additionally sync data with databuilder
to have indices compatible with Amundsen Elasticsearch Search Proxy. 

Mixing Atlas Metadata Proxy with Elasticsearch Search Proxy is 100% safe and fully compatible.

Raw janusgraph indices are not compatible with Amundsen Elasticsearch Search Proxy and it would require implementing custom class over Elasticsearch Search Proxy.

**This is preferred way of handling Amundsen search.**

### Advantages

- The performance is 10-20x better (verified on production environment)
- Possibility to search on many fields at the same time (and defining importance of each field)
- Much better and flexible relevancy scoring

### Disadvantages

- Requires additional component (Elasticsearch) if Apache Solr is used for Atlas search backend
- Requires scheduling (cron, airflow, kubernetes cron job) of databuilder app to synchronize the data periodically
- The data in Elasticsearch is as fresh as frequent syncing app - there might be misalignment between Atlas Metadata and Elasticsearch index

## Use Atlas REST API

Directly using the Atlas API's is quick to implement and easy to setup for administrators. Atlas uses a search engine 
behind the scenes (Solr and Elasticsearch are fully supported) to perform search queries.

### Advantages

- Quicker way to achieve Amundsen <> Atlas integration
- Data in search is available as soon as it's indexed in Atlas
- Simpler setup (less components/applications)

### Disadvantages

- Atlas Search API is very limited in terms of multi-field search and relevancy tuning
- Atlas Search API has suboptimal performance and doesn't really leverage underlying full text engine (it's heavily abstracted by janusgraph) 
- Amundsen AtlasProxy for search might be lagging in features as it's not as popular as Elasticsearch Proxy

## Discussion

Both the REST API approach and the data builder approach can be configurable. Both approaches have 
their own benefits, the data builder together provides a more fine-tuned search whereas the Atlas REST API comes out 
of the box with Atlas.

The focus was initially to implement the REST API approach but after several months on production we decided to introduce
Atlas search data extractor and use Elasticsearch Proxy for Amundsen search. It proved to be much more robust and flexible solution. 
The disadvantages were quickly eclipsed by advantages.
