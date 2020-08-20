# Amundsen Roadmap
The following roadmap gives an overview of what we are currently working on and what we want to tackle next. This helps potential contributors understand the current status of your project and where it's going next, as well as giving a chance to be part of the planning.

## Amundsen Mission
> *To organize all information about data and make it universally actionable*

## Vision for 2020
> *Centralize a comprehensive and actionable map of all our data resources that can be leveraged to solve a growing number of use cases and workflows*

## Short Term - Our Current focus

#### Provide Rich metadata to make data trust worthy
*What*: Enrich table detail page with additional structure metadata / programmatic description.

*Status*: tech spec WIP

#### Native lineage integration
*What*: We want to create a native lineage integration in Amundsen, to better surface how data assets interact with each other.

*Status*: tech spec out

#### Integrate with Data Quality system
*What*: Integrate with different data quality systems to provide quality score.

*Status*: planning

## Mid Term - Our Next steps
#### Improve search ranking
*What*: Update search ranking to be informed by "badges" that may exist on data sets e.g. deprecated, etc.

*Status*: planning

#### Notifications when a table evolves
*What*: Notify users in Amundsen (akin to Facebook notifications or similar) when a table evolves. Owners of data and consumers of data will likely need to be notified of different things.

*Status*: planning has not started 

#### Commonly joined tables / browsing the data model
*What*: As a data user, I would like to see commonly joined tables and how to join them.
One option would be to show commonly joined tables and showing example join queries. Another option would be to provide a navigational experience for data model, showing foreign keys and which tables they come from.

*Status*: planning has not started 

#### Curated navigation experience
*What*: Currently Amundsen's experience is very focussed on search. However, especially for new users, an experience where they are able to navigate through the data hierarchy is very important. This item proposes to revamp the navigational experience in Amundsen (currently, barebones - based on tags) to do justice to the user need to browse through data sets when they don't know what to even search for.

*Status*: planning

#### Push ingest API
*What*: We want to create a push API so that it is as easy as possible for a new data resource type to be ingested  

*Status*: implementation has started (around 80% complete)  

#### GET Rest API
*What*: enable users to access our data map programmatically through a Rest API  

*Status*: implementation has started  

#### Granular Access Control
*What*: we want to have a more granular control of the access. For example, only certain types of people would be able to see certain types of metadata/functionality  

*Status*: implementation has not started  

#### Show distinct column values
*What*: When a column has a limited set of possible values, we want to make then easily discoverable  

*Status*: implementation has not started  

#### “Order by” for columns
*What*: we want to help users make sense of what are the columns people use in the tables we index. Within a frequently used table, a column might not be used anymore because it is know to be deprecated  

*Status*: implementation has not started  

#### Versioning system
*What*: We want to create a versioning system for our indexed resources, to be able to index different versions of the same resource. This is especially required for machine learning purposes.  

*Status*: implementation has not started  

#### Index Processes
*What*: we want to index ETLs and pipelines from our Machine Learning Engine  

*Status*: implementation has not started  

#### Index Teams
*What*: We want to add teams pages to enable users to see what are the important tables and dashboard a team uses  

*Status*: implementation has not started  

#### Index Services
*What*: With our microservices architecture, we want to index services and show how these services interact with data artifacts

*Status*: implementation has not started

#### Index S3 buckets
*What*: add these new resource types to our data map and create resource pages for them  

*Status*:  implementation has not started

#### Index Pub/Sub systems
*What*: We want to make our pub/sub systems discoverable

*Status*: implementation has not started

## How to Get Involved
Let us know in the [Slack channel](https://app.slack.com/client/TGFR0CZM3/CGFBVT23V) if you are interested in taking a stab at leading the development of one of these features.

You can also jump right in by tackling one of our issues labeled as ['help wanted'](https://github.com/amundsen-io/amundsen/labels/help%20wanted) or, if you are new to Amundsen, try one of our ['good first issue'](https://github.com/amundsen-io/amundsen/labels/good%20first%20issue) tickets.
