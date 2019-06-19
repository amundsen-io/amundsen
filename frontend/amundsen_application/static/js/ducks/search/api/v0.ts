import axios, { AxiosResponse } from 'axios';

import { ResourceType, SearchAllOptions } from 'interfaces';

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

export function searchAll(options: SearchAllOptions, term: string) {
  return axios.all([
      axios.get(`${BASE_URL}/table?query=${term}&page_index=${options.tableIndex || 0}`),
      // TODO PEOPLE - Add request for people here
    ]).then(axios.spread((tableResponse: AxiosResponse<SearchAPI>) => {
      return {
        search_term: tableResponse.data.search_term,
        tables: tableResponse.data.tables,
      }
  }));
};

export function searchResource(pageIndex: number, resource: ResourceType, term: string) {
  return axios.get(`${BASE_URL}/${resource}?query=${term}&page_index=${pageIndex}`)
    .then((response: AxiosResponse<SearchAPI>) => {
      const { data } = response;
      const ret = { searchTerm: data.search_term };
      ['tables', 'users'].forEach((key) => {
        if (data[key]) {
          ret[key] = data[key];
        }
      });
      return ret;
    });
};
