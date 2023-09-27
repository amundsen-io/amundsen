import { Badge, Tag, SnowflakeTableShare } from 'interfaces';
import * as qs from 'simple-query-string';

export function sortTagsAlphabetical(a: Tag, b: Tag): number {
  return a.tag_name.localeCompare(b.tag_name);
}

export function sortBadgesAlphabetical(a: Badge, b: Badge): number {
  const aBadgeName = a.badge_name || '';
  const bBadgeName = b.badge_name || '';

  return aBadgeName.localeCompare(bBadgeName);
}

export function sortSnowflakeTableSharesAlphabetical(a: SnowflakeTableShare, b: SnowflakeTableShare): number {
  const owner_account_compare = a.owner_account.localeCompare(b.owner_account);
  if (owner_account_compare == 0) {
    return a.name.localeCompare(b.name);
  }
  else {
    return owner_account_compare;
  }
}

export function extractFromObj(
  initialObj: object,
  desiredKeys: string[]
): object {
  return Object.keys(initialObj)
    .filter((key) => desiredKeys.indexOf(key) > -1)
    .reduce((obj, key) => {
      obj[key] = initialObj[key];

      return obj;
    }, {});
}

export function filterFromObj(
  initialObj: object,
  rejectedKeys: string[]
): object {
  return Object.keys(initialObj)
    .filter((key) => rejectedKeys.indexOf(key) === -1)
    .reduce((obj, key) => {
      obj[key] = initialObj[key];

      return obj;
    }, {});
}

/**
 * Takes a parameter objects and generates the query string parameters needed for requests.
 * Example:
 * const queryParameters = getQueryParams({key: tableData.key, column_name: columnName})
 */
export function getQueryParams(params: object): string {
  return qs.stringify(params);
}
