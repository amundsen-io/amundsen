# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from collections import namedtuple
from common.amundsen_common.utils.atlas import AtlasSerializedEntityFields

AtlasEntity = namedtuple(
    'AtlasEntity',
    [
        'operation',
        'typeName',
        'relationships',
        'attributes'
    ]
)
