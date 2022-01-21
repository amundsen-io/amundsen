# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
import os
from typing import Dict

import boto3
from amundsen_application.base.base_s3_preview_client import \
    BaseS3PreviewClient
from amundsen_application.models.preview_data import ColumnItem, PreviewData


class S3JSONPreviewClient(BaseS3PreviewClient):
    """
    S3JSONPreviewClient is an S3 Preview Client that:
    1. Gets JSON files from S3 that are stored in a bucket with keys preview_data/{schema}/{table}.json
    2. Converts the JSON values to PreviewData model
    3. Returns the serialized model

    In order for this preview client to work you must:
    - Have S3 files stored in a bucket with keys 'preview_data/{schema}/{table}.json'
    - Files are formatted as list of rows as map with key being the column name and value being column value
      Ex:
    [
      {
        'col1': 1,
        'col2': '2'
      },
      {
        'col1': 3,
        'col2': '4'
      }
      ...
    ]
    - Nested field are not supported. We suggest flattening your nested fields.
      Ex:
        [
          {
            'col1': {
              'col2: 1
          }
        ]
      should be:
        [
          {
            'col1.col2': 1
          }
        ]
    - Run your frontend service with an IAM Profile that has s3:GetObject permissions on the 'preview_data/' prefix
    """

    def __init__(self) -> None:
        self.s3 = boto3.client("s3")
        bucket = os.getenv("PREVIEW_CLIENT_S3_BUCKET")
        if bucket == "":
            raise Exception("When using the S3CSVPreviewClient you must set the PREVIEW_CLIENT_S3_BUCKET environment "
                            "variable to point to where your preview_data CSVs are stored.")
        self.s3_bucket = bucket

    def get_s3_preview_data(self, *, params: Dict) -> PreviewData:
        schema = params.get("schema")
        table = params.get("tableName")

        try:
            obj = self.s3.get_object(Bucket=self.s3_bucket, Key=f"preview_data/{schema}/{table}.json")
        except Exception as e:
            raise Exception(f"Error getting object from s3. preview_data/{schema}/{table}.json"
                            f"Caused by: {e}")

        data = json.loads(obj['Body'].read().decode('utf-8'))
        columns = [ColumnItem(col_name, '') for col_name in data[0]]  # TODO: figure out how to do Type. Is it needed?
        return PreviewData(columns=columns, data=data)
