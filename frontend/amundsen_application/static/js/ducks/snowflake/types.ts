// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { SnowflakeTableShare } from 'interfaces';

export enum GetSnowflakeTableShares {
  REQUEST = 'amundsen/snowflake/table/shares/GET_SNOWFLAKE_TABLE_SHARES_REQUEST',
  SUCCESS = 'amundsen/snowflake/table/shares/GET_SNOWFLAKE_TABLE_SHARES_SUCCESS',
  FAILURE = 'amundsen/snowflake/table/shares/GET_SNOWFLAKE_TABLE_SHARES_FAILURE',
}
export interface GetSnowflakeTableSharesRequest {
  type: GetSnowflakeTableShares.REQUEST;
  payload: {
    tableUri: string;
  };
}
export interface GetSnowflakeTableSharesResponse {
  type: GetSnowflakeTableShares.SUCCESS | GetSnowflakeTableShares.FAILURE;
  payload: {
    snowflakeTableShares: SnowflakeTableShare[];
    // statusCode: number;
  };
}
