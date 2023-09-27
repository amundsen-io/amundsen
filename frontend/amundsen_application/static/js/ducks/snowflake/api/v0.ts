import axios, { AxiosResponse } from 'axios';

import { SnowflakeTableShare } from 'interfaces';
import { sortSnowflakeTableSharesAlphabetical } from 'ducks/utilMethods';


export const API_PATH = '/api/snowflake/v0';

export type SnowflakeTableSharesAPI = {
  msg: string;
  snowflake_table_shares: SnowflakeTableShare[];
};

export function getSnowflakeTableShares(tableUri: string) {
  return axios
  .get(`${API_PATH}/get_snowflake_table_shares?tableUri=${encodeURIComponent(tableUri)}`)
    .then((response: AxiosResponse<SnowflakeTableSharesAPI>) =>
      response.data.snowflake_table_shares.sort(sortSnowflakeTableSharesAlphabetical)
    );
}