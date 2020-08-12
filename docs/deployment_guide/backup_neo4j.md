## Neo4j backup and restore
Install the Neo4j APOC plugin (in a folder next to your `example/docker/neo4j/conf/`)

```
  mkdir example/docker/neo4j/plugins
  pushd example/docker/neo4j/plugins
  wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.3.0.4/apoc-3.3.0.4-all.jar
  popd
  mkdir example/backup
```

Add volumes for plugins + backup in amundsen-docker.yml:

```
        volumes:
            - ./example/docker/neo4j/conf:/conf
            - ./example/docker/neo4j/plugins:/plugins
            - ./example/backup:/backup  
  
```

Start containers,

```
Docker-compose -f docker-amundsen.yml up
```

ingest data via Databuilder

In the Amundsen frontend web, change descriptions. Maybe add owners…

In the Neo4j web console

```
CALL apoc.export.cypher.schema('/backup/amundsen_schema.cypher')
CALL apoc.export.graphml.all('/backup/amundsen_data.graphml', {useTypes: true, readLabels: true})
```

Delete the Neo4j graph (still in the Neo4j web console):

```
MATCH (n)
DETACH DELETE n
```

Restore the backup (yep, you guessed it, still in the Neo4j console) :

```
CALL apoc.import.graphml('/backup/amundsen_data.graphml', {useTypes: true, readLabels: true})
```

ToDo:

* Figure out where CLI/cron job should live: as part of metadata - as shell/cron (wrap in airflow) - as Databuilder - as Airflow Operator
* Test volume add works - does not break for non-existing plugin/backup in repo (or add KeepFolder file)
* Check under what circumstances restore of Schema is needed

