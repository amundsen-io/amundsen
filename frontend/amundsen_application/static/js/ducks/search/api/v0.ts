import axios, { AxiosResponse } from 'axios';

import {
  indexDashboardsEnabled,
  indexFeaturesEnabled,
  indexUsersEnabled,
  searchHighlightingEnabled,
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

const RESOURCE_TYPES = ['dashboard', 'feature', 'table', 'user'];

export interface SearchAPI {
  msg: string;
  status_code: number;
  search_term: string;
  dashboard?: DashboardSearchResults;
  feature?: FeatureSearchResults;
  table?: TableSearchResults;
  user?: UserSearchResults;
}

export const searchHelper = (response: AxiosResponse<SearchAPI>) => {
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
  // table is always configured
  if (resource === ResourceType.table) {
    return true;
  }
  if (resource === ResourceType.user) {
    return indexUsersEnabled();
  }
  if (resource === ResourceType.dashboard) {
    return indexDashboardsEnabled();
  }
  if (resource === ResourceType.feature) {
    return indexFeaturesEnabled();
  }
  return false;
};

export function search(
  pageIndex: number,
  resultsPerPage: number,
  resources: ResourceType[],
  searchTerm: string,
  filters: ResourceFilterReducerState = {},
  searchType: SearchType
) {
  // If given invalid resource in list dont search for that one only for valid ones
  const validResources = resources.filter((r) => isResourceIndexed(r));
  if (!validResources.length) {
    // If there are no resources to search through then return {}
    return Promise.resolve({});
  }

  const highlightingOptions = validResources.reduce(
    (obj, resource) => ({
      ...obj,
      [resource]: {
        enable_highlight: searchHighlightingEnabled(resource),
      },
    }),
    {}
  );

  return axios
    .post(`${BASE_URL}/search`, {
      filters,
      pageIndex,
      resources: validResources,
      resultsPerPage,
      searchTerm,
      searchType,
      highlightingOptions,
    })
    .then(searchHelper);
}
