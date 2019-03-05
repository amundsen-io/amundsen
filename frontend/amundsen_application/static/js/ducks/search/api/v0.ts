import axios, { AxiosResponse, AxiosError } from 'axios';

import { SearchResponse } from '../types';

import { SearchReducerState } from '../reducer';

function transformSearchResults(data: SearchResponse): SearchReducerState {
  return {
    searchTerm: data.search_term,
    dashboards: data.dashboards,
    tables: data.tables,
    users: data.users,
  };
}

export function searchExecuteSearch(action) {
  const { term, pageIndex } = action;
  return axios.get(`/api/search/v0/?query=${term}&page_index=${pageIndex}`)
  .then((response: AxiosResponse<SearchResponse>) => transformSearchResults(response.data))
  .catch((error: AxiosError) => {
    const data = error.response ? error.response.data : {};
    return transformSearchResults(data);
  });
}
