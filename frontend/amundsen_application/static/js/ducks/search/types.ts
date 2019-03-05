import { Resource, DashboardResource, TableResource, UserResource } from "../../components/common/ResourceListItem/types";
import { SearchReducerState } from './reducer';

interface SearchResults<T extends Resource> {
  page_index: number;
  total_results: number;
  results: T[];
}

export type DashboardSearchResults = SearchResults<DashboardResource>;
export type TableSearchResults = SearchResults<TableResource>;
export type UserSearchResults = SearchResults<UserResource>;
export type SearchResponse = {
  msg: string;
  status_code: number;
  search_term: string;
  dashboards: DashboardSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
}

/* executeSearch */
export enum ExecuteSearch {
  ACTION = 'amundsen/search/EXECUTE_SEARCH',
  SUCCESS = 'amundsen/search/EXECUTE_SEARCH_SUCCESS',
  FAILURE = 'amundsen/search/EXECUTE_SEARCH_FAILURE',
}

export interface ExecuteSearchRequest {
  type: ExecuteSearch.ACTION;
  term: string;
  pageIndex: number;
}

export interface ExecuteSearchResponse {
  type: ExecuteSearch.SUCCESS | ExecuteSearch.FAILURE;
  payload?: SearchReducerState;
}
