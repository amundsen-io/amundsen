# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

class PublisherConfigs:
    # A directory that contains CSV files for nodes
    NODE_FILES_DIR = 'node_files_directory'
    # A directory that contains CSV files for relationships
    RELATION_FILES_DIR = 'relation_files_directory'

    # A CSV header with this suffix will be passed to the statement without quotes
    UNQUOTED_SUFFIX = ':UNQUOTED'

    # This will be used to provide unique tag to the node and relationship
    JOB_PUBLISH_TAG = 'job_publish_tag'

    # any additional fields that should be added to nodes and rels through config
    ADDITIONAL_PUBLISHER_METADATA_FIELDS = 'additional_publisher_metadata_fields'

    # Property name for published tag
    PUBLISHED_TAG_PROPERTY_NAME = 'published_tag'
    # Property name for last updated timestamp
    LAST_UPDATED_EPOCH_MS = 'publisher_last_updated_epoch_ms'


class PublishBehaviorConfigs:
    # A boolean flag to indicate if publisher_metadata (e.g. published_tag,
    # publisher_last_updated_epoch_ms)
    # will be included as properties of the nodes
    ADD_PUBLISHER_METADATA = 'add_publisher_metadata'

    # NOTE: Do not use this unless you have a specific use case for it. Amundsen expects two way relationships, and
    # the default value should be set to true to publish relations in both directions. If it is overridden and set
    # to false, reverse relationships will not be published.
    PUBLISH_REVERSE_RELATIONSHIPS = 'publish_reverse_relationships'

    # If enabled, stops the publisher from updating a node or relationship
    # created via the UI, e.g. a description or owner added manually by an Amundsen user.
    # Such nodes/relationships will not have a 'published_tag' property that is set by databuilder.
    PRESERVE_ADHOC_UI_DATA = 'preserve_adhoc_ui_data'

    # If enabled, the default behavior will continue to publish properties with empty values.
    # If False, empty properties will be set to NULL and will not show up on the node or relation.
    PRESERVE_EMPTY_PROPS = 'preserve_empty_props'


class Neo4jCsvPublisherConfigs:
    # A end point for Neo4j e.g: bolt://localhost:9999
    NEO4J_END_POINT_KEY = 'neo4j_endpoint'
    # A transaction size that determines how often it commits.
    NEO4J_TRANSACTION_SIZE = 'neo4j_transaction_size'

    NEO4J_MAX_CONN_LIFE_TIME_SEC = 'neo4j_max_conn_life_time_sec'

    # list of nodes that are create only, and not updated if match exists
    NEO4J_CREATE_ONLY_NODES = 'neo4j_create_only_nodes'

    NEO4J_USER = 'neo4j_user'
    NEO4J_PASSWORD = 'neo4j_password'
    # in Neo4j (v4.0+), we can create and use more than one active database at the same time
    NEO4J_DATABASE_NAME = 'neo4j_database'

    # NEO4J_ENCRYPTED is a boolean indicating whether to use SSL/TLS when connecting
    NEO4J_ENCRYPTED = 'neo4j_encrypted'
    # NEO4J_VALIDATE_SSL is a boolean indicating whether to validate the server's SSL/TLS
    # cert against system CAs
    NEO4J_VALIDATE_SSL = 'neo4j_validate_ssl'
