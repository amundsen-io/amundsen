import * as qs from 'simple-query-string';

import { filterFromObj } from 'ducks/utilMethods';

import {
  NotificationType,
  PeopleUser,
  ProviderMetadata,
  UpdateMethod,
} from 'interfaces';
import * as API from './v0';

export interface ProviderQueryParams {
  key: string;
  column_name?: string;
  index?: string;
  source?: string;
}

/**
 * Generates the query string parameters needed for requests that act on a particular provider resource.
 */
export function getProviderQueryParams(params: ProviderQueryParams): string {
  return qs.stringify(params);
}

/**
 * Generates the query string parameters needed for the request for the related dashboards to a provider
 */
export function getRelatedDashboardSlug(key: string): string {
  return encodeURIComponent(key);
}

/**
 * Parses the response for provider metadata information to create a ProviderMetadata object
 */
export function getProviderDataFromResponseData(
  responseData: API.ProviderDataAPI
): ProviderMetadata {
  return filterFromObj(responseData.providerData, [
    'owners',
    'tags',
  ]) as ProviderMetadata;
}

/**
 * Workaround logic for not sending emails to alumni or teams.
 */
export function shouldSendNotification(user: PeopleUser): boolean {
  return user.is_active && !!user.display_name;
}

