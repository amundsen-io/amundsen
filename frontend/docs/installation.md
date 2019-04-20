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

1. Install `docker`, `docker-compose`, and `docker-machine`.
2. Start a managed docker virtual host using the following command:
```bash
# in our examples our machine is named 'default'
$ docker-machine create -d virtualbox default
```
3. Check your docker daemon locally using:
```bash
$ docker-machine ls
```
  You should see the `default` machine listed, running on virtualbox with no errors listed.
4. Set up the docker environment using
```bash
$ eval $(docker-machine env default)
```
5. Setup your local environment.
  * Clone [this repo](https://github.com/lyft/amundsenfrontendlibrary), [amundsenmetadatalibrary](https://github.com/lyft/amundsenmetadatalibrary), and [amundsensearchlibrary](https://github.com/lyft/amundsensearchlibrary).
  * In your local versions of each library, update the `LOCAL_HOST` in the `LocalConfig` with the IP used for the `default` docker machine. You can see the IP in the `URL` outputted from running `docker-machine ls`.
  * Build the docker images
    ```bash
    # in ~/<your-path-to-cloned-repo>/amundsenmetadatalibrary
    $ docker build -f public.Dockerfile -t amundsen-metadata:latest .

    # in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary
    $ docker build -f public.Dockerfile -t amundsen-frontend:latest .

    # in ~/<your-path-to-cloned-repo>/amundsensearchlibrary
    $ docker build -f Dockerfile -t amundsen-search:latest .
    ```
6. Start all of the services using:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary
$ docker-compose -f docker-amundsen.yml up
```
7. Ingest dummy data into Neo4j by doing the following:
  * Clone [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder).
  * Update the `NEO4J_ENDPOINT` and `Elasticsearch host` in [sample_data_loader.py](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py) and replace `localhost` with the IP used for the `default` docker machine. You can see the IP in the `URL` outputted from running `docker-machine ls`.
  * Run the following commands:
    ```bash
    # in ~/<your-path-to-cloned-repo>/amundsendatabuilder
    $ virtualenv -p python3 venv3
    $ source venv3/bin/activate  
    $ pip3 install -r requirements.txt
    $ python setup.py install      
    $ python example/scripts/sample_data_loader.py
    ```
8. Verify dummy data has been ingested by viewing in Neo4j by visiting `http://YOUR-DOCKER-HOST-IP:7474/browser/` and run `MATCH (n:Table) RETURN n LIMIT 25` in the query box. You should see two tables -- `hive.test_schema.test_table1` and `dynamo.test_schema.test_table2`.
9. View UI at `http://YOUR-DOCKER-HOST-IP:5000/table_detail/gold/hive/test_schema/test_table1` or `/table_detail/gold/dynamo/test_schema/test_table2`
10. View UI at `http://YOUR-DOCKER-HOST-IP:5000` and try to search `test`, it should return some result.