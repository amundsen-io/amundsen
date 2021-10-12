# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import pathlib
import re
import unittest

from feast.entity import Entity
from feast.feature_table import FeatureTable
from pyhocon import ConfigFactory

from databuilder import Scoped
from databuilder.extractor.feast_extractor import FeastExtractor
from databuilder.models.table_metadata import (
    ColumnMetadata, DescriptionMetadata, TableMetadata,
)


class TestFeastExtractor(unittest.TestCase):

    def test_feature_view_extraction(self) -> None:
        self._init_extractor(programmatic_description_enabled=False)

        table = self.extractor.extract()

        expected = TableMetadata(
            database="feast",
            cluster="local",
            schema="fs",
            name="driver_hourly_stats",
            description=None,
            columns=[
                ColumnMetadata(
                    "driver_id", "Internal identifier of the driver", "INT64", 0
                ),
                ColumnMetadata("conv_rate", None, "FLOAT", 1),
                ColumnMetadata("acc_rate", None, "FLOAT", 2),
                ColumnMetadata("avg_daily_trips", None, "INT64", 3),
            ],
        )

        self.assertEqual(expected.__repr__(), table.__repr__())

    def test_feature_table_extraction_with_description_batch(self) -> None:
        self._init_extractor(programmatic_description_enabled=True)

        root_tests_path = pathlib.Path(__file__).parent.parent.resolve()
        feature_table_definition = self.extractor.extract()
        assert isinstance(feature_table_definition, TableMetadata)

        description = self.extractor.extract()
        assert isinstance(description, TableMetadata)
        expected = DescriptionMetadata(
            TestFeastExtractor._strip_margin(
                """* Created at **2020-01-01 03:00:00**
                  |* Tags:
                  |    * is_pii: **true**
                  |"""
            ),
            "feature_view_details",
        )
        self.assertEqual(expected.__repr__(), description.description.__repr__())

        batch_source = self.extractor.extract()
        assert isinstance(batch_source, TableMetadata)
        expected = DescriptionMetadata(
            TestFeastExtractor._strip_margin(
                f"""```
                |type: BATCH_FILE
                |event_timestamp_column: "event_timestamp"
                |created_timestamp_column: "created"
                |file_options {"{"}
                |  file_url: "{root_tests_path}/resources/extractor/feast/fs/data/driver_stats.parquet"
                |{"}"}
                |```"""
            ),
            "batch_source",
        )
        self.assertEqual(expected.__repr__(), batch_source.description.__repr__())


    def test_feature_table_extraction_with_description_stream(self) -> None:
        self._init_extractor(programmatic_description_enabled=True)
        root_tests_path = pathlib.Path(__file__).parent.parent.resolve()

        feature_table_definition = self.extractor.extract()
        assert isinstance(feature_table_definition, TableMetadata)

        description = self.extractor.extract()
        assert isinstance(description, TableMetadata)
        expected = DescriptionMetadata(
            TestFeastExtractor._strip_margin(
                """* Created at **2020-01-01 03:00:00**
                  |* Tags:
                  |    * is_pii: **true**
                  |"""
            ),
            "feature_view_details",
        )
        self.assertEqual(expected.__repr__(), description.description.__repr__())

        batch_source = self.extractor.extract()
        assert isinstance(batch_source, TableMetadata)
        expected = DescriptionMetadata(
            TestFeastExtractor._strip_margin(
                f"""```
                |type: BATCH_FILE
                |event_timestamp_column: "event_timestamp"
                |created_timestamp_column: "created"
                |file_options {"{"}
                |  file_url: "{root_tests_path}/resources/extractor/feast/fs/data/driver_stats.parquet"
                |{"}"}
                |```"""
            ),
            "batch_source",
        )
        self.assertEqual(expected.__repr__(), batch_source.description.__repr__())

        stream_source = self.extractor.extract()
        assert isinstance(stream_source, TableMetadata)
        expected = DescriptionMetadata(
            TestFeastExtractor._strip_margin(
                """```
                 |type: STREAM_KAFKA
                 |event_timestamp_column: "datetime"
                 |created_timestamp_column: "datetime"
                 |kafka_options {
                 |  bootstrap_servers: "broker1"
                 |  topic: "driver_hourly_stats"
                 |  message_format {
                 |    avro_format {
                 |      schema_json: "\\\'{\\"type\\": \\"record\\", \\"name\\": \\"driver_hourly_stats\\", \\"fields\\": [ {\\"name\\": \\"conv_rate\\", \\"type\\": \\"float\\"},  {\\"name\\": \\"acc_rate\\", \\"type\\": \\"float\\"}, {\\"name\\": \\"avg_daily_trips\\", \\"type\\": \\"int\\"}, {\\"name\\": \\"datetime\\", \\"type\\": {\\"type\\": \\"long\\", \\"logicalType\\": \\"timestamp-micros\\"}}]}\\\'"
                 |    }
                 |  }
                 |}
                 |```"""
            ),
            "stream_source",
        )
        self.assertEqual(expected.__repr__(), stream_source.description.__repr__())


    def _init_extractor(self, programmatic_description_enabled: bool = True) -> None:
        conf = {
            f'extractor.feast.{FeastExtractor.FEAST_REPOSITORY_PATH}': '../resources/extractor/feast/fs',
            f'extractor.feast.{FeastExtractor.DESCRIBE_FEATURE_VIEWS}': programmatic_description_enabled,
        }
        self.extractor = FeastExtractor()
        self.extractor.init(
            Scoped.get_scoped_conf(
                conf=ConfigFactory.from_dict(conf), scope=self.extractor.get_scope()
            )
        )

    @staticmethod
    def _strip_margin(text: str) -> str:
        return re.sub("\n[ \t]*\\|", "\n", text)


if __name__ == "__main__":
    unittest.main()
