# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc

import six
from requests.exceptions import HTTPError
from typing import Iterable, Union, List, Dict, Any, Optional  # noqa: F401


@six.add_metaclass(abc.ABCMeta)
class BaseFailureHandler(object):

    @abc.abstractmethod
    def can_skip_failure(self,
                         exception,  # type: Exception
                         ):
        # type: (...) -> bool
        pass


class HttpFailureSkipOnStatus(BaseFailureHandler):

    def __init__(self,
                 status_codes_to_skip,  # type: Iterable[int]
                 ):
        # type: (...) -> None
        self._status_codes_to_skip = {v for v in status_codes_to_skip}

    def can_skip_failure(self,
                         exception,  # type: Exception
                         ):
        # type: (...) -> bool

        if (isinstance(exception, HTTPError) or hasattr(exception, 'response')) \
                and exception.response.status_code in self._status_codes_to_skip:
            return True

        return False
