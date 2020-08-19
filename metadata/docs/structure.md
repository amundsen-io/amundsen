Amundsen metadata service consists of three packages, API, Entity, and Proxy.

### [API package](https://github.com/amundsen-io/amundsenmetadatalibrary/tree/master/metadata_service/api "API package")
A package that contains [Flask Restful resources](https://flask-restful.readthedocs.io/en/latest/api.html#flask_restful.Resource "Flask Restful resources") that serves Restful API request.
The [routing of API](https://flask-restful.readthedocs.io/en/latest/quickstart.html#resourceful-routing "routing of API") is being registered [here](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/__init__.py#L67 "here").

### [Proxy package](https://github.com/amundsen-io/amundsenmetadatalibrary/tree/master/metadata_service/proxy "Proxy package")
Proxy package contains proxy modules that talks dependencies of Metadata service. There are currently three modules in Proxy package, 
[Neo4j](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/proxy/neo4j_proxy.py "Neo4j"), 
[Statsd](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/proxy/statsd_utilities.py "Statsd")
and [Atlas](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/proxy/atlas_proxy.py "Atlas")

Selecting the appropriate proxy (Neo4j or Atlas) is configurable using a config variable `PROXY_CLIENT`, 
which takes the path to class name of proxy module available [here](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/config.py#L11).

_Note: Proxy's host and port are configured using config variables `PROXY_HOST` and `PROXY_PORT` respectively. 
Both of these variables can be set using environment variables._  

##### [Neo4j proxy module](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/proxy/neo4j_proxy.py "Neo4j proxy module")
[Neo4j](https://neo4j.com/docs/ "Neo4j") proxy module serves various use case of getting metadata or updating metadata from or into Neo4j. Most of the methods have [Cypher query](https://neo4j.com/developer/cypher/ "Cypher query") for the use case, execute the query and transform into [entity](https://github.com/amundsen-io/amundsenmetadatalibrary/tree/master/metadata_service/entity "entity").

##### [Apache Atlas proxy module](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/proxy/atlas_proxy.py "Apache Atlas proxy module")
[Apache Atlas](https://atlas.apache.org/ "Apache Atlas") proxy module serves all of the metadata from Apache Atlas, using [pyatlasclient](https://pyatlasclient.readthedocs.io/en/latest/index.html). 
More information on how to setup Apache Atlas to make it compatible with Amundsen can be found [here](proxy/atlas_proxy.md) 

##### [Statsd utilities module](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/proxy/statsd_utilities.py "Statsd utilities module")
[Statsd](https://github.com/etsy/statsd/wiki "Statsd") utilities module has methods / functions to support statsd to publish metrics. By default, statsd integration is disabled and you can turn in on from [Metadata service configuration](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/config.py "Metadata service configuration").
For specific configuration related to statsd, you can configure it through [environment variable.](https://statsd.readthedocs.io/en/latest/configure.html#from-the-environment "environment variable.")

### [Entity package](https://github.com/amundsen-io/amundsenmetadatalibrary/tree/master/metadata_service/entity "Entity package")
Entity package contains many modules where each module has many Python classes in it. These Python classes are being used as a schema and a data holder. All data exchange within Amundsen Metadata service use classes in Entity to ensure validity of itself and improve readability and mainatability.


## [Configurations](configurations.md)
There are different settings you might want to change depending on the application environment like toggling the debug mode, setting the proxy, and other such environment-specific things.
