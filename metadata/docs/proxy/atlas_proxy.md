Create a new atlas client instance. (update the host and credentials information)
```python
from atlasclient.client import Atlas
client = Atlas(host='localhost', port=21000, username='admin', password='admin')
``` 

### Create a Super Type Entity
Since Atlas stores most of the metadata about tables, databases, columns etc., 
we need to have a super Entity Type, that can be used to filter out the Tables only.

[Atlas Proxy](https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/proxy/atlas_proxy.py) uses 
`Table` as super entity type. 
```python
TABLE_ENTITY = 'Table'
```
 
Create a new type, defined above via `TABLE_ENTITY` using the script below.
 ```python 
typedef_dict = {
    "entityDefs": [
        {
            "name": TABLE_ENTITY,
            "superTypes": ["DataSet"],
        }
    ]
}

client.typedefs.create(data=typedef_dict)
```

### Add required fields
We need to add some extra fields to atlas in order to get all the information needed for the amundsen frontend. 
Adding those extra attributes in the super type entity definition would be handy to keep them in once place.

[TBD - How to add attributes definition] 

### Assign superType to entity definitions
Assign newly created TABLE_ENTITY entity as super type to the entity definitions you want to behave like tables.
in the code snippet below, `'hive_table' and 'rdbms_table'` would be affected. 
```python
# Below are the entity which would behave like table entities for Amundsen Atlas Proxy
atlas_tables = ['hive_table', 'rdbms_table']
entities_to_update = []
for t in client.typedefs:
    for e in t.entityDefs:
        if e.name in atlas_tables:
            superTypes = e.superTypes     # Get a property first to inflate the relational objects
            ent_dict = e._data
            ent_dict["superTypes"] = superTypes
            ent_dict["superTypes"].append(TABLE_ENTITY)
            entities_to_update.append(ent_dict)

typedef_dict = {
    "entityDefs": entities_to_update
}
client.typedefs.update(data=typedef_dict)
```
