Amundsen allows for many modifications, and many require code-level modifications. Until we put together a "paved path" suggestion on how to manage such a set-up, for now we will document what community members are doing independenly. If you have a production Amundsen deployment, please edit this doc to describe your setup.


# Notes from community meeting 2020-12-03
These notes are from 2 companies a community round-table: https://www.youtube.com/watch?v=gVf7S98bnyg

## Brex
- What modifications have you made?
    - We've added backups
    - We wanted table descriptions to come solely from code.
- How do you deploy/secure Amundsen?
    - Our hosting is behind VPN, use OIDC
- What do you use Amundsen for?
    - Our primary use case: if I change this table, what dashboards will it break.
    - We also do PII tagging
    - ETL pipeline puts docs in Snowflake

## REA group

- Why did you choose Amundsen?
    - We don't have data stewards or formal roles who work on documentation. We liked that Amundsen didn't rely on curated/manual documentation.
    - Google Data Catalog doesn't allow you to search for data that you don't have access to.
    - Things that we considered in other vendors - business metric glossary, column level lineage.
- How do you deploy Amundsen?
    - Deployment on ECS. Built docker images on our own.
    - Deployment is done so that metadata is not lost. Looked into backing metadata in AWS, but decided not to. Instead use block storage so even if the instance goes down, the metadata is still there.
    - We only index prod data sets.
    - We don't consider Amundsen as a source of truth. Thus, we don't let people to enable update descriptions.
    - ETL indexer gets descriptions from BQ and puts it into Amundsen.
    - Postgres/source tables need some work to get descriptions from Go into Amundsen.
- Some changes we'd like to make:
    - Authentication and Authorization
        - Workflow for requesting access to data you can't already access: right now we don't have a workflow for requesting access that's connected to Amundsen. Seems like an area of investment.
    - Data Lineage
    - Business metrics glossary
- Q&A
    - Why build your own images?
        - Want to make sure system image and code running on the image should be tightly controlled. Patch over the specific files on top of Amundsen upstream code. Don't fork right now. We chose to patch and not fork.
- What was the process of getting alpha users onboard and getting feedback?
    - Chose ~8 people who had different roles and different tenure. Then did UX interviews.
