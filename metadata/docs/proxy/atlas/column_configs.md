# Atlas Columns Configuration 

Create a new atlas client instance. (update the host and credentials information)
```python
from atlasclient.client import Atlas
client = Atlas(host='localhost', port=21000, username='admin', password='admin')
``` 

## Setting up column statistics
In order to store the statistics for each column, amundsen expects you to use Atlas' Structures definition, 
that will hold all the statistics as an attribute `stats` in each column. 

First, you need to create Structure definition within atlas:

```python
# Change this if you want to name your Structure differently
COLUMN_STATS_ENTITY = 'col_stat'

# Make the structure definition dictionary
struct_def_dict = {
        "structDefs": [
            {
                "name": COLUMN_STATS_ENTITY,
                "attributeDefs": [
                    {
                        "name": "stat_name",
                        "typeName": "string",
                        "isOptional": False,
                        "cardinality": "SINGLE",
                        "isUnique": True,
                        "isIndexable": False
                    },
                    {
                        "name": "stat_val",
                        "typeName": "double",
                        "isOptional": False,
                        "cardinality": "SINGLE",
                        "isUnique": False,
                        "isIndexable": False
                    },
                    {
                        "name": "start_epoch",
                        "typeName": "date",
                        "isOptional": False,
                        "cardinality": "SINGLE",
                        "isUnique": False,
                        "isIndexable": False
                    },
                    {
                        "name": "end_epoch",
                        "typeName": "date",
                        "isOptional": False,
                        "cardinality": "SINGLE",
                        "isUnique": False,
                        "isIndexable": False
                    }                    
                ]
            }]
}

# Create the new definition within Atlas
client.typedefs.create(data=struct_def_dict)
```

Next part is to assign the newly created structure as an attribute for all the column type entities in Atlas. 

```python
# Create the entity definition for all the columns available within atlas
column_entity_defs = []
for t in client.typedefs:
    for col in t.entityDefs:
        # If the type name ends with '_column' then add a new attribute 'stats'
        # and 'stats' would be an array of 'COLUMN_STATS_ENTITY'
        
        # You can have your own logic of assigning specific columns with this attribute here.
        if col.name.endswith('_column'):
            entity_dict = col._data
            stats_attribute = {
                        "name": "stats",
                        "typeName": "array<{col_entity}>".format(col_entity=COLUMN_STATS_ENTITY),
                        "isOptional": True,
                        "cardinality": "LIST",
                        "isUnique": False,
                        "isIndexable": False,
                        "includeInNotification": False
                    }
            entity_dict["attributeDefs"].append(stats_attribute)
            column_entity_defs.append(entity_dict)
            
# Make the entity definition dictionary
col_def_dict = {
        "entityDefs": column_entity_defs
}

# Update the column definitions.
client.typedefs.update(data=col_def_dict)
```

Once done, the columns in atlas should have the new attribute `stats`, which you can use to store your column statistics. 

*Sample statistics:*
```python
{
    "typeName": "col_stat",
    "attributes": {
        "stat_name": "max",
        "stat_val": 12.0,
        "end_epoch": 1560260088,
        "start_epoch": 1560260088
    }
},
{
    "typeName": "col_stat",
    "attributes": {
        "stat_name": "mean",
        "stat_val": 2.2,
        "end_epoch": 1560260088,
        "start_epoch": 1560260088
    }
},
{
    "typeName": "col_stat",
    "attributes": {
        "stat_name": "min",
        "stat_val": 3.0,
        "end_epoch": 1560260088,
        "start_epoch": 1560260088
    }
},
```




