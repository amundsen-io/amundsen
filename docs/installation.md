# Installation

## Bootstrap a default version of Amundsen using Docker
The following instructions are for setting up a version of Amundsen using Docker.

1. Install `docker` and  `docker-compose`.
2. Clone [this repo](https://github.com/lyft/amundsen) and its submodules by running:
   ```bash
   $ git clone --recursive git@github.com:lyft/amundsen.git
   ```
3. Enter the cloned directory and run:
    ```bash
    $ docker-compose -f docker-amundsen.yml up
    ```
4. Ingest dummy data into Neo4j by doing the following:
   * Change directory to the [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder) submodule.
   * Run the following commands in the `amundsendatabuilder` upstream directory:
   ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate  
    $ pip3 install -r requirements.txt
    $ python3 setup.py install
    $ python3 example/scripts/sample_data_loader.py
   ```
5. View UI at [`http://localhost:5000`](http://localhost:5000) and try to search `test`, it should return some result.

### Verify setup

1. You can verify dummy data has been ingested into Neo4j by by visiting [`http://localhost:7474/browser/`](http://localhost:7474/browser/) and run `MATCH (n:Table) RETURN n LIMIT 25` in the query box. You should see two tables:
   1. `hive.test_schema.test_table1`
   2. `dynamo.test_schema.test_table2`
2. You can verify the data has been loaded into the metadataservice by visiting:
   1. [`http://localhost:5000/table_detail/gold/hive/test_schema/test_table1`](http://localhost:5000/table_detail/gold/hive/test_schema/test_table1)
   2. [`http://localhost:5000/table_detail/gold/dynamo/test_schema/test_table2`](http://localhost:5000/table_detail/gold/dynamo/test_schema/test_table2)

### Troubleshooting

1. If the docker container doesn't have enough heap memory for Elastic Search, `es_amundsen` will fail during `docker-compose`.
   1. docker-compose error: `es_amundsen | [1]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]`
   2. Increase the heap memory [detailed instructions here](https://www.elastic.co/guide/en/elasticsearch/reference/7.1/docker.html#docker-cli-run-prod-mode)
      1. Edit `/etc/sysctl.conf`
      2. Make entry `vm.max_map_count=262144`. Save and exit.
      3. Reload settings `$ sysctl -p`
      4. Restart `docker-compose`
