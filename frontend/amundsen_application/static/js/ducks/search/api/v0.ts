import axios, { AxiosResponse } from 'axios';

import {
  indexDashboardsEnabled,
  indexFeaturesEnabled,
  indexUsersEnabled,
} from 'config/config-utils';
import { ResourceType, SearchType } from 'interfaces';

import {
  DashboardSearchResults,
  FeatureSearchResults,
  TableSearchResults,
  UserSearchResults,
} from '../types';

import { ResourceFilterReducerState } from '../filters/reducer';

export const BASE_URL = '/api/search/v1';

const RESOURCE_TYPES = ['dashboards', 'features', 'tables', 'users'];

export interface SearchAPI {
  msg: string;
  status_code: number;
  search_term: string;
  dashboards?: DashboardSearchResults;
  features?: FeatureSearchResults;
  tables?: TableSearchResults;
  users?: UserSearchResults;
}

export const searchResourceHelper = (response: AxiosResponse<SearchAPI>) => {
  const { data } = response;
  const ret = { searchTerm: data.search_term };
  RESOURCE_TYPES.forEach((key) => {
    if (data[key]) {
      ret[key] = data[key];
    }
  });
  return ret;
};

export const isResourceIndexed = (resource: ResourceType) => {
  // table is always configured and user has a separate case
  if (resource === ResourceType.table || resource === ResourceType.user) {
    return true;
  }
  if (resource === ResourceType.dashboard) {
    return indexDashboardsEnabled();
  }
  if (resource === ResourceType.feature) {
    return indexFeaturesEnabled();
  }
  return false;
};

export function searchResource(
  pageIndex: number,
  resource: ResourceType,
  term: string,
  filters: ResourceFilterReducerState = {},
  searchType: SearchType
) {
  /* If resource support is not configured or if there is no search term for non-filter supported resources*/
  if (
    resource === ResourceType.user &&
    (!indexUsersEnabled() || term.length === 0)
  ) {
    return Promise.resolve({});
  }
  if (!isResourceIndexed(resource)) {
    return Promise.resolve({});
  }

  console.log(filters)

  /* Note: This logic must exist until query string endpoints are created for all resources */
  return axios
    .post(`${BASE_URL}/search`, {
      filters,
      pageIndex,
      term,
      searchType,
    })
    .then(searchResourceHelper);
}
