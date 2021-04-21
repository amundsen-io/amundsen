import axios, { AxiosResponse } from 'axios';

import { indexDashboardsEnabled, indexUsersEnabled } from 'config/config-utils';
import { ResourceType, SearchType } from 'interfaces';

import {
  DashboardSearchResults,
  TableSearchResults,
  UserSearchResults,
} from '../types';

import { ResourceFilterReducerState } from '../filters/reducer';

export const BASE_URL = '/api/search/v0';

export interface SearchAPI {
  msg: string;
  status_code: number;
  search_term: string;
  dashboards?: DashboardSearchResults;
  tables?: TableSearchResults;
  users?: UserSearchResults;
}

export const searchResourceHelper = (response: AxiosResponse<SearchAPI>) => {
  const { data } = response;
  const ret = { searchTerm: data.search_term };
  ['dashboards', 'tables', 'users'].forEach((key) => {
    if (data[key]) {
      ret[key] = data[key];
    }
  });
  return ret;
};

export function searchResource(
  pageIndex: number,
  resource: ResourceType,
  term: string,
  filters: ResourceFilterReducerState = {},
  searchType: SearchType
) {
  /* If resource support is not configured or if there is no search term for non-filter supported resources */
  if (
    (resource === ResourceType.dashboard && !indexDashboardsEnabled()) ||
    (resource === ResourceType.user &&
      (!indexUsersEnabled() || term.length === 0))
  ) {
    return Promise.resolve({});
  }

  /* Note: This logic must exist until query string endpoints are created for all resources */
  if (resource === ResourceType.table || resource === ResourceType.dashboard) {
    return axios
      .post(`${BASE_URL}/${resource}`, {
        filters,
        pageIndex,
        term,
        searchType,
      })
      .then(searchResourceHelper);
  }
  return axios
    .get(
      `${BASE_URL}/${resource}?query=${term}&page_index=${pageIndex}&search_type=${searchType}`
    )
    .then(searchResourceHelper);
}
