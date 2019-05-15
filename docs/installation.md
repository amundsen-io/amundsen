# Installation

## Bootstrap a default version of Amundsen using Docker
The following instructions are for setting up a version of Amundsen using Docker. At the moment, we only support a bootstrap for connecting the Amundsen application to an example metadata service.

1. Install `docker`, `docker-compose`, and `docker-machine`.
2. Install `virtualbox` and `virtualenv`.
3. Start a managed docker virtual host using the following command:
```bash
# in our examples our machine is named 'default'
$ docker-machine create -d virtualbox default
```
4. Check your docker daemon locally using:
```bash
$ docker-machine ls
```
  You should see the `default` machine listed, running on virtualbox with no errors listed.
5. Set up the docker environment using
```bash
$ eval $(docker-machine env default)
```
6. Setup your local environment.
  * Clone [this repo](https://github.com/lyft/amundsenfrontendlibrary), [amundsenmetadatalibrary](https://github.com/lyft/amundsenmetadatalibrary), and [amundsensearchlibrary](https://github.com/lyft/amundsensearchlibrary).
  * In your local versions of each library, update the `LOCAL_HOST` in the `LocalConfig` with the IP used for the `default` docker machine. You can see the IP in the `URL` outputted from running `docker-machine ls`.
7. Start all of the services using:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary
$ docker-compose -f docker-amundsen.yml up
```
8. Ingest dummy data into Neo4j by doing the following:
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
9. Verify dummy data has been ingested by viewing in Neo4j by visiting `http://YOUR-DOCKER-HOST-IP:7474/browser/` and run `MATCH (n:Table) RETURN n LIMIT 25` in the query box. You should see two tables -- `hive.test_schema.test_table1` and `dynamo.test_schema.test_table2`.
10. View UI at `http://YOUR-DOCKER-HOST-IP:5000/table_detail/gold/hive/test_schema/test_table1` or `/table_detail/gold/dynamo/test_schema/test_table2`
11. View UI at `http://YOUR-DOCKER-HOST-IP:5000` and try to search `test`, it should return some result.
