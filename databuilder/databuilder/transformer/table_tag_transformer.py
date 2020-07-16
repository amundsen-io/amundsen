# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from pyhocon import ConfigFactory

from databuilder.transformer.base_transformer import Transformer
from databuilder.models.table_metadata import TableMetadata


class TableTagTransformer(Transformer):
    """Simple transformer that adds tags to all table nodes produced as part of a job."""
    # Config
    TAGS = 'tags'
    DEFAULT_CONFIG = ConfigFactory.from_dict({TAGS: None})

    def init(self, conf):
        conf = conf.with_fallback(TableTagTransformer.DEFAULT_CONFIG)
        tags = conf.get_string(TableTagTransformer.TAGS)

        self.tags = TableMetadata.format_tags(tags)

    def transform(self, record):
        if isinstance(record, TableMetadata):
            if record.tags:
                record.tags += self.tags
            else:
                record.tags = self.tags
        return record

    def get_scope(self):
        # type: () -> str
        return 'transformer.table_tag'
