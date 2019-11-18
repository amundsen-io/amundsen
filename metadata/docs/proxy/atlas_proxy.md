# Atlas Proxy

In order to make the Atlas-Amundsen integration smooth, we've released a python package, 
[amundsenatlastypes](https://github.com/dwarszawski/amundsen-atlas-types) that has all the required entity definitions along with helper functions needed to make 
Atlas compatible with Amundsen. 

Usage and Installation of `amundsenatlastypes` can be found [here](https://github.com/dwarszawski/amundsen-atlas-types/blob/master/README.md)

### Metadata Entities Explained  

In order to support different kind of statistics for Table, Column (or even DataSet) 
we need to add new entities `Metadata` (table_metadata, column_metadata etc.) and make a relationship between Metadata and DataSet.

Also, in order to store User information and User's statistics and actions, we'll need a new User type entity, 
which will be linked with Metadata as Readers, Owners, Managers etc.

We are not going to add custom attributes directly to a Table/DataSet entity, to make it backward compatible and clean of course.


### Configurations  

Once you are done with setting up required entity definitions using [amundsenatlastypes](https://github.com/dwarszawski/amundsen-atlas-types),
you are all set to use Atlas with Amundsen. 


Other things to configure:
 
- [Popular Tables](/docs/proxy/atlas/popular_tables.md)