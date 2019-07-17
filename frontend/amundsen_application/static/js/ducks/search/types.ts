import {
  DashboardResource,
  Resource,
  ResourceType,
  SearchAllOptions,
  TableResource,
  UserResource,
} from 'interfaces';

export interface SearchResults<T extends Resource> {
  page_index: number;
  total_results: number;
  results: T[];
};
export type DashboardSearchResults = SearchResults<DashboardResource>;
export type TableSearchResults = SearchResults<TableResource>;
export type UserSearchResults = SearchResults<UserResource>;

export interface SearchResponsePayload {
  search_term: string;
  isLoading: boolean;
  dashboards: DashboardSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
};

export enum SearchAll {
  REQUEST = 'amundsen/search/SEARCH_ALL_REQUEST',
  SUCCESS = 'amundsen/search/SEARCH_ALL_SUCCESS',
  FAILURE = 'amundsen/search/SEARCH_ALL_FAILURE',
  RESET = 'amundsen/search/SEARCH_ALL_RESET',
};
export interface SearchAllRequest {
  payload: {
    options: SearchAllOptions;
    term: string;
  };
  type: SearchAll.REQUEST;
};
export interface SearchAllResponse {
  type: SearchAll.SUCCESS | SearchAll.FAILURE;
  payload?: SearchResponsePayload;
};
export interface SearchAllReset {
  type: SearchAll.RESET;
}

export enum SearchResource {
  REQUEST = 'amundsen/search/SEARCH_RESOURCE_REQUEST',
  SUCCESS = 'amundsen/search/SEARCH_RESOURCE_SUCCESS',
  FAILURE = 'amundsen/search/SEARCH_RESOURCE_FAILURE',
};
export interface SearchResourceRequest {
  payload: {
    pageIndex: number;
    resource: ResourceType;
    term: string;
  };
  type: SearchResource.REQUEST;
};
export interface SearchResourceResponse {
  type: SearchResource.SUCCESS | SearchResource.FAILURE;
  payload?: SearchResponsePayload;
};
