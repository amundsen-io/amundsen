import axios, { AxiosResponse, AxiosError } from 'axios';
import { Effect } from 'redux-saga';

import {
  GetPreviewDataRequest, GetTableDataRequest, UpdateTableOwnerRequest, UpdateTagsRequest,
} from 'ducks/tableMetadata/types';

import { PreviewData, PreviewQueryParams, TableMetadata, User, Tag } from 'interfaces';

const API_PATH = '/api/metadata/v0';

type MessageResponse = { msg: string };
type TableData = TableMetadata & {
  owners: User[];
  tags: Tag[];
};
export type DescriptionResponse = { description: string; } & MessageResponse;
export type LastIndexedResponse = { timestamp: string; } & MessageResponse;
export type PreviewDataResponse = { previewData: PreviewData; } & MessageResponse;
export type TableDataResponse = { tableData: TableData; } & MessageResponse;

/** HELPERS **/
import {
  getTableQueryParams, getTableDataFromResponseData, getTableOwnersFromResponseData, getTableTagsFromResponseData,
} from './helpers';

export function metadataTableTags(tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData);
  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`)
  .then((response: AxiosResponse<TableDataResponse>) => {
    return getTableTagsFromResponseData(response.data);
  });
}

/* TODO: Typing this method generates redux-saga related type errors that needs more dedicated debugging */
export function metadataUpdateTableTags(action, tableData) {
  const updatePayloads = action.tagArray.map((tagObject) => {
    return {
      method: tagObject.methodName,
      url: `${API_PATH}/update_table_tags`,
      data: {
        key: tableData.key,
        tag: tagObject.tagName,
      },
    }
  });
  return updatePayloads.map(payload => { axios(payload) });
}

export function metadataGetTableData(action: GetTableDataRequest) {
  const { searchIndex, source } = action;
  const tableParams = getTableQueryParams(action);

  return axios.get(`${API_PATH}/table?${tableParams}&index=${searchIndex}&source=${source}`)
  .then((response: AxiosResponse<TableDataResponse>) => {
    return {
      data: getTableDataFromResponseData(response.data),
      owners: getTableOwnersFromResponseData(response.data),
      tags: getTableTagsFromResponseData(response.data),
      statusCode: response.status,
    };
  });
}

export function metadataGetTableDescription(tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData);
  return axios.get(`${API_PATH}/v0/get_table_description?${tableParams}`)
  .then((response: AxiosResponse<DescriptionResponse>) => {
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

export function metadataTableOwners(tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData);
  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`)
  .then((response: AxiosResponse<TableDataResponse>) => {
    return getTableOwnersFromResponseData(response.data);
  });
}

/* TODO: Typing this method generates redux-saga related type errors that need more dedicated debugging */
// TODO - Add 'key' to the action and remove 'tableData' as a param.
export function metadataUpdateTableOwner(action, tableData: TableMetadata) {
  const updatePayloads = action.updateArray.map((item) => {
    return {
      method: item.method,
      url: `${API_PATH}/update_table_owner`,
      data: {
        key: tableData.key,
        owner: item.id,
      },
    }
  });
  return updatePayloads.map(payload => { axios(payload) });
}

export function metadataGetColumnDescription(columnIndex: number, tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData);
  const columnName = tableData.columns[columnIndex].name;
  return axios.get(`${API_PATH}/get_column_description?${tableParams}&column_name=${columnName}`)
  .then((response: AxiosResponse<DescriptionResponse>) => {
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
  .then((response: AxiosResponse<LastIndexedResponse>) => {
    return response.data.timestamp;
  });
}

export function metadataGetPreviewData(queryParams: PreviewQueryParams) {
  return axios({
    url: '/api/preview/v0/',
    method: 'POST',
    data: queryParams,
  })
  .then((response: AxiosResponse<PreviewDataResponse>) => {
    return { data: response.data.previewData, status: response.status };
  });
}
