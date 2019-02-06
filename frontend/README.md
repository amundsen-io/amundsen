# Amundsen

Amundsen is a data discovery web portal. It leverages a separate [search service](https://github.com/lyft/amundsensearchlibrary) for allowing users to search for data resources, and a separate [metadata service](https://github.com/lyft/amundsenmetadatalibrary) for viewing and editing metadata for a given resource. It is a Flask application with a React frontend.

**TODO: Insert images and GIFs**

## Requirements
- Python >= 3.4

## Installation

### Install standalone application directly from the source
The following instructions are for setting up a standalone version of the Amundsen application. This approach is ideal for local development.
```bash
$ git clone https://github.com/lyft/amundsenfrontendlibrary.git
$ cd amundsenfrontendlibrary
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ python3 setup.py install
$ cd amundsen_application/static
$ npm install
$ npm run build # or npm run dev-build for un-minified source
$ cd ../..
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

### Bootstrap a default version of Amundsen using Docker
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
    $ docker build -f public.Dockerfile -t amundsen-search:latest .
    ```
6. Start all of the services using:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary
$ docker-compose -f docker-amundsen.yml up
```
7. Ingest dummy data into Neo4j by doing the following:
  * Clone [amundsendatabuilder](https://github.com/lyft/amundsendatabuilder).
  * Update the `NEO4J_ENDPOINT` in [sample_data_loader.py](https://github.com/lyft/amundsendatabuilder/blob/master/example/scripts/sample_data_loader.py) and replace `localhost` with the IP used for the `default` docker machine. You can see the IP in the `URL` outputted from running `docker-machine ls`.
  * Run the following commands:
    ```bash
    # in ~/<your-path-to-cloned-repo>/amundsendatabuilder
    $ virtualenv -p python3 venv3
    $ source venv3/bin/activate
    $ pip3 install -r requirements.txt
    $ python example/scripts/sample_data_loader.py
    ```
8. Verify dummy data has been ingested by viewing in Neo4j by visiting `http://YOUR-DOCKER-HOST-IP:7474/browser/` and run `MATCH (n:Table) RETURN n LIMIT 25` in the query box. You should see two tables -- `hive.core.test_driver` and `dynamo.core.test_pax`.
9. View UI at `http://YOUR-DOCKER-HOST-IP:5000/table_detail/gold/hive/core/test_driver`

## Configuration

### Flask
The default Flask application uses a [LocalConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) that looks for the metadata and search services running on localhost. In order to use different end point, you need to create a custom config class suitable for your use case. Once the config class has been created, it can be referenced via the [environment variable](https://github.com/lyft/amundsenfrontendlibrary/blob/4bf244d85bf82319b14919358691fd47a094e821/amundsen_application/wsgi.py#L5): `FRONTEND_SVC_CONFIG_MODULE_CLASS`

For more information on how the configuration is being loaded and used, please reference the official Flask [documentation](http://flask.pocoo.org/docs/1.0/config/#development-production).

### React Application

#### Application Config
Certain features of the React application import variables from an [AppConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/config/config.ts#L5) object. The configuration can be customized by modifying [config-custom.ts](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/config/config-custom.ts).

#### Custom Fonts & Styles
Fonts and css variables can be customized by modifying [fonts-custom.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_fonts-custom.scss) and
[variables-custom.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_variables-custom.scss).

## Developer Guide

### Environment
Follow the installation instructions in the section [Install standalone application directly from the source](https://github.com/lyft/amundsenfrontendlibrary#install-standalone-application-directly-from-the-spource).

Install the javascript development requirements:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/amundsen_application
$ cd static
$ npm install --only=dev
```

To test local changes to the javascript static files:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/amundsen_application
$ cd static
$ npm run dev-build # builds the development bundle
```

To test local changes to the python files, re-run the wsgi:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/amundsen_application
$ python3 wsgi.py
```

### Contributing

#### Python

If changes were made to any python files, run the python unit tests, linter, and type checker. Unit tests are run with `py.test`. They are located in `tests/unit`. Type checks are run with `mypy`. Linting is `flake8`. There are friendly `make` targets for each of these tests:
```bash
# after setting up environment
make test  # unit tests in Python 3
make lint  # flake8
make mypy  # type checks
```
Fix all errors before submitting a PR.

#### JS Assets
By default, the build commands that are run to verify local changes -- `npm run build` and `npm run dev-build` -- also conduct linting and type checking. During development be sure to fix all errors before submitting a PR.

**TODO: JS unit tests are in progress - document unit test instructions after work is complete**
