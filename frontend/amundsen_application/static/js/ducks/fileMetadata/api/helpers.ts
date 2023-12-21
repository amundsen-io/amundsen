import * as qs from 'simple-query-string';

import { filterFromObj } from 'ducks/utilMethods';

import {
  NotificationType,
  PeopleUser,
  FileMetadata,
  UpdateMethod,
} from 'interfaces';
import * as API from './v0';

export interface FileQueryParams {
  key: string;
  column_name?: string;
  index?: string;
  source?: string;
}

/**
 * Generates the query string parameters needed for requests that act on a particular file resource.
 */
export function getFileQueryParams(params: FileQueryParams): string {
  return qs.stringify(params);
}

/**
 * Parses the response for file metadata information to create a FileMetadata object
 */
export function getFileDataFromResponseData(
  responseData: API.FileDataAPI
): FileMetadata {
  return filterFromObj(responseData.fileData, [
    'owners',
    'tags',
  ]) as FileMetadata;
}

/**
 * Workaround logic for not sending emails to alumni or teams.
 */
export function shouldSendNotification(user: PeopleUser): boolean {
  return user.is_active && !!user.display_name;
}

