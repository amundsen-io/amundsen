# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from amundsen_application.authz.actions.rw_action import RWAction
from amundsen_application.authz.mappers.default_request_to_action_mapper import DefaultRequestToActionMapper
from amundsen_application.authz.clients.casbin_example_csv_client import CasbinExampleCsvClient

AUTHORIZATION_ENABLED = True
AUTHORIZATION_CLIENT_CLASS = CasbinExampleCsvClient
AUTHORIZATION_REQUEST_TO_ACTION_MAPPER = DefaultRequestToActionMapper()
AUTHORIZATION_ACTION_ENUM = RWAction
AUTHORIZATION_ALLOW_ACCESS_ON_MISSING_MAPPING = True


# Subject accessing 'get_table_metadata' defined in blueprint 'metadata'
# has to have 'read' action allowed in order to access the table metadata
AUTHORIZATION_REQUEST_TO_ACTION_MAPPER.add_mapping(
    blueprint_name="metadata",
    function_name="get_table_metadata",
    required_action=AUTHORIZATION_ACTION_ENUM.READ,
)


"""
# One can follow the same logic to add more mappings...

AUTHORIZATION_REQUEST_TO_ACTION_MAPPER.add_mapping(
    blueprint_name="metadata",
    function_name="update_table_tags",
    required_action=AUTHORIZATION_ACTION_ENUM.WRITE,
)
"""
