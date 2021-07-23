# Amundsen Roadmap

The following roadmap gives an overview of what we are currently working on and what we want to tackle next. This helps potential contributors understand the current status of your project and where it's going next, as well as giving a chance to be part of the planning.

## Amundsen Mission

> _To organize all information about data and make it universally actionable_

## Vision for 2021

> _Centralize a comprehensive and actionable map of all our data resources that can be leveraged to solve a growing number of use cases and workflows_

## Short Term - Our Current focus

#### Native lineage integration

_What_: We want to create a native lineage integration in Amundsen, to better surface how data assets interact with each other.

_Status_: designs complete

#### Integrate with Data Quality system

_What_: Integrate with different data quality systems to provide quality score.

_Status_: in progress

#### Improve search ranking

_What_: Overhaul search ranking to improve results.

_Status_: planning

#### Show distinct column values

_What_: When a column has a limited set of possible values, we want to make then easily discoverable.

_Status_: implementation started

#### Neptune Databuilder support

_What_: Supports Databuilder ingestion for Neptune (`FsNeo4jCSVLoader`, `FsNeputuneCSVLoader` and various Neptune components). Detail could be found in [RFC-13](https://github.com/amundsen-io/rfcs/pull/13/files).

_Status_: implementation started

#### RDS Proxy Support

_What_: Support RDS as another type of proxy for both metadata and databuilder. Detail could be found in [RFC-10](https://github.com/amundsen-io/rfcs/pull/10)

_Status_: Planning


## Mid Term - Our Next steps

#### Curated navigation experience

_What_: Currently Amundsen's experience is very focussed on search. However, especially for new users, an experience where they are able to navigate through the data hierarchy is very important. This item proposes to revamp the navigational experience in Amundsen (currently, barebones - based on tags) to do justice to the user need to browse through data sets when they don't know what to even search for.

_Status_: planning

#### Notifications when a table evolves

_What_: Notify users in Amundsen (akin to Facebook notifications or similar) when a table evolves. Owners of data and consumers of data will likely need to be notified of different things.

_Status_: planning has not started

#### Commonly joined tables / browsing the data model

_What_: As a data user, I would like to see commonly joined tables and how to join them.
One option would be to show commonly joined tables and showing example join queries. Another option would be to provide a navigational experience for data model, showing foreign keys and which tables they come from.

_Status_: planning has not started

#### Push ingest API

_What_: Possible through [Kafka extractor](https://github.com/amundsen-io/amundsen/blob/main/databuilder/databuilder/extractor/kafka_source_extractor.py), though Kafka topic schema is not well defined. And it requires client side SDK to support message pushing.

_Status_: 50%

#### Granular Access Control

_What_: we want to have a more granular control of the access. For example, only certain types of people would be able to see certain types of metadata/functionality

_Status_: not planned

#### Versioning system

_What_: We want to create a versioning system for our indexed resources, to be able to index different versions of the same resource. This is especially required for machine learning purposes.

_Status_: not planned

#### Index Processes

_What_: we want to index ETLs and pipelines from our Machine Learning Engine

_Status_: not planned

#### Index Teams

_What_: We want to add teams pages to enable users to see what are the important tables and dashboard a team uses

_Status_: not planned

#### Index Services

_What_: With our microservices architecture, we want to index services and show how these services interact with data artifacts

_Status_: not planned

#### Index S3 buckets

_What_: add these new resource types to our data map and create resource pages for them

_Status_: not planned

#### Index Pub/Sub systems

_What_: We want to make our pub/sub systems discoverable

_Status_: not planned

## How to Get Involved

Let us know in the [Slack channel](https://app.slack.com/client/TGFR0CZM3/CGFBVT23V) if you are interested in taking a stab at leading the development of one of these features.

You can also jump right in by tackling one of our issues labeled as ['help wanted'](https://github.com/amundsen-io/amundsen/labels/help%20wanted) or, if you are new to Amundsen, try one of our ['good first issue'](https://github.com/amundsen-io/amundsen/labels/good%20first%20issue) tickets.
