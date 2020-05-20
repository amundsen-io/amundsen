# Amundsen Roadmap

**Mission**: To organize all information about data and make it universally actionable  
**Vision (2020)**: Centralize a comprehensive and actionable map of all our data resources that can be leveraged to solve a growing number of use cases and workflows

The following roadmap gives an overview of what we are currently working on and what we want to tackle next. We share it so that the community can plan work together. Let us know in the [Slack channel](https://app.slack.com/client/TGFR0CZM3/CGFBVT23V) if you are interested in taking a stab at leading the development of one of these features (or of a non listed one!).

## Current focus

#### Index Dashboards
*What*: We want to help with the discovery of existing analysis work, dashboards. This is going to help avoid reinventing the wheel, create value for less technical users and help give context on how tables are used.  
*Status*: MVP Done
*Links*: [Designs](https://drive.google.com/drive/folders/12oBrcXUsDtOsuU_QvO93LTvs4Dehx6az?usp=sharing) | [Product Specifications](https://docs.google.com/document/d/16cSKgM2sCYvhKq54yfwaHKwslJEGtdS2g5dcPV4p5qo/edit?usp=sharing) | [Technical RFC](https://docs.google.com/document/d/1PHk8OjcIULJ7hG0ckeMrRfTk3vXqnq5asEykgQUw-Ow/edit?usp=sharing)

## Next steps

#### Native lineage integration
*What*: We want to create a native lineage integration in Amundsen, to better surface how data assets interact with each other  
*Status*: implementation has not started

#### Landing page
*What*: We are creating a proper landing page to provide more value, with an emphasis on helping users finding data when then don’t really know what to search for (exploration)  
*Status*: being spec’d out


#### Push ingest API
*What*: We want to create a push API so that it is as easy as possible for a new data resource type to be ingested  
*Status*: implementation has started (around 80% complete)  



#### GET Rest API
*What*: enable users to access our data map programmatically through a Rest API  
*Status*: implementation has started  



#### Index Druid tables and S3 buckets
*What*: add these new resource types to our data map and create resource pages for them  
*Status*:  implementation has not started



#### Granular Access Control
*What*: we want to have a more granular control of the access. For example, only certain types of people would be able to see certain types of metadata/functionality  
*Status*: implementation has not started  



#### Show distinct column values
*What*: When a column has a limited set of possible values, we want to make then easily discoverable  
*Status*: implementation has not started  



#### “Order by” for columns
*What*: we want to help users make sense of what are the columns people use in the tables we index. Within a frequently used table, a column might not be used anymore because it is know to be deprecated  
*Status*: implementation has not started  



#### Index online datastores
*What*: We want to make our DynamoDB and other online datastores discoverable by indexing them. For this purpose, we will probably leverage the fact that we have a centralized IDL (interface definition language)  
*Status*: implementation has not started  



#### Integration with BI Tools
*What*: get the richness of Amundsen’s metadata to where the data is used: in Bi tools such as Mode, Superset and Tableau  
*Status*: implementation has not started  



#### Index Processes
*What*: we want to index ETLs and pipelines from our Machine Learning Engine  
*Status*: implementation has not started  



#### Versioning system
*What*: We want to create a versioning system for our indexed resources, to be able to index different versions of the same resource. This is especially required for machine learning purposes.  
*Status*: implementation has not started  



#### Index Teams
*What*: We want to add teams pages to enable users to see what are the important tables and dashboard a team uses  
*Status*: implementation has not started  



#### Index Services
*What*: With our microservices architecture, we want to index services and show how these services interact with data artifacts
*Status*: implementation has not started



#### Index Pub/Sub systems
*What*: We want to make our pub/sub systems discoverable
*Status*: implementation has not started
