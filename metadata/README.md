# Amundsen Metadata service
Amundsen Metadata service serves Restful API and responsible for providing and also updating metadata, such as table & column description, and tags. Metadata service is using Neo4j as a persistent layer.


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

# Developer guide
## Code style
- PEP 8: Amundsen Metadata service follows [PEP8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/ "PEP8 - Style Guide for Python Code"). 
- Typing hints: Amundsen Metadata service also utilizes [Typing hint](https://docs.python.org/3/library/typing.html "Typing hint") for better readability.

## Code structure
Please visit [Code Structure](docs/structure.md) to read how different modules are structured in Amundsen Metadata service.