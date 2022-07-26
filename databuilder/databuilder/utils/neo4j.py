# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import neo4j
from typing import Tuple
from neo4j import Driver, GraphDatabase


def create_neo4j_driver(uri: str,
                        max_connection_lifetime: int,
                        auth: Tuple[str],
                        validate_ssl: bool = None,
                        encrypted: bool = None) -> Driver:
    driver_args = {
        'uri': uri,
        'max_connection_lifetime': max_connection_lifetime,
        'auth': auth
    }
    if validate_ssl is not None:
        driver_args['trust'] = neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES if validate_ssl \
            else neo4j.TRUST_ALL_CERTIFICATES
    if encrypted is not None:
        driver_args['encrypted'] = encrypted

    return GraphDatabase.driver(**driver_args)
