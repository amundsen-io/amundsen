# Popular Tables Configurations 

The required entity definitions for Atlas can be applied using [amundsenatlastypes](https://github.com/dwarszawski/amundsen-atlas-types/blob/master/README.md#kickstart-apache-atlas). 


Popular Tables
--------------
Amundsen has a concept of popular tables, which is a default entry point of the application for now. 
Popular Tables API expects you to generate the relationships above, and fill in your `popularityScore` within `table_metadata` entity
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
                {'typeName': 'table_metadata',
                 'guid': metadata_guid,
                 'attributes':
                    {'qualifiedName': qn_metadata,
                     'popularityScore': item.get("popularity_score"),
                     'table': {'guid': entity.entity['guid'],
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