import axios, { AxiosResponse, AxiosError } from 'axios';

import { PreviewData, PreviewQueryParams, TableMetadata, UpdateOwnerPayload, User, Tag } from 'interfaces';

export const API_PATH = '/api/metadata/v0';

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
  getTableQueryParams, getTableDataFromResponseData, getTableOwnersFromResponseData,
  createOwnerUpdatePayload, createOwnerNotificationData, shouldSendNotification
} from './helpers';


export function getTableData(tableKey: string, index?: string, source?: string ) {
  const queryParams = getTableQueryParams(tableKey, index, source);
  return axios.get(`${API_PATH}/table?${queryParams}`)
  .then((response: AxiosResponse<TableDataAPI>) => {
    return {
      data: getTableDataFromResponseData(response.data),
      owners: getTableOwnersFromResponseData(response.data),
      tags: response.data.tableData.tags,
      statusCode: response.status,
    };
  });
}

export function getTableDescription(tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData.key);
  return axios.get(`${API_PATH}/get_table_description?${tableParams}`)
  .then((response: AxiosResponse<DescriptionAPI>) => {
    tableData.description = response.data.description;
    return tableData;
  });
}

export function updateTableDescription(description: string, tableData: TableMetadata) {
  return axios.put(`${API_PATH}/put_table_description`, {
    description,
    key: tableData.key,
    source: 'user',
  });
}

export function getTableOwners(tableKey: string) {
  const tableParams = getTableQueryParams(tableKey);
  return axios.get(`${API_PATH}/table?${tableParams}`)
  .then((response: AxiosResponse<TableDataAPI>) => {
    return getTableOwnersFromResponseData(response.data);
  });
}

/* TODO: Typing return type generates redux-saga related type error that need more dedicated debugging */
export function generateOwnerUpdateRequests(updateArray: UpdateOwnerPayload[], tableData: TableMetadata) {
  const updateRequests = [];

  /* Create the request for updating each owner*/
  updateArray.forEach((item) => {
    const updatePayload = createOwnerUpdatePayload(item, tableData.key);
    const notificationData = createOwnerNotificationData(item, tableData);

    /* Chain requests to send notification on success to desired users */
    const request =
      axios(updatePayload)
      .then((response) => {
        return axios.get(`/api/metadata/v0/user?user_id=${item.id}`)
      })
      .then((response) => {
        if(shouldSendNotification(response.data.user)) {
          return axios.post('/api/mail/v0/notification', notificationData);
        }
      });

    updateRequests.push(request);
  });

  /* Return the list of requests to be executed */
  return updateRequests;
}

export function getColumnDescription(columnIndex: number, tableData: TableMetadata) {
  const tableParams = getTableQueryParams(tableData.key);
  const columnName = tableData.columns[columnIndex].name;
  return axios.get(`${API_PATH}/get_column_description?${tableParams}&column_name=${columnName}`)
  .then((response: AxiosResponse<DescriptionAPI>) => {
    tableData.columns[columnIndex].description = response.data.description;
    return tableData;
  });
}

export function updateColumnDescription(description: string, columnIndex: number, tableData: TableMetadata) {
  const columnName = tableData.columns[columnIndex].name;
  return axios.put(`${API_PATH}/put_column_description`, {
    description,
    column_name: columnName,
    key: tableData.key,
    source: 'user',
  });
}

export function getLastIndexed() {
  return axios.get(`${API_PATH}/get_last_indexed`)
  .then((response: AxiosResponse<LastIndexedAPI>) => {
    return response.data.timestamp;
  });
}

export function getPreviewData(queryParams: PreviewQueryParams) {
  return axios({
    url: '/api/preview/v0/',
    method: 'POST',
    data: queryParams,
  })
  .then((response: AxiosResponse<PreviewDataAPI>) => {
    return { data: response.data.previewData, status: response.status };
  })
  .catch((e: AxiosError<PreviewDataAPI>) => {
    const response = e.response;
    let data = {};
    if (response && response.data && response.data.previewData) {
      data = response.data.previewData;
    }
    const status = response ? response.status : null;
    return Promise.reject({ data, status });
  });
}
