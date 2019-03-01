/** TODO: We will introduce better typing for function parameters return types */

import { filterFromObj, sortTagsAlphabetical } from '../../utilMethods';

/**
 * Generates the query string parameters needed for requests that act on a particular table resource.
 */
export function getTableParams(tableDataObject) {
  const { cluster, database, schema, table_name } = tableDataObject;
  return `db=${database}&cluster=${cluster}&schema=${schema}&table=${table_name}`;
}

/**
 * Parses the response for table metadata to create a TableMetadata object
 */
export function getTableDataFromResponseData(responseData) {
  return filterFromObj(responseData, ['owners', 'tags']);
}

/**
 * Parses the response for table metadata to return the array of table owners
 */
export function getTableOwnersFromResponseData(responseData) {
  // TODO: owner needs proper id, until then we have to remember that we are using display_name
  const ownerObj = responseData.owners.reduce((resultObj, currentOwner) => {
    resultObj[currentOwner.display_name] = currentOwner;
    return resultObj;
  }, {});
  return ownerObj;
}

/**
 * Parses the response for table metadata to return an array of sorted table tags
 */
export function getTableTagsFromResponseData(responseData) {
  return responseData.tags.sort(sortTagsAlphabetical);
}
