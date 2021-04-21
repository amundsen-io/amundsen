# Atlas search investigation
There are several approaches to integrate searching within [Apache Atlas](https://atlas.apache.org/ "Apache Atlas"), we describe multiple options below:

- Use REST API's

Directly using the Atlas API's is quick to implement and easy to setup for administrators. Atlas uses a search engine 
underwater (embedded Solr) to perform search queries, thus in theory this method should scale up. Disadvantages are that 
we are limited to the REST api that Atlas offers, we could potentially add functionality via pull requests and extend 
the search capabilities. The [advanced search](https://atlas.apache.org/Search-Advanced.html "Apache Atlas Advanced Search") 
provides a DSL which contains basic forms of aggregation and arithmetic.

- Use Data Builder to fill Elasticsearch from Atlas

Adopting Atlas within the Data Builder to fill Elasticsearch is a relatively straightforward way of staying 
compatible with the Neo4j database. It could either be pulling data from Atlas or being pushed by Kafka. This method
requires a setup of Elasticsearch and Airflow, which increases the amount of infrastructure and maintenance. 
Another disadvantage is that with a big inflow of metadata this method might not scale as well as the other methods. 

- Use underlying Solr or Elasticsearch from Apache Atlas

Within Atlas there is the possibility to open up either Solr or the experimental Elasticsearch. It depends on janusgraph
(the behind the scenes graph database) which populates the search engine. Therefore the search engine would not be compatible with 
the data builder setup. Adoption of such a search engine would require either new queries, some kind of transformer 
within the search engine, or changes within Atlas itself.  

## Discussion
Both the REST API approach and the data builder approach can be implemented and be configurable. Both approaches have 
their own benefits, the data builder together provides a more fine-tuned search whereas the Atlas REST API comes out 
of the box with Atlas. The last approach of using the underlying search engine from Atlas provides direct access
to all the meta data with a decent search API. However, integration would be less straight forward as the indexes would
differ from the data builders search engine loader.


The focus is initially to implement the REST API approach and afterwards potentially implement an Atlas data extractor 
and importer within the Amundsen Data Builder. So that administrators have more flexibility in combining data sources.
