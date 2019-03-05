import axios, { AxiosResponse, AxiosError } from 'axios';
import { Effect } from 'redux-saga';

import {
  DescriptionResponse, LastIndexedResponse, PreviewDataResponse, TableDataResponse,
  GetPreviewDataRequest, GetTableDataRequest, UpdateTableOwnerRequest, UpdateTagsRequest,
  PreviewData, TableMetadata, User, Tag
} from '../../tableMetadata/types';

const API_PATH = '/api/metadata/v0';

/** HELPERS **/
import {
  getTableParams, getTableDataFromResponseData, getTableOwnersFromResponseData, getTableTagsFromResponseData,
} from './helpers';

export function metadataTableTags(tableData: TableMetadata) {
  const tableParams = getTableParams(tableData);

  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`)
  .then((response: AxiosResponse<TableDataResponse>) => {
    return getTableTagsFromResponseData(response.data);
  })
  .catch((error: AxiosError) => {
    return [];
  });
}

/* TODO: Typing this method generates redux-saga related type errors that needs more dedicated debugging */
export function metadataUpdateTableTags(action, tableData) {
  const updatePayloads = action.tagArray.map((tagObject) => {
    return {
      method: tagObject.methodName,
      url: `${API_PATH}/update_table_tags`,
      data: {
        cluster: tableData.cluster,
        db: tableData.database,
        schema: tableData.schema,
        table: tableData.table_name,
        tag: tagObject.tagName,
      },
    }
  });
  return updatePayloads.map(payload => { axios(payload) });
}

export function metadataGetTableData(action: GetTableDataRequest) {
  const { searchIndex, source } = action;
  const tableParams = getTableParams(action);

  return axios.get(`${API_PATH}/table?${tableParams}&index=${searchIndex}&source=${source}`)
  .then((response: AxiosResponse<TableDataResponse>) => {
    return {
      data: getTableDataFromResponseData(response.data),
      owners: getTableOwnersFromResponseData(response.data),
      tags: getTableTagsFromResponseData(response.data),
      statusCode: response.status,
    };
  })
  .catch((error: AxiosError) => {
    const statusCode = error.response ? error.response.status : 500;
    return { statusCode, data: {}, owners: {}, tags: [] };
  });
}

export function metadataGetTableDescription(tableData: TableMetadata) {
  const tableParams = getTableParams(tableData);
  return axios.get(`${API_PATH}/v0/get_table_description?${tableParams}`)
  .then((response: AxiosResponse<DescriptionResponse>) => {
    tableData.table_description = response.data.description;
    return tableData;
  })
  .catch((error: AxiosError) => {
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
      db: tableData.database,
      cluster: tableData.cluster,
      schema: tableData.schema,
      table: tableData.table_name,
      source: 'user',
    });
  }
}

export function metadataTableOwners(tableData: TableMetadata) {
  const tableParams = getTableParams(tableData);

  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`)
  .then((response: AxiosResponse<TableDataResponse>) => {
    return getTableOwnersFromResponseData(response.data);
  })
  .catch((error) => {
    return {};
  });
}

/* TODO: Typing this method generates redux-saga related type errors that need more dedicated debugging */
export function metadataUpdateTableOwner(action, tableData) {
  const updatePayloads = action.updateArray.map((item) => {
    return {
      method: item.method,
      url: `${API_PATH}/update_table_owner`,
      data: {
        cluster: tableData.cluster,
        db: tableData.database,
        owner: item.id,
        schema: tableData.schema,
        table: tableData.table_name,
      },
    }
  });
  return updatePayloads.map(payload => { axios(payload) });
}

export function metadataGetColumnDescription(columnIndex: number, tableData: TableMetadata) {
  const tableParams = getTableParams(tableData);
  const columnName = tableData.columns[columnIndex].name;
  return axios.get(`${API_PATH}/get_column_description?${tableParams}&column_name=${columnName}`)
  .then((response: AxiosResponse<DescriptionResponse>) => {
    tableData.columns[columnIndex].description = response.data.description;
    return tableData;
  })
  .catch((error: AxiosError) => {
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
      db: tableData.database,
      cluster: tableData.cluster,
      column_name: columnName,
      schema: tableData.schema,
      table: tableData.table_name,
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

export function metadataGetPreviewData(action: GetPreviewDataRequest) {
  return axios({
    url: '/api/preview/v0/',
    method: 'POST',
    data: action.queryParams,
  })
  .then((response: AxiosResponse<PreviewDataResponse>) => {
    return { data: response.data.previewData, status: response.status };
  })
  .catch((error: AxiosError) => {
    const data = error.response ? error.response.data : {};
    const status = error.response ? error.response.status : null;
    return { data, status };
  });
}
