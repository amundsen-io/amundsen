import { filterFromObj, sortTagsAlphabetical } from 'ducks/utilMethods';

import { OwnerDict, TableMetadata, Tag, User } from 'interfaces';
import { TableDataAPI } from './v0';

/**
 * Generates the query string parameters needed for requests that act on a particular table resource.
 */
export function getTableQueryParams(tableKey: string): string {
  return `key=${encodeURIComponent(tableKey)}`;
}

/**
 * Parses the response for table metadata to create a TableMetadata object
 */
export function getTableDataFromResponseData(responseData: TableDataAPI): TableMetadata {
  return filterFromObj(responseData.tableData, ['owners', 'tags']) as TableMetadata;
}

/**
 * Parses the response for table metadata to return the array of table owners
 */
export function getTableOwnersFromResponseData(responseData: TableDataAPI): OwnerDict {
  // TODO: owner needs proper id, until then we have to remember that we are using display_name
  const ownerObj = responseData.tableData.owners.reduce((resultObj, currentOwner) => {
    resultObj[currentOwner.display_name] = currentOwner as User;
    return resultObj;
  }, {});
  return ownerObj;
}

/**
 * Parses the response for table metadata to return an array of sorted table tags
 */
export function getTableTagsFromResponseData(responseData: TableDataAPI): Tag[] {
  return responseData.tableData.tags.sort(sortTagsAlphabetical);
}
