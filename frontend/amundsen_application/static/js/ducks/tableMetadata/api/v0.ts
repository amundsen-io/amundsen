import axios, { AxiosResponse, AxiosError } from 'axios';

import {
  PreviewData,
  TablePreviewQueryParams,
  TableMetadata,
  DashboardResource,
  UpdateOwnerPayload,
  User,
  Tag,
  Lineage,
  ResourceType,
  TableQualityChecks,
} from 'interfaces';

/** HELPERS **/
import { indexDashboardsEnabled } from 'config/config-utils';
import {
  createOwnerUpdatePayload,
  getOwnersDictFromUsers,
} from 'utils/ownerUtils';
import {
  getTableQueryParams,
  getRelatedDashboardSlug,
  getTableDataFromResponseData,
  createOwnerNotificationData,
  shouldSendNotification,
  getTypeMetadataFromKey,
} from './helpers';

export const API_PATH = '/api/metadata/v0';

type MessageAPI = { msg: string };

export type TableData = TableMetadata & {
  owners: User[];
  tags: Tag[];
};
export type DescriptionAPI = { description: string } & MessageAPI;
export type PreviewDataAPI = { previewData: PreviewData } & MessageAPI;
export type TableDataAPI = { tableData: TableData } & MessageAPI;
export type RelatedDashboardDataAPI = {
  dashboards: DashboardResource[];
} & MessageAPI;
export type LineageAPI = { lineage: Lineage } & MessageAPI;
export type TableQualityChecksAPI = { checks: TableQualityChecks } & MessageAPI;

const extractColumnName = (columnKey) =>
  columnKey.substring(columnKey.lastIndexOf('/') + 1);

export function getTableData(key: string, index?: string, source?: string) {
  const tableQueryParams = getTableQueryParams({ key, index, source });
  const tableURL = `${API_PATH}/table?${tableQueryParams}`;
  const tableRequest = axios.get<TableDataAPI>(tableURL);

  return tableRequest.then((tableResponse: AxiosResponse<TableDataAPI>) => ({
    data: getTableDataFromResponseData(tableResponse.data),
    owners: getOwnersDictFromUsers(tableResponse.data.tableData.owners),
    tags: tableResponse.data.tableData.tags,
    statusCode: tableResponse.status,
  }));
}

export function getTableDashboards(tableKey: string) {
  if (!indexDashboardsEnabled()) {
    return Promise.resolve({ dashboards: [] });
  }

  const relatedDashboardsSlug: string = getRelatedDashboardSlug(tableKey);
  const relatedDashboardsURL: string = `${API_PATH}/table/${relatedDashboardsSlug}/dashboards`;
  const relatedDashboardsRequest = axios.get<RelatedDashboardDataAPI>(
    relatedDashboardsURL
  );

  return relatedDashboardsRequest
    .then(
      (relatedDashboardsResponse: AxiosResponse<RelatedDashboardDataAPI>) => ({
        dashboards: relatedDashboardsResponse.data.dashboards,
      })
    )
    .catch((e: AxiosError<RelatedDashboardDataAPI>) => {
      const { response } = e;
      const msg = response?.data?.msg || '';

      return Promise.reject({ msg, dashboards: [] });
    });
}

export function getTableDescription(tableData: TableMetadata) {
  const tableParams = getTableQueryParams({ key: tableData.key });
  return axios
    .get(`${API_PATH}/get_table_description?${tableParams}`)
    .then((response: AxiosResponse<DescriptionAPI>) => {
      tableData.description = response.data.description;
      return tableData;
    });
}

export function updateTableDescription(
  description: string,
  tableData: TableMetadata
) {
  return axios.put(`${API_PATH}/put_table_description`, {
    description,
    key: tableData.key,
    source: 'user',
  });
}

export function getTableOwners(key: string) {
  const tableParams = getTableQueryParams({ key });
  return axios
    .get(`${API_PATH}/table?${tableParams}`)
    .then((response: AxiosResponse<TableDataAPI>) =>
      getOwnersDictFromUsers(response.data.tableData.owners)
    );
}

/* TODO: Typing return type generates redux-saga related type error that need more dedicated debugging */
export function generateOwnerUpdateRequests(
  updateArray: UpdateOwnerPayload[],
  tableData: TableMetadata
): any {
  /* Return the list of requests to be executed */
  return updateArray.map((updateOwnerPayload) => {
    const updatePayload = createOwnerUpdatePayload(
      ResourceType.table,
      tableData.key,
      updateOwnerPayload
    );
    const notificationData = createOwnerNotificationData(
      updateOwnerPayload,
      tableData
    );

    /* Chain requests to send notification on success to desired users */
    return axios(updatePayload)
      .then(() =>
        axios.get(`/api/metadata/v0/user?user_id=${updateOwnerPayload.id}`)
      )
      .then((response) => {
        if (shouldSendNotification(response.data.user)) {
          return axios.post('/api/mail/v0/notification', notificationData);
        }
      });
  });
}

export function getColumnDescription(
  columnKey: string,
  tableData: TableMetadata
) {
  const tableParams = getTableQueryParams({
    key: tableData.key,
    column_name: extractColumnName(columnKey),
  });
  return axios
    .get(`${API_PATH}/get_column_description?${tableParams}`)
    .then((response: AxiosResponse<DescriptionAPI>) => {
      const column = tableData.columns.find(
        (column) => column.key === columnKey
      );
      if (column) {
        column.description = response.data.description;
      }
      return tableData;
    });
}

export function updateColumnDescription(
  description: string,
  columnKey: string,
  tableData: TableMetadata
) {
  return axios.put(`${API_PATH}/put_column_description`, {
    description,
    column_name: extractColumnName(columnKey),
    key: tableData.key,
    source: 'user',
  });
}

export function getTypeMetadataDescription(
  typeMetadataKey: string,
  tableData: TableMetadata
) {
  return axios
    .get(
      `${API_PATH}/get_type_metadata_description?type_metadata_key=${typeMetadataKey}`
    )
    .then((response: AxiosResponse<DescriptionAPI>) => {
      const typeMetadata = getTypeMetadataFromKey(typeMetadataKey, tableData);
      if (typeMetadata) {
        typeMetadata.description = response.data.description;
      }
      return tableData;
    });
}

export function updateTypeMetadataDescription(
  description: string,
  typeMetadataKey: string,
  tableData: TableMetadata
) {
  return axios.put(`${API_PATH}/put_type_metadata_description`, {
    description,
    type_metadata_key: typeMetadataKey,
    table_key: tableData.key,
    source: 'user',
  });
}

export function getPreviewData(queryParams: TablePreviewQueryParams) {
  return axios({
    url: '/api/preview/v0/',
    method: 'POST',
    data: queryParams,
  })
    .then((response: AxiosResponse<PreviewDataAPI>) => ({
      data: response.data.previewData,
      status: response.status,
    }))
    .catch((e: AxiosError<PreviewDataAPI>) => {
      const { response } = e;
      let data = {};
      if (response && response.data && response.data.previewData) {
        data = response.data.previewData;
      }
      const status = response ? response.status : null;
      return Promise.reject({ data, status });
    });
}

export function getTableQualityChecksSummary(key: string) {
  const tableQueryParams = getTableQueryParams({
    key,
  });
  return axios
    .get(`/api/quality/v0/table/summary?${tableQueryParams}`)
    .then((response: AxiosResponse<TableQualityChecksAPI>) => ({
      checks: response.data.checks,
      status: response.status,
    }))
    .catch((e) => {
      const { response } = e;
      const status = response ? response.status : null;
      return Promise.reject({ status });
    });
}
