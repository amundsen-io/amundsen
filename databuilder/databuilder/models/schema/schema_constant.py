# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

SCHEMA_NODE_LABEL = 'Schema'

SCHEMA_NAME_ATTR = 'name'

SCHEMA_RELATION_TYPE = 'SCHEMA'
SCHEMA_REVERSE_RELATION_TYPE = 'SCHEMA_OF'

DATABASE_SCHEMA_KEY_FORMAT = '{db}://{cluster}.{schema}'
DATABASE_SCHEMA_DESCRIPTION_FORMAT = DATABASE_SCHEMA_KEY_FORMAT + "/{desc}"
DATABASE_SCHEMA_KEY_DESCRIPTION_FORMAT = '{schema_key}/{desc}'

# pattern used to match a schema key, e.g., hive://gold.test_schema
SCHEMA_KEY_PATTERN_REGEX = '([a-zA-Z0-9_]+://[a-zA-Z0-9_-]+).[a-zA-Z0-9_.-]+'
