# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import ANY

from databuilder.serializers.neptune_serializer import (
    NEPTUNE_CREATION_TYPE_JOB, NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT,
    NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_HEADER_ID, NEPTUNE_HEADER_LABEL,
    NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT, NEPTUNE_RELATIONSHIP_HEADER_FROM,
    NEPTUNE_RELATIONSHIP_HEADER_TO,
)

EXPECTED_NEPTUNE_NODES = [
    {
        'name:String(single)': 'test_table1',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1',
        NEPTUNE_HEADER_LABEL: 'Table',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        'is_view:Bool(single)': False
    },
    {
        'description:String(single)': 'test_table1',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/_description',
        NEPTUNE_HEADER_LABEL: 'Description',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        'description_source:String(single)': 'description'
    },
    {
        'sort_order:Long(single)': 0,
        'type:String(single)': 'bigint',
        'name:String(single)': 'test_id1',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/test_id1',
        NEPTUNE_HEADER_LABEL: 'Column'
    },
    {
        'description:String(single)': 'description of test_table1',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/test_id1/_description',
        NEPTUNE_HEADER_LABEL: 'Description',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        'description_source:String(single)': 'description'
    },
    {
        'sort_order:Long(single)': 1,
        'type:String(single)': 'bigint',
        'name:String(single)': 'test_id2',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/test_id2',
        NEPTUNE_HEADER_LABEL: 'Column',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'description:String(single)': 'description of test_id2',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/test_id2/_description',
        NEPTUNE_HEADER_LABEL: 'Description',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        'description_source:String(single)': 'description'
    },
    {
        'sort_order:Long(single)': 2,
        'type:String(single)': 'boolean',
        'name:String(single)': 'is_active',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/is_active',
        NEPTUNE_HEADER_LABEL: 'Column',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'sort_order:Long(single)': 3,
        'type:String(single)': 'varchar',
        'name:String(single)': 'source',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/source',
        NEPTUNE_HEADER_LABEL: 'Column',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'description:String(single)': 'description of source',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/source/_description',
        NEPTUNE_HEADER_LABEL: 'Description',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        'description_source:String(single)': 'description'
    },
    {
        'sort_order:Long(single)': 4,
        'type:String(single)': 'timestamp',
        'name:String(single)': 'etl_created_at',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/etl_created_at',
        NEPTUNE_HEADER_LABEL: 'Column',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'description:String(single)': 'description of etl_created_at',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/etl_created_at/_description',
        NEPTUNE_HEADER_LABEL: 'Description',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
        'description_source:String(single)': 'description'
    },
    {
        'sort_order:Long(single)': 5,
        'type:String(single)': 'varchar',
        'name:String(single)': 'ds',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1/test_table1/ds',
        NEPTUNE_HEADER_LABEL: 'Column',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'name:String(single)': 'hive',
        NEPTUNE_HEADER_ID: 'database://hive',
        NEPTUNE_HEADER_LABEL: 'Database',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'name:String(single)': 'gold',
        NEPTUNE_HEADER_ID: 'hive://gold',
        NEPTUNE_HEADER_LABEL: 'Cluster',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    },
    {
        'name:String(single)': 'test_schema1',
        NEPTUNE_HEADER_ID: 'hive://gold.test_schema1',
        NEPTUNE_HEADER_LABEL: 'Schema',
        NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
        NEPTUNE_CREATION_TYPE_NODE_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
    }
]

