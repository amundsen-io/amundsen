import {
  Resource,
  ResourceType,
  DashboardResource,
  TableResource,
  UserResource,
} from 'interfaces';
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
  dashboards?: DashboardSearchResults;
  tables?: TableSearchResults;
  users?: UserSearchResults;
}

/* searchAll - Search all resource types */
export enum SearchAll {
  ACTION = 'amundsen/search/SEARCH_ALL',
  SUCCESS = 'amundsen/search/SEARCH_ALL_SUCCESS',
  FAILURE = 'amundsen/search/SEARCH_ALL_FAILURE',
  RESET = 'amundsen/search/SEARCH_ALL_RESET',
}

export interface SearchAllOptions {
  dashboardIndex?: number;
  tableIndex?: number;
  userIndex?: number;
}

export interface SearchAllRequest {
  options: SearchAllOptions;
  term: string;
  type: SearchAll.ACTION;
}

export interface SearchAllResponse {
  type: SearchAll.SUCCESS | SearchAll.FAILURE;
  payload?: SearchReducerState;
}

export interface SearchAllReset {
  type: SearchAll.RESET;
}

/* searchResource - Search a single resource type */
export enum SearchResource {
  ACTION = 'amundsen/search/SEARCH_RESOURCE',
  SUCCESS = 'amundsen/search/SEARCH_RESOURCE_SUCCESS',
  FAILURE = 'amundsen/search/SEARCH_RESOURCE_FAILURE',
}

export interface SearchResourceRequest {
  pageIndex: number;
  resource: ResourceType;
  term: string;
  type: SearchResource.ACTION;
}

export interface SearchResourceResponse {
  type: SearchResource.SUCCESS | SearchResource.FAILURE;
  payload?: SearchReducerState;
}
