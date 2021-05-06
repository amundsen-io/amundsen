import { getTableQueryParams } from 'ducks/tableMetadata/api/helpers';
import axios, { AxiosError, AxiosResponse } from 'axios';
import { Lineage } from 'interfaces/Lineage';

export const API_PATH = '/api/metadata/v0';

export type LineageAPI = { lineage: Lineage };

export function getTableLineage(key: string) {
  const tableQueryParams = getTableQueryParams({ key });
  return axios({
    url: `${API_PATH}/get_table_lineage?${tableQueryParams}`,
    method: 'GET',
  })
    .then((response: AxiosResponse<LineageAPI>) => ({
      data: response.data,
      status: response.status,
    }))
    .catch((e: AxiosError<LineageAPI>) => {
      const { response } = e;
      const status = response ? response.status : null;
      return Promise.reject({ status });
    });
}

export function getColumnLineage(key: string, columnName: string) {
  const tableQueryParams = getTableQueryParams({
    key,
    column_name: columnName,
  });
  return axios({
    url: `${API_PATH}/get_column_lineage?${tableQueryParams}`,
    method: 'GET',
  })
    .then((response: AxiosResponse<LineageAPI>) => ({
      data: response.data,
      status: response.status,
    }))
    .catch((e: AxiosError<LineageAPI>) => {
      const { response } = e;
      const status = response ? response.status : null;
      return Promise.reject({ status });
    });
}
