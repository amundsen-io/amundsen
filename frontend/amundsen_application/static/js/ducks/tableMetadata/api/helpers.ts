import * as qs from 'simple-query-string';

import { isNestedColumnsEnabled } from 'config/config-utils';
import { filterFromObj } from 'ducks/utilMethods';

import {
  NotificationType,
  PeopleUser,
  TableColumn,
  TableMetadata,
  UpdateMethod,
  UpdateOwnerPayload,
} from 'interfaces';
import {
  convertNestedTypeToColumns,
  parseNestedType,
} from 'features/ColumnList/ColumnType/parser';
import * as API from './v0';

export interface TableQueryParams {
  key: string;
  column_name?: string;
  index?: string;
  source?: string;
}

/**
 * Generates the query string parameters needed for requests that act on a particular table resource.
 */
export function getTableQueryParams(params: TableQueryParams): string {
  return qs.stringify(params);
}

/**
 * Generates the query string parameters needed for the request for the related dashboards to a table
 */
export function getRelatedDashboardSlug(key: string): string {
  return encodeURIComponent(key);
}

/**
 * Adds a column_index and nested columns to column objects
 * @param columns
 */
export function processColumns(
  columns: TableColumn[],
  databaseId?: string
): TableColumn[] {
  return columns.map((column, index) => {
    const nestedType = parseNestedType(column.col_type, databaseId);

    return {
      ...column,
      col_index: index,
      children:
        nestedType && isNestedColumnsEnabled()
          ? convertNestedTypeToColumns(nestedType)
          : undefined,
    };
  });
}

/**
 * Parses the response for table metadata information to create a TableMetadata object
 */
export function getTableDataFromResponseData(
  responseData: API.TableDataAPI
): TableMetadata {
  const tableData = filterFromObj(responseData.tableData, [
    'owners',
    'tags',
  ]) as TableMetadata;
  tableData.columns = processColumns(tableData.columns, tableData.database);
  return tableData;
}

/**
 * Creates post data for sending a notification to owners when they are added/removed
 */
export function createOwnerNotificationData(
  payload: UpdateOwnerPayload,
  tableData: TableMetadata
) {
  return {
    notificationType:
      payload.method === UpdateMethod.PUT
        ? NotificationType.OWNER_ADDED
        : NotificationType.OWNER_REMOVED,
    options: {
      resource_name: `${tableData.schema}.${tableData.name}`,
      resource_path: `/table_detail/${tableData.cluster}/${tableData.database}/${tableData.schema}/${tableData.name}`,
    },
    recipients: [payload.id],
  };
}

/**
 * Workaround logic for not sending emails to alumni or teams.
 */
export function shouldSendNotification(user: PeopleUser): boolean {
  return user.is_active && !!user.display_name;
}

/**
 * Returns total column count, including nested columns
 */
export function getColumnCount(columns: TableColumn[]) {
  return columns.reduce((acc, column) => {
    return acc + (column?.children?.length || 0);
  }, columns.length);
}
