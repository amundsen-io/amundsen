import { GetTableDataRequest, TableMetadata, TableDataResponse, Tag, User } from '../../tableMetadata/types';

import { filterFromObj, sortTagsAlphabetical } from '../../utilMethods';

/**
 * Generates the query string parameters needed for requests that act on a particular table resource.
 */
export function getTableParams(tableDataObject: TableMetadata | GetTableDataRequest): string {
  const { cluster, database, schema, table_name } = tableDataObject;
  return `db=${database}&cluster=${cluster}&schema=${schema}&table=${table_name}`;
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
