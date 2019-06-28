import axios, { AxiosResponse } from 'axios';

import AppConfig from 'config/config';
import { ResourceType } from 'interfaces';

import { DashboardSearchResults, TableSearchResults, UserSearchResults } from '../types';

const BASE_URL = '/api/search/v0';

interface SearchAPI {
  msg: string;
  status_code: number;
  search_term: string;
  dashboards?: DashboardSearchResults;
  tables?: TableSearchResults;
  users?: UserSearchResults;
};

export function searchResource(pageIndex: number, resource: ResourceType, term: string) {
  if (resource === ResourceType.dashboard ||
     (resource === ResourceType.user && !AppConfig.indexUsers.enabled)) {
    return Promise.resolve({});
  }
  return axios.get(`${BASE_URL}/${resource}?query=${term}&page_index=${pageIndex}`)
    .then((response: AxiosResponse<SearchAPI>) => {
      const { data } = response;
      const ret = { searchTerm: data.search_term };
      ['tables', 'users', 'dashboards'].forEach((key) => {
        if (data[key]) {
          ret[key] = data[key];
        }
      });
      return ret;
    });
};
