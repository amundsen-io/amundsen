# Popular Tables Configurations 

The required entity definitions for Atlas can be applied using [amundsenatlastypes](https://github.com/dwarszawski/amundsen-atlas-types/blob/master/README.md#kickstart-apache-atlas). 


Popular Tables
--------------
Amundsen has a concept of popular tables, which is a default entry point of the application for now. 
Popular Tables API leverages `popularityScore` attribute of `Table` super type to enable custom sorting strategy.
  
The suggested formula to generate the popularity score is provided below and should be applied by the external script or batch/stream process to update Atlas entities accordingly.
```
Popularity score = number of distinct readers * log(total number of reads)
``` 

`Table` entity definition with `popularityScore` attribute [amundsenatlastypes==1.0.2](https://github.com/dwarszawski/amundsen-atlas-types/blob/master/amundsenatlastypes/schema/01_2_table_schema.json). 

```json
    {
      "entityDefs": [
        {
          "name": "Table",
          "superTypes": [
            "DataSet"
          ],
          "attributeDefs": [
            {
              "name": "popularityScore",
              "typeName": "float",
              "isOptional": true,
              "cardinality": "SINGLE",
              "isUnique": false,
              "isIndexable": false,
              "defaultValue": "0.0"
            },
            {
              "name": "readers",
              "typeName": "array<Reader>",
              "isOptional": true,
              "cardinality": "LIST",
              "isUnique": false,
              "isIndexable": true,
              "includeInNotification": false
            }
          ]
        }
      ]
    }
```