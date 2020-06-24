# Amundsen Roadmap

**Mission**: To organize all information about data and make it universally actionable  
**Vision (2020)**: Centralize a comprehensive and actionable map of all our data resources that can be leveraged to solve a growing number of use cases and workflows

The following roadmap gives an overview of what we are currently working on and what we want to tackle next. We share it so that the community can plan work together. Let us know in the [Slack channel](https://app.slack.com/client/TGFR0CZM3/CGFBVT23V) if you are interested in taking a stab at leading the development of one of these features (or of a non listed one!).

## Current focus

#### Provide Rich metadata to make data trust worthy
*What*: Enrich table detail page with additional structure metadata / programmatic description
*Status*: tech spec WIP

#### Native lineage integration
*What*: We want to create a native lineage integration in Amundsen, to better surface how data assets interact with each other  
*Status*: tech spec out


#### Integrate with data quality system
*What*: Integrate with different data quality systems to provide quality score
*Status*: planning


## Next steps


#### Push ingest API
*What*: We want to create a push API so that it is as easy as possible for a new data resource type to be ingested  
*Status*: implementation has started (around 80% complete)  



#### GET Rest API
*What*: enable users to access our data map programmatically through a Rest API  
*Status*: implementation has started  



#### Index S3 buckets
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
