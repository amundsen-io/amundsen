import { GetTableDataRequest, TableMetadata, TableDataResponse, Tag, User } from 'ducks/tableMetadata/types';

import { filterFromObj, sortTagsAlphabetical } from 'ducks/utilMethods';

/**
 * Generates the query string parameters needed for requests that act on a particular table resource.
 */
export function getTableQueryParams(tableDataObject: TableMetadata | GetTableDataRequest): string {
  const { key } = tableDataObject;
  return `key=${encodeURIComponent(key)}`;
}

/**
 * Parses the response for table metadata to create a TableMetadata object
 */
export function getTableDataFromResponseData(responseData: TableDataResponse): TableMetadata {
  return filterFromObj(responseData.tableData, ['owners', 'tags']) as TableMetadata;
}

/**
 * Parses the response for table metadata to return the array of table owners
 */
export function getTableOwnersFromResponseData(responseData: TableDataResponse): { [id: string] : User } {
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
export function getTableTagsFromResponseData(responseData: TableDataResponse): Tag[] {
  return responseData.tableData.tags.sort(sortTagsAlphabetical);
}
