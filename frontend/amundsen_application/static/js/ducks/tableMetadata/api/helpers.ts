import * as qs from 'simple-query-string';

import { filterFromObj, sortTagsAlphabetical } from 'ducks/utilMethods';

import { NotificationType, OwnerDict, PeopleUser, TableMetadata, Tag, UpdateMethod, UpdateOwnerPayload, User } from 'interfaces';
import * as API from './v0';

/**
 * Generates the query string parameters needed for requests that act on a particular table resource.
 */
export function getTableQueryParams(key: string, index?: string, source?: string): string {
  return qs.stringify({ key, index, source });
}

/**
 * Parses the response for table metadata to create a TableMetadata object
 */
export function getTableDataFromResponseData(responseData: API.TableDataAPI): TableMetadata {
  return filterFromObj(responseData.tableData, ['owners', 'tags']) as TableMetadata;
}

/**
 * Parses the response for table metadata to return the array of table owners
 */
export function getTableOwnersFromResponseData(responseData: API.TableDataAPI): OwnerDict {
  // TODO: owner needs proper id, until then we have to remember that we are using display_name
  const ownerObj = responseData.tableData.owners.reduce((resultObj, currentOwner) => {
    resultObj[currentOwner.display_name] = currentOwner as User;
    return resultObj;
  }, {});
  return ownerObj;
}

/**
 * Creates post data for sending a notification to owners when they are added/removed
 */
export function createOwnerNotificationData(payload: UpdateOwnerPayload, tableData: TableMetadata) {
  return {
    notificationType: payload.method === UpdateMethod.PUT ? NotificationType.OWNER_ADDED : NotificationType.OWNER_REMOVED,
    options: {
      resource_name: `${tableData.schema}.${tableData.name}`,
      resource_path: `/table_detail/${tableData.cluster}/${tableData.database}/${tableData.schema}/${tableData.name}`
    },
    recipients: [payload.id],
  };
};

/**
 * Creates axios payload for the request to update an owner
 */
export function createOwnerUpdatePayload(payload: UpdateOwnerPayload, tableKey: string) {
  return {
    method: payload.method,
    url: `${API.API_PATH}/update_table_owner`,
    data: {
      key: tableKey,
      owner: payload.id,
    },
  }
};

/**
 * Workaround logic for not sending emails to alumni or teams.
 */
export function shouldSendNotification(user: PeopleUser): boolean {
  return user.is_active && !!user.display_name;
}
