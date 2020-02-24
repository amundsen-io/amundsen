# FAQ

## Service version guide
### Amundsen 1.x -> 2.x Migration Guide:

v2.0 renames a handful of fields in the services to be more consistent. Unfortunately one side effect is that the 2.0 versions of the services will need to be deployed simultaneously, as they are not interoperable with the 1.x versions.

Additionally, some indexed field names in the elasticsearch document change as well, so if you're using elasticsearch, you'll need to republish Elasticsearch index via Databuilder job.

The data in the metadata store, however, can be preserved when migrating from 1.x to 2.0.

v2.0 deployments consists of deployment of all three services along with republishing Elasticsearch document on Table with v2.0 Databuilder.

Keep in mind there is likely to be some downtime as v2.0.0, between deploying 3 services and re-seeding the elasticsearch indexes, so it might be ideal to stage a rollout by datacenter/environment if uptime is key

