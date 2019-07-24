# Amundsen Roadmap

**Mission**: To organize all information about data and make it universally actionable<br/>
**Vision (2020)**: Centralize a comprehensive and actionable map of all our data resources that can be leveraged to solve a growing number of use cases and workflows

The following roadmap gives an overview of what we are currently working on and what we want to tackle next. We share it so that the community can plan work together. Let us know in the Slack channel if you are interested in taking a stab at leading the development of one of these features (or of a non listed one!).

## Current focus

**Search & Resource page redesign**<br/>
*What*: Redesign the search experience and the resource page, to make them scalable in the number of resources types and the number of metadata<br/>
*Status*: Designs are ready, engineering work has started<br/>
*Links*: [Designs](https://drive.google.com/drive/folders/12oBrcXUsDtOsuU_QvO93LTvs4Dehx6az?usp=sharing)

**Email notifications system**<br/>
*What*: We are creating an email notification system to reach Amundsen’s users. The primary goal is to use this system to help solve the lack of ownership for data assets at Lyft. The secondary goal is to engage with users for general purposes.<br/>
*Status*: Designs are ready, engineering work has started

## Next steps

**Index Dashboards**
*What*: We want to help with the discovery of existing analysis work, dashboards. This is going to help avoid reinventing the wheel, create value for less technical users and help give context on how tables are used.<br/>
*Status*: Product + technical specs are ready, designs are ready, implementation has not started<br/>
*Links*: [Designs](https://drive.google.com/drive/folders/12oBrcXUsDtOsuU_QvO93LTvs4Dehx6az?usp=sharing) | [Product Specifications](https://docs.google.com/document/d/16cSKgM2sCYvhKq54yfwaHKwslJEGtdS2g5dcPV4p5qo/edit?usp=sharing) | [Technical RFC](https://docs.google.com/document/d/1PHk8OjcIULJ7hG0ckeMrRfTk3vXqnq5asEykgQUw-Ow/edit?usp=sharing)

**Native lineage integration**<br/>
*What*: We want to create a native lineage integration in Amundsen, to better surface how data assets interact with each other<br/>
*Status*: implementation has not started

**Landing page**<br/>
*What*: We are creating a proper landing page to provide more value, with an emphasis on helping users finding data when then don’t really know what to search for (exploration)<br/>
*Status*: being spec’d out

**Push ingest API**<br/>
*What*: We want to create a push API so that it is as easy as possible for a new data resource type to be ingested<br/>
*Status*: implementation has started (around 80% complete)

**GET Rest API**<br/>
*What*: enable users to access our data map programmatically through a Rest API<br/>
*Status*: implementation has started

**Index Druid tables and S3 buckets**<br/>
*What*: add these new resource types to our data map and create resource pages for them<br/>
*Status*:  implementation has not started

**Granular Access Control**<br/>
*What*: we want to have a more granular control of the access. For example, only certain types of people would be able to see certain types of metadata/functionality<br/>
*Status*: implementation has not started

**Show distinct column values**<br/>
*What*: When a column has a limited set of possible values, we want to make then easily discoverable<br/>
*Status*: implementation has not started

**“Order by” for columns**<br/>
*What*: we want to help users make sense of what are the columns people use in the tables we index. Within a frequently used table, a column might not be used anymore because it is know to be deprecated<br/>
*Status*: implementation has not started

**Index online datastores**<br/>
*What*: We want to make our DynamoDB and other online datastores discoverable by indexing them. For this purpose, we will probably leverage the fact that we have a centralized IDL (interface definition language)<br/>
*Status*: implementation has not started

**Integration with BI Tools**<br/>
*What*: get the richness of Amundsen’s metadata to where the data is used: in Bi tools such as Mode, Superset and Tableau<br/>
*Status*: implementation has not started

**Index Processes**<br/>
*What*: we want to index ETLs and pipelines from our Machine Learning Engine<br/>
*Status*: implementation has not started

**Versioning system**<br/>
*What*: We want to create a versioning system for our indexed resources, to be able to index different versions of the same resource. This is especially required for machine learning purposes.<br/>
*Status*: implementation has not started

**Index Teams**<br/>
*What*: We want to add teams pages to enable users to see what are the important tables and dashboard a team uses<br/>
*Status*: implementation has not started

**Index Services**<br/>
*What*: With our microservices architecture, we want to index services and show how these services interact with data artifacts<br/>
*Status*: implementation has not started

**Index Pub/Sub systems**<br/>
*What*: We want to make our pub/sub systems discoverable<br/>
*Status*: implementation has not started


