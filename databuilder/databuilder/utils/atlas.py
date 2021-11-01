# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

class AtlasRelationshipTypes:
    group_dashboard = 'DashboardGroup__Dashboard'
    resource_owner = 'DataSet_Users_Owner'
    dashboard_query = 'Dashboard__DashboardQuery'
    query_chart = 'DashboardQuery__DashboardChart'
    dashboard_execution = 'Dashboard__DashboardExecution'
    table_dashboard = 'Table__Dashboard'
    dashboard_owner = 'Dashboard_Users_Owner'
    table_application = 'DataSet__Application'
    table_source = 'Source__Tables'
    lineage_upstream = 'dataset_process_inputs'
    lineage_downstream = 'process_dataset_outputs'
    referenceable_reader = 'Referenceable_Readers'
    reader_user = 'Reader_Users'
    referenceable_report = 'Referenceable__Report'

    # These are just `virtual` relationship types which do not actually exist in Atlas.
    # We use those constant values to distinguish Atlas Python Client methods which should be used for populating
    # such data.
    # Tags are published using Glossary API, badges using Classification API. Other entities are published using regular
    # Entity API.
    tag = 'AtlasGlossaryTerm'
    badge = 'AtlasClassification'


class AtlasSerializedRelationshipFields:
    relation_type = 'relationshipType'
    entity_type_1 = 'entityType1'
    qualified_name_1 = 'entityQualifiedName1'
    entity_type_2 = 'entityType2'
    qualified_name_2 = 'entityQualifiedName2'


class AtlasSerializedEntityFields:
    operation = 'operation'
    relationships = 'relationships'
    type_name = 'typeName'
    attributes = 'attributes'
    relationships_separator = '|'
    relationships_kv_separator = '#'


class AtlasSerializedEntityOperation:
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
