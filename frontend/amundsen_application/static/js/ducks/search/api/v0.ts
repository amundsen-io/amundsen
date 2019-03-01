import axios, { AxiosResponse, AxiosError } from 'axios';
import {
  DashboardSearchResults,
  TableSearchResults,
  UserSearchResults,
} from '../types';

import { SearchReducerState } from "../reducer";

interface SearchResponse {
  msg: string;
  status_code: number;
  search_term: string;
  dashboards: DashboardSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
}

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
  .then((response: AxiosResponse<SearchResponse>)=> transformSearchResults(response.data))
  .catch((error: AxiosError) => transformSearchResults(error.response.data));
}
