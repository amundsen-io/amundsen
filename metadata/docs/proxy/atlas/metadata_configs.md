# Popular Tables Configurations (Table, Metadata, User Relationship)

In order to support different kind of statistics for Table (or even DataSet) we need to add
a new entity `Metadata` and make a relationship between Metadata and DataSet.

Also, in order to store User information and User's statistics and actions, we'll need a new User type entity, 
which will be linked with Metadata as Readers, Owners, Managers etc.  

We are not going to add custom attributes directly to a Table/DataSet entity, to make it backward compatible and clean of course.

Following is the code to generate that relationship between Metadata, User and DataSet.

```python
    userReaderMetadata_DefDict = {
        "entityDefs": [
            {
                "superTypes": ["Referenceable"],
                "name": "User",
                "typeVersion": "2.0",
                "description": "The User Entity. Used to make relationship between users and entities.",
            },
            {
                "superTypes": ["Referenceable"],
                "name": "Reader",
                "description": "The entity reader count. Maps user with the count",
                "typeVersion": "2.0",
                "attributeDefs": [
                    {
                        "name": "count",
                        "isOptional": False,
                        "isUnique": False,
                        "isIndexable": False,
                        "typeName": "int",
                        "cardinality": "SINGLE",
                        "valuesMinCount": 0
                    }
                ]
            },
            {
                "superTypes": ["Referenceable"],
                "name": "Metadata",
                "description": "The metadata information of the Entity.",
                "typeVersion": "2.0",
                "attributeDefs": [
                    {
                        "name": "popularityScore",
                        "typeName": "float",
                        "isOptional": True,
                        "cardinality": "SINGLE",
                        "isUnique": False,
                        "isIndexable": False
                    }
                ]
            }
        ],
        "relationshipDefs": [
            {
                "name": "Reader_Users",
                "typeVersion": "2.0",
                "relationshipCategory": "COMPOSITION",
                "relationshipLabel": "__Reader.Users",
                "endDef1": {
                    "type": "Reader",
                    "name": "user",
                    "isContainer": False,
                    "cardinality": "SINGLE",
                    "isLegacyAttribute": True
                },
                "endDef2": {
                    "type": "User",
                    "name": "entityReads",
                    "isContainer": True,
                    "cardinality": "SET",
                    "isLegacyAttribute": True
                },
                "propagateTags": "NONE"
            },
            {
                "name": "Metadata_Reader",
                "typeVersion": "2.0",
                "relationshipCategory": "COMPOSITION",
                "relationshipLabel": "__Metadata.Reader",
                "endDef1": {
                    "type": "Metadata",
                    "name": "readers",
                    "isContainer": True,
                    "cardinality": "SET",
                    "isLegacyAttribute": False
                },
                "endDef2": {
                    "type": "Reader",
                    "name": "entityMetadata",
                    "isContainer": False,
                    "cardinality": "SINGLE",
                    "isLegacyAttribute": True
                },
                "propagateTags": "NONE"
            },
            {
                "name": "DataSet_Metadata",
                "typeVersion": "2.0",
                "relationshipCategory": "AGGREGATION",
                "relationshipLabel": "_DataSet.Metadata",
                "endDef1": {
                    "type": "DataSet",
                    "name": "metadata",
                    "isContainer": True,
                    "cardinality": "SINGLE",
                    "isLegacyAttribute": True
                },
                "endDef2": {
                    "type": "Metadata",
                    "name": "parentEntity",
                    "isContainer": False,
                    "cardinality": "SINGLE",
                    "isLegacyAttribute": True
                },
                "propagateTags": "NONE"
            },
        ]
    }
    try:
        client.typedefs.create(data=userReaderMetadata_DefDict)
    except Conflict as ex:
        print("Exception: {0}".format(str(ex)))
        client.typedefs.update(data=userReaderMetadata_DefDict)
```

Popular Tables
--------------
Amundsen has a concept of popular tables, which is a default entry point of the application for now. 
Popular Tables API expects you to generate the relationships above, and fill in your `popularityScore` within Metadata entityt
for each Table. 
The suggested formula to generate the popularity score is
```
Popularity score = number of distinct readers * log(total number of reads)
``` 

Sample code to fill in the `popularityScore`, using above relationships would be something like this. 

```python
    # Generate a list of all resources/tables, and group them by users' number of access
    updated_list = [
        {'resource': 'customer_dim@cl1', 'users': [['dummy@gmail.com', 2], ['user@gmail.copm', 2]], 'popularity_score': 4},
        {'resource': 'sales_fact@cl1', 'users': [['dummy@gmail.com', 14], ['foobar@gmail.com', 1]], 'popularity_score': 6},
        {'resource': 'log_fact_daily_mv@cl1', 'users': [['dummy@gmail.com', 1]], 'popularity_score': 1},
        {'resource': 'amundsen_logging_fact_monthly_mv_updated@cl1', 'users': [['user@gmail.com', 10], ['boo@gmail.com', 15]],
         'popularity_score': 8},
        {'resource': 'product_dim@cl1', 'users': [['dummy@gmail.com', 3], ['boo@gmail.com', 16], ['foobar@gmail.com', 12]], 'popularity_score': 5},
    ]

    
    # Iterate over each item and generate relevant entities
    for item in updated_list:
        bulk_entities = list()
        # Qualified Name (qn)
        qn_entity = item.get('resource')
        entity = client.entity_unique_attribute('Table', qualifiedName=qn_entity)
        if entity.entity:
            qn_metadata = f'{qn_entity}.metadata'

            metadata = entity.entity.get("relationshipAttributes").get("metadata")

            # Create Metadata if not exist already
            if metadata:
                metadata_guid = metadata["guid"]
            else:
                # Temp GUID
                metadata_guid = -10000

            # Add/Update Metadata and the popularityScore
            bulk_entities.append(
                {'typeName': 'Metadata',
                 'guid': metadata_guid,
                 'attributes':
                    {'qualifiedName': qn_metadata,
                     'popularityScore': item.get("popularity_score"),
                     'parentEntity': {'guid': entity.entity['guid'],
                                      'typeName': entity.entity['typeName']}}
                 }
            )

            for index, user in enumerate(item.get('users')):
                qn_user, access_count = user
                qn_reader = f'{qn_metadata}.{qn_user}.reader'
                user_entity = client.entity_unique_attribute('User', qualifiedName=qn_user)
                if user_entity.entity:
                    user_guid = user_entity.entity["guid"]
                else:
                    user_guid = -20000 + index
                    bulk_entities.append(
                        {'typeName': 'User',
                         'guid': user_guid,
                         'attributes': {'qualifiedName': qn_user}
                         }
                    )
                # Add/Update Reader object of user based on access counts
                bulk_entities.append(
                    {'typeName': 'Reader',
                     'attributes': {'qualifiedName': qn_reader,
                                    'count': access_count,
                                    'entityMetadata': {'guid': metadata_guid},
                                    'user': {'guid': user_guid}}
                     }
                )

            if bulk_entities:
                client.entity_bulk.create(data={"entities": bulk_entities})

```