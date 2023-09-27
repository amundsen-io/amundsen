# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from typing import Union, List

from amundsen_common.models.snowflake.snowflake import SnowflakeTableShare



class SnowflakeBaseProxy(metaclass=ABCMeta):
    
    @abstractmethod
    def get_snowflake_table_shares(self, *, table_uri: str) -> Union[List[SnowflakeTableShare], None]:
        pass

    
