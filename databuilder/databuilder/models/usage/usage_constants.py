# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from databuilder.publisher.neo4j_csv_publisher import UNQUOTED_SUFFIX


READ_RELATION_TYPE = 'READ'
READ_REVERSE_RELATION_TYPE = 'READ_BY'

READ_RELATION_COUNT_PROPERTY = 'read_count{}'.format(UNQUOTED_SUFFIX)