EXPECTED_RELATIONSHIPS_NEPTUNE = [
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='TABLE'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'TABLE',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1',
                label='TABLE_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1',
            NEPTUNE_HEADER_LABEL: 'TABLE_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/_description',
                label='DESCRIPTION'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/_description',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/_description',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='DESCRIPTION_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/_description',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/test_id1',
                label='COLUMN'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/test_id1',
            NEPTUNE_HEADER_LABEL: 'COLUMN',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/test_id1',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='COLUMN_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/test_id1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'COLUMN_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/test_id1',
                to_vertex_id='hive://gold.test_schema1/test_table1/test_id1/_description',
                label='DESCRIPTION'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/test_id1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/test_id1/_description',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/test_id1/_description',
                to_vertex_id='hive://gold.test_schema1/test_table1/test_id1',
                label='DESCRIPTION_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/test_id1/_description',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/test_id1',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/test_id2',
                label='COLUMN'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/test_id2',
            NEPTUNE_HEADER_LABEL: 'COLUMN',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/test_id2',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='COLUMN_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/test_id2',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'COLUMN_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/test_id2',
                to_vertex_id='hive://gold.test_schema1/test_table1/test_id2/_description',
                label='DESCRIPTION'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/test_id2',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/test_id2/_description',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/test_id2/_description',
                to_vertex_id='hive://gold.test_schema1/test_table1/test_id2',
                label='DESCRIPTION_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/test_id2/_description',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/test_id2',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/is_active',
                label='COLUMN'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/is_active',
            NEPTUNE_HEADER_LABEL: 'COLUMN',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/is_active',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='COLUMN_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/is_active',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'COLUMN_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/source',
                label='COLUMN'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/source',
            NEPTUNE_HEADER_LABEL: 'COLUMN',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/source',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='COLUMN_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/source',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'COLUMN_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/source',
                to_vertex_id='hive://gold.test_schema1/test_table1/source/_description',
                label='DESCRIPTION'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/source',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/source/_description',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/source/_description',
                to_vertex_id='hive://gold.test_schema1/test_table1/source',
                label='DESCRIPTION_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/source/_description',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/source',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/etl_created_at',
                label='COLUMN'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/etl_created_at',
            NEPTUNE_HEADER_LABEL: 'COLUMN',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/etl_created_at',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='COLUMN_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/etl_created_at',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'COLUMN_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/etl_created_at',
                to_vertex_id='hive://gold.test_schema1/test_table1/etl_created_at/_description',
                label='DESCRIPTION'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/etl_created_at',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/etl_created_at/_description',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/etl_created_at/_description',
                to_vertex_id='hive://gold.test_schema1/test_table1/etl_created_at',
                label='DESCRIPTION_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/etl_created_at/_description',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/etl_created_at',
            NEPTUNE_HEADER_LABEL: 'DESCRIPTION_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1',
                to_vertex_id='hive://gold.test_schema1/test_table1/ds',
                label='COLUMN'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1/ds',
            NEPTUNE_HEADER_LABEL: 'COLUMN',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        },
        {
            NEPTUNE_HEADER_ID: "{from_vertex_id}_{to_vertex_id}_{label}".format(
                from_vertex_id='hive://gold.test_schema1/test_table1/ds',
                to_vertex_id='hive://gold.test_schema1/test_table1',
                label='COLUMN_OF'
            ),
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1/test_table1/ds',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1/test_table1',
            NEPTUNE_HEADER_LABEL: 'COLUMN_OF',
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB
        }
    ],
    [
        {
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'database://hive',
            NEPTUNE_HEADER_ID: 'database://hive_hive://gold_CLUSTER',
            NEPTUNE_HEADER_LABEL: 'CLUSTER',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold'
        },
        {
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold',
            NEPTUNE_HEADER_ID: 'hive://gold_database://hive_CLUSTER_OF',
            NEPTUNE_HEADER_LABEL: 'CLUSTER_OF',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'database://hive'
        }
    ],
    [
        {
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold',
            NEPTUNE_HEADER_ID: 'hive://gold_hive://gold.test_schema1_SCHEMA',
            NEPTUNE_HEADER_LABEL: 'SCHEMA',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold.test_schema1'
        },
        {
            NEPTUNE_CREATION_TYPE_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: NEPTUNE_CREATION_TYPE_JOB,
            NEPTUNE_LAST_EXTRACTED_AT_RELATIONSHIP_PROPERTY_NAME_BULK_LOADER_FORMAT: ANY,
            NEPTUNE_RELATIONSHIP_HEADER_FROM: 'hive://gold.test_schema1',
            NEPTUNE_HEADER_ID: 'hive://gold.test_schema1_hive://gold_SCHEMA_OF',
            NEPTUNE_HEADER_LABEL: 'SCHEMA_OF',
            NEPTUNE_RELATIONSHIP_HEADER_TO: 'hive://gold'
        }
    ]
]
