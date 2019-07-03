import axios, { AxiosResponse, AxiosError } from 'axios';

import {
  GetPreviewDataRequest, GetTableDataRequest, UpdateTableOwnerRequest, UpdateTagsRequest,
} from 'ducks/tableMetadata/types';

import { PreviewData, PreviewQueryParams, TableMetadata, User, Tag } from 'interfaces';

const API_PATH = '/api/metadata/v0';

// TODO: Consider created shared interfaces for ducks so we can reuse MessageAPI everywhere else
type MessageAPI = { msg: string };

export type TableData = TableMetadata & {
  owners: User[];
  tags: Tag[];
};
export type DescriptionAPI = { description: string; } & MessageAPI;
export type LastIndexedAPI = { timestamp: string; } & MessageAPI;
export type PreviewDataAPI = { previewData: PreviewData; } & MessageAPI;
export type TableDataAPI= { tableData: TableData; } & MessageAPI;

/** HELPERS **/
import {
  getTableQueryParams, getTableDataFromResponseData, getTableOwnersFromResponseData, getTableTagsFromResponseData,
} from './helpers';

export function metadataTableTags(tableKey: string) {
  const tableParams = getTableQueryParams(tableKey);
  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`)
  .then((response: AxiosResponse<TableDataAPI>) => {
    return getTableTagsFromResponseData(response.data);
  });
}

/* TODO: Typing this method generates redux-saga related type errors that needs more dedicated debugging */
export function metadataUpdateTableTags(tagArray, tableKey: string) {
  const updatePayloads = tagArray.map((tagObject) => {
    return {
      method: tagObject.methodName,
      url: `${API_PATH}/update_table_tags`,
      data: {
        key: tableKey,
        tag: tagObject.tagName,
      },
    }
  });
  return updatePayloads.map(payload => { axios(payload) });
}

export function metadataGetTableData(tableKey: string, searchIndex: string, source: string ) {
  const tableParams = getTableQueryParams(tableKey);
  return axios.get(`${API_PATH}/table?${tableParams}&index=${searchIndex}&source=${source}`)
  .then((response: AxiosResponse<TableDataAPI>) => {
    return {
      data: getTableDataFromResponseData(response.data),
      owners: getTableOwnersFromResponseData(response.data),
      tags: getTableTagsFromResponseData(response.data),
      statusCode: response.status,
    };
  });
}

export function metadataGetTableDescription(tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData.key);
  return axios.get(`${API_PATH}/v0/get_table_description?${tableParams}`)
  .then((response: AxiosResponse<DescriptionAPI>) => {
    tableData.table_description = response.data.description;
    return tableData;
  });
}

export function metadataUpdateTableDescription(description: string, tableData: TableMetadata) {
  if (description.length === 0) {
    throw new Error();
  }
  else {
    return axios.put(`${API_PATH}/put_table_description`, {
      description,
      key: tableData.key,
      source: 'user',
    });
  }
}

export function metadataTableOwners(tableKey: string) {
  const tableParams = getTableQueryParams(tableKey);
  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`)
  .then((response: AxiosResponse<TableDataAPI>) => {
    return getTableOwnersFromResponseData(response.data);
  });
}

/* TODO: Typing this method generates redux-saga related type errors that need more dedicated debugging */
export function metadataUpdateTableOwner(updateArray, tableKey: string) {
  const updatePayloads = updateArray.map((item) => {
    return {
      method: item.method,
      url: `${API_PATH}/update_table_owner`,
      data: {
        key: tableKey,
        owner: item.id,
      },
    }
  });
  return updatePayloads.map(payload => { axios(payload) });
}

export function metadataGetColumnDescription(columnIndex: number, tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData.key);
  const columnName = tableData.columns[columnIndex].name;
  return axios.get(`${API_PATH}/get_column_description?${tableParams}&column_name=${columnName}`)
  .then((response: AxiosResponse<DescriptionAPI>) => {
    tableData.columns[columnIndex].description = response.data.description;
    return tableData;
  });
}

export function metadataUpdateColumnDescription(description: string, columnIndex: number, tableData: TableMetadata) {
  if (description.length === 0) {
    throw new Error();
  }
  else {
    const columnName = tableData.columns[columnIndex].name;
    return axios.put(`${API_PATH}/put_column_description`, {
      description,
      column_name: columnName,
      key: tableData.key,
      source: 'user',
    });
  }
}

export function metadataGetLastIndexed() {
  return axios.get(`${API_PATH}/get_last_indexed`)
  .then((response: AxiosResponse<LastIndexedAPI>) => {
    return response.data.timestamp;
  });
}

export function metadataGetPreviewData(queryParams: PreviewQueryParams) {
  return axios({
    url: '/api/preview/v0/',
    method: 'POST',
    data: queryParams,
  })
  .then((response: AxiosResponse<PreviewDataAPI>) => {
    return { data: response.data.previewData, status: response.status };
  });
}
