# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import pathlib
import re
from datetime import datetime

from feast import (
    Entity, Feature, FeatureView, FileSource, KafkaSource, ValueType,
)
from feast.data_format import AvroFormat
from google.protobuf.duration_pb2 import Duration

# Read data from parquet files. Parquet is convenient for local development mode. For
# production, you can use your favorite DWH, such as BigQuery. See Feast documentation
# for more info.

root_path = pathlib.Path(__file__).parent.resolve()
driver_hourly_stats = FileSource(
    path=f"{root_path}/data/driver_stats.parquet",
    event_timestamp_column="event_timestamp",
    created_timestamp_column="created",
)

driver_hourly_stats_kafka_source = KafkaSource(
    bootstrap_servers="broker1",
    event_timestamp_column="datetime",
    created_timestamp_column="datetime",
    topic="driver_hourly_stats",
    message_format=AvroFormat(
        schema_json=re.sub(
            "\n[ \t]*\\|",
            "",
            """'{"type": "record",
                 |"name": "driver_hourly_stats",
                 |"fields": [
                 | {"name": "conv_rate", "type": "float"},
                 | {"name": "acc_rate", "type": "float"},
                 | {"name": "avg_daily_trips", "type": "int"},
                 | {"name": "datetime", "type": {"type": "long", "logicalType": "timestamp-micros"}}]}'""",
        )
    ),
)

# Define an entity for the driver. You can think of entity as a primary key used to
# fetch features.
driver = Entity(
    name="driver_id",
    value_type=ValueType.INT64,
    description="Internal identifier of the driver",
)

# Our parquet files contain sample data that includes a driver_id column, timestamps and
# three feature column. Here we define a Feature View that will allow us to serve this
# data to our model online.
driver_hourly_stats_view = FeatureView(
    name="driver_hourly_stats",
    entities=["driver_id"],
    ttl=Duration(seconds=86400 * 1),
    features=[
        Feature(name="conv_rate", dtype=ValueType.FLOAT),
        Feature(name="acc_rate", dtype=ValueType.FLOAT),
        Feature(name="avg_daily_trips", dtype=ValueType.INT64),
    ],
    online=True,
    stream_source=driver_hourly_stats_kafka_source,
    batch_source=driver_hourly_stats,
    tags={"is_pii": "true"},
)

driver_hourly_stats_view.created_timestamp = datetime.strptime(
    "2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
)
