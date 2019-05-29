# Installation

## Install standalone application directly from the source

The following instructions are for setting up a standalone version of the Amundsen application. This approach is ideal for local development.
```bash
# Clone repo
$ git clone https://github.com/lyft/amundsenfrontendlibrary.git

# Build static content
$ cd amundsenfrontendlibrary/amundsen_application/static
$ npm install
$ npm run build # or npm run dev-build for un-minified source
$ cd ../../

# Install python resources
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements3.txt
$ python3 setup.py install

# Start server
$ python3 amundsen_application/wsgi.py
# visit http://localhost:5000 to confirm the application is running
```

You should now have the application running at http://localhost:5000, but will notice that there is no data and interactions will throw errors. The next step is to connect the standalone application to make calls to the search and metadata services.
1. Setup a local copy of the metadata service using the instructions found [here](https://github.com/lyft/amundsenmetadatalibrary).
2. Setup a local copy of the search service using the instructions found [here](https://github.com/lyft/amundsensearchlibrary).
3. Modify the `LOCAL_HOST`, `METADATA_PORT`, and `SEARCH_PORT` variables in the [LocalConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) to point to where your local metadata and search services are running, and restart the application with
```bash
$ python3 amundsen_application/wsgi.py
```

## Bootstrap a default version of Amundsen using Docker

The following instructions are for setting up a version of Amundsen using Docker. At the moment, we only support a bootstrap for connecting the Amundsen application to an example metadata service.

1. Install `docker` and  `docker-compose`.
2. Clone [this repo](https://github.com/lyft/amundsenfrontendlibrary) or download the [docker-amundsen.yml](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docker-amundsen.yml) file directly.
3. Enter the directory where the `docker-amundsen.yml` file is and then:
    ```bash
    $ docker-compose -f docker-amundsen.yml up
    ```
4. Ingest dummy data into Neo4j by doing the following:
   * Clone [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder).
   * Run the following commands in the `amundsenddatabuilder` directory:
   ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate  
    $ pip3 install -r requirements.txt
    $ python3 setup.py install
    $ python3 example/scripts/sample_data_loader.py
   ```
5. View UI at [`http://localhost:5000`](http://localhost:5000) and try to search `test`, it should return some result.
6. From where the `docker-amundsen.yml` file is, run the following command when done:
    ```bash
    $ docker-compose -f docker-amundsen.yml down
    ```

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
