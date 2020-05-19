# FAQ

## How to select between Neo4j and Atlas as backend for Amundsen?

### Why Neo4j?
1. Amundsen has direct influence over the data model if you use neo4j. This, at least initially, will benefit the speed by which new features in amundsen can arrive
2. Atlas is developed with data governance in mind and not with data discovery. You could view "slapping amundsen on top of Atlas" as a kind of Frankenstein: never able to properly able to cater to your audience
3. Atlas seems to have a slow development cycle and it's community is not very responsive although some small improvements have been made
4. Atlas has the "Hadoop" era "smell" which isn't considered very sexy nowadays
5. Neo4j for it is the market leader in Graph database and also was proven by Airbnb’s Data portal on their Data discovery tool.

### Why Atlas?
1. Atlas has lineage support already available. It's been tried and tested.
2. Tag propagation is supported
3. It has a robust authentication and authorization system
4. Atlas does data governance adding amundsen for discovery makes it best of both worlds
5. It has support for push based due to its many plugins
6. The free version of Neo4j does not have authorization support(Enterprise version does). Your question should actually be why use "neo4j over janusgraph" cause that is the right level of comparison. Atlas adds a whole bunch on top of the graph database.

##  What are the prerequisites to use Apache Atlas as backend for Amundsen?
To run Amundsen with Atlas, latest versions of following components should be used:
1. [Apache Atlas](https://github.com/apache/atlas/) - built from `master` branch. Ref [`103e867cc126ddb84e64bf262791a01a55bee6e5`](https://github.com/apache/atlas/commit/103e867cc126ddb84e64bf262791a01a55bee6e5) (or higher).
2. [amundsenatlastypes](https://pypi.org/project/amundsenatlastypes/) - library for installing Atlas entity definitions specific to Amundsen integration. Version `1.1.0` (or higher).

## How to migrate from Amundsen 1.x -> 2.x?

v2.0 renames a handful of fields in the services to be more consistent. Unfortunately one side effect is that the 2.0 versions of the services will need to be deployed simultaneously, as they are not interoperable with the 1.x versions.

Additionally, some indexed field names in the elasticsearch document change as well, so if you're using elasticsearch, you'll need to republish Elasticsearch index via Databuilder job.

The data in the metadata store, however, can be preserved when migrating from 1.x to 2.0.

v2.0 deployments consists of deployment of all three services along with republishing Elasticsearch document on Table with v2.0 Databuilder.

Keep in mind there is likely to be some downtime as v2.0.0, between deploying 3 services and re-seeding the elasticsearch indexes, so it might be ideal to stage a rollout by datacenter/environment if uptime is key
