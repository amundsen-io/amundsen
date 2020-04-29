
## People resources 

### What can I do with User Resources? 
User profile pages and the ability to bookmark/favorite and search for users is also available as of now. See a demo of what they feels like from an end user viewpoint from around the 36 minute mark of [this September 2019 talk](https://youtu.be/Gr3-RfWn49A?t=36m00s) - so you could actually argue that this video snippet can work as an end user guide.

### How do I enable User pages?

The configuration to have `Users` available consists of:

1. Enable the users profile page index and display feature by performing [this frontend configuration](../../frontend/docs/application_config#index-users)

2. There are two different alternative ways to populate user profile data. You can either:

    * Configure the Metadata service to a do a [live lookup](../../metadata/docs/configurations#user_detail_method-optional) in some directory service, like LDAP or a HR system.

    * Setup ongoing ingest of user profile data as they onboard/change/offboard into Neo4j and Elasticsearch effectively caching it with the pros/cons of that (similar to what the Databuilder sample loader does from user CSV, see the “pre-cooked demo data” link in the [Architecture overview](../../architecture#databuilder)

    !!! note
        Currently, for both of these options Amundsen _only_ provides these hooks/interfaces to add your own implementation. If you build something you think is generally useful, contributions are welcome!

3. Configure login, according to the [Authentication guide](../../authentication/oidc)

