import { Search as UrlSearch } from 'history';

import {
  DashboardResource,
  Resource,
  ResourceType,
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
  dashboards?: DashboardSearchResults;
  tables?: TableSearchResults;
  users?: UserSearchResults;
};
export interface SearchAllResponsePayload extends SearchResponsePayload {
  selectedTab: ResourceType;
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
    resource: ResourceType;
    pageIndex: number;
    term: string;
  };
  type: SearchAll.REQUEST;
};
export interface SearchAllResponse {
  type: SearchAll.SUCCESS | SearchAll.FAILURE;
  payload?: SearchAllResponsePayload;
};
export interface SearchAllReset {
  type: SearchAll.RESET;
};


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


export enum SubmitSearch {
  REQUEST = 'amundsen/search/SUBMIT_SEARCH_REQUEST',
};
export interface SubmitSearchRequest {
  payload: {
    searchTerm: string;
  };
  type: SubmitSearch.REQUEST;
};


export enum SetResource {
  REQUEST = 'amundsen/search/SET_RESOURCE_REQUEST',
};
export interface SetResourceRequest {
  payload: {
    resource: ResourceType;
    updateUrl: boolean;
  };
  type: SetResource.REQUEST;
};


export enum SetPageIndex {
  REQUEST = 'amundsen/search/SET_PAGE_INDEX_REQUEST',
};
export interface SetPageIndexRequest {
  payload: {
    pageIndex: number;
    updateUrl: boolean;
  };
  type: SetPageIndex.REQUEST;
};


export enum LoadPreviousSearch {
  REQUEST = 'amundsen/search/LOAD_PREVIOUS_SEARCH_REQUEST',
};
export interface LoadPreviousSearchRequest {
  type: LoadPreviousSearch.REQUEST;
};


export enum UrlDidUpdate {
  REQUEST = 'amundsen/search/URL_DID_UPDATE_REQUEST',
};
export interface UrlDidUpdateRequest {
  payload: {
    urlSearch: UrlSearch;
  };
  type: UrlDidUpdate.REQUEST;
};
