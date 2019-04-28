# Amundsen Metadata service
Amundsen Metadata service serves Restful API and responsible for providing and also updating metadata, such as table & column description, and tags. Metadata service can use Neo4j or Apache Atlas as a persistent layer.


## Requirements
- Python >= 3.7

## Instructions to start the Metadata service from distribution
```bash
$ venv_path=[path_for_virtual_environment]
$ python3 -m venv $venv_path
$ source $venv_path/bin/activate
$ pip3 install amundsenmetadata
$ python3 metadata_service/metadata_wsgi.py

-- In different terminal, verify getting HTTP/1.0 200 OK
$ curl -v http://localhost:5000/healthcheck
```

## Instructions to start the Metadata service from the source
```bash
$ git clone https://github.com/lyft/amundsenmetadatalibrary.git
$ cd amundsenmetadatalibrary
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ python3 setup.py install
$ python3 metadata_service/metadata_wsgi.py

-- In different terminal, verify getting HTTP/1.0 200 OK
$ curl -v http://localhost:5000/healthcheck
```

## Instructions to start the service from the Docker
```bash
$ docker pull amundsen-metadata
$ docker run -p 5000:5000 amundsen-metadata

-- In different terminal, verify getting HTTP/1.0 200 OK
$ curl -v http://localhost:5000/healthcheck
```

## Production environment
By default, Flask comes with Werkzeug webserver, which is for development. For production environment use production grade web server such as [Gunicorn](https://gunicorn.org/ "Gunicorn").

```bash
$ pip install gunicorn
$ gunicorn metadata_service.metadata_wsgi
```
Here is [documentation](http://docs.gunicorn.org/en/latest/run.html "documentation") of gunicorn configuration.

### Configuration outside local environment
By default, Metadata service uses [LocalConfig](https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/config.py "LocalConfig") that looks for Neo4j running in localhost.
In order to use different end point, you need to create [Config](https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/config.py "Config") suitable for your use case. Once config class has been created, it can be referenced by [environment variable](https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/metadata_wsgi.py "environment variable"): `METADATA_SVC_CONFIG_MODULE_CLASS`

For example, in order to have different config for production, you can inherit Config class, create Production config and passing production config class into environment variable. Let's say class name is ProdConfig and it's in metadata_service.config module. then you can set as below:

`METADATA_SVC_CONFIG_MODULE_CLASS=metadata_service.config.ProdConfig`

This way Metadata service will use production config in production environment. For more information on how the configuration is being loaded and used, here's reference from Flask [doc](http://flask.pocoo.org/docs/1.0/config/#development-production "doc").

# Apache Atlas
Amundsen Metadata service can use Apache Atlas as a backend. Some of the benefits of using Apache Atlas instead of Neo4j is that Apache Atlas offers plugins to several services (e.g. Apache Hive, Apache Spark) that allow for push based updates. It also allows to set policies on what metadata is accesible and editable by means of Apache Ranger.

If you would like to use Apache Atlas as a backend for Metadata service you will need to create a [Config](https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/config.py "Config") as mentioned above. Make sure to include the following:

```python
PROXY_CLIENT = PROXY_CLIENTS['ATLAS'] # or env PROXY_CLIENT='ATLAS'
PROXY_PORT = 21000          # or env PROXY_PORT
PROXY_USER = 'atlasuser'    # or env CREDENTIALS_PROXY_USER
PROXY_PASSWORD = 'password' # or env CREDENTIALS_PROXY_PASSWORD
```

To start the service with Atlas from Docker. Make sure you have `atlasserver` configured in DNS (or docker-compose)

```bash
$ docker run -p 5000:5000 --env PROXY_CLIENT=ATLAS --env PROXY_PORT=21000 --env PROXY_HOST=atlasserver --env CREDENTIALS_PROXY_USER=atlasuser --env CREDENTIALS_PROXY_PASSWORD=password amundsen-metadata:latest
```

---
**NOTE**

The support for Apache Atlas is work in progress. For example, while Apache Atlas supports fine grained access, Amundsen does not support this yet. 

# Developer guide
## Code style
- PEP 8: Amundsen Metadata service follows [PEP8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/ "PEP8 - Style Guide for Python Code"). 
- Typing hints: Amundsen Metadata service also utilizes [Typing hint](https://docs.python.org/3/library/typing.html "Typing hint") for better readability.

## Code structure
Please visit [Code Structure](docs/structure.md) to read how different modules are structured in Amundsen Metadata service.