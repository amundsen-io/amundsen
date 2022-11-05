# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0


class MailClientNotImplemented(Exception):
    """
    An exception when Mail Client is not implemented
    """
    pass


class AuthorizationMappingMissingException(Exception):
    """
    An exception raised when mapping from given request to required action is missing
    """
    pass
