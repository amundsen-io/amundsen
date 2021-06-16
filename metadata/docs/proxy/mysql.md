# MySQL Proxy

MySQL proxy works with [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/13/orm/) and [Amundsen RDS](https://github.com/amundsen-io/amundsenrds)
containing all the ORM models used for Amundsen databuilder and metadataservice.

# Requirements
MySQL >= 5.7

# Schema migration
Before running MySQL as the Amundsen metadata store, we need initialize/upgrade all the table schemas first. 
The schema migration is managed by cli in metadata service and [Alembic](https://alembic.sqlalchemy.org/en/latest/) behind. 

#### Add config for MySQL
```
PROXY_CLI = PROXY_CLIS['MYSQL']
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', {mysql_connection_string})
# other fileds used for mysql proxy
......
``` 
see metadata [config](https://github.com/amundsen-io/amundsen/blob/main/metadata/metadata_service/config.py)


#### Add environment variables

Specify how to load the application: ```export FLASK_APP=metadata_service/metadata_wsgi.py```


#### Run migration commands

If we need initialize/upgrade db: ```flask rds initdb```

If we need reset db:  ```flask rds resetdb --yes```
or ```flask rds resetdb``` (then enter y after a prompt message.) 
