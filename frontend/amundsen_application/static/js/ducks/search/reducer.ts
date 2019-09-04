import { ResourceType } from 'interfaces';

import { Search as UrlSearch } from 'history';

import {
  DashboardSearchResults,
  SearchAll,
  SearchAllRequest,
  SearchAllReset,
  SearchAllResponse,
  SearchAllResponsePayload,
  SearchResource,
  SearchResponsePayload,
  SearchResourceRequest,
  SearchResourceResponse,
  TableSearchResults,
  UserSearchResults,
  SubmitSearchRequest,
  SubmitSearch,
  SetResourceRequest,
  SetResource,
  SetPageIndexRequest, SetPageIndex, LoadPreviousSearchRequest, LoadPreviousSearch, UrlDidUpdateRequest, UrlDidUpdate,
} from './types';

export interface SearchReducerState {
  search_term: string;
  selectedTab: ResourceType;
  isLoading: boolean;
  dashboards: DashboardSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
};

/* ACTIONS */
export function searchAll(term: string, resource: ResourceType, pageIndex: number): SearchAllRequest {
  return {
    payload: {
      resource,
      pageIndex,
      term,
    },
    type: SearchAll.REQUEST,
  };
};
export function searchAllSuccess(searchResults: SearchAllResponsePayload): SearchAllResponse {
  return { type: SearchAll.SUCCESS, payload: searchResults };
};
export function searchAllFailure(): SearchAllResponse {
  return { type: SearchAll.FAILURE };
};

export function searchResource(term: string, resource: ResourceType, pageIndex: number): SearchResourceRequest {
  return {
    payload: {
      pageIndex,
      term,
      resource,
    },
    type: SearchResource.REQUEST,
  };
};
export function searchResourceSuccess(searchResults: SearchResponsePayload): SearchResourceResponse {
  return { type: SearchResource.SUCCESS, payload: searchResults };
};
export function searchResourceFailure(): SearchResourceResponse {
  return { type: SearchResource.FAILURE };
};

export function searchReset(): SearchAllReset {
  return {
    type: SearchAll.RESET,
  };
};

export function submitSearch(searchTerm: string): SubmitSearchRequest {
  return {
    payload: { searchTerm },
    type: SubmitSearch.REQUEST,
  };
};

export function setResource(resource: ResourceType, updateUrl: boolean = true): SetResourceRequest {
  return {
    payload: { resource, updateUrl },
    type: SetResource.REQUEST,
  };
};

export function setPageIndex(pageIndex: number, updateUrl: boolean = true): SetPageIndexRequest {
  return {
    payload: { pageIndex, updateUrl },
    type: SetPageIndex.REQUEST,
  };
};

export function loadPreviousSearch(): LoadPreviousSearchRequest {
  return {
    type: LoadPreviousSearch.REQUEST,
  };
};

export function urlDidUpdate(urlSearch: UrlSearch): UrlDidUpdateRequest{
  return {
    payload: { urlSearch },
    type: UrlDidUpdate.REQUEST,
  };
};


/* REDUCER */
export const initialState: SearchReducerState = {
  search_term: '',
  isLoading: false,
  selectedTab: ResourceType.table,
  dashboards: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
  tables: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
  users: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
};

export default function reducer(state: SearchReducerState = initialState, action): SearchReducerState {
  switch (action.type) {
    case SearchAll.RESET:
      return initialState;
    case SearchAll.REQUEST:
      // updates search term to reflect action
      return {
        ...state,
        search_term: (<SearchAllRequest>action).payload.term,
        isLoading: true,
      };
    case SearchResource.REQUEST:
      return {
        ...state,
        isLoading: true,
      };
    case SearchAll.SUCCESS:
      // resets all resources with initial state then applies search results
      const newState = (<SearchAllResponse>action).payload;
      return {
        ...initialState,
        ...newState,
        isLoading: false,
      };
    case SearchResource.SUCCESS:
      // resets only a single resource and preserves search state for other resources
      const resourceNewState = (<SearchResourceResponse>action).payload;
      return {
        ...state,
        ...resourceNewState,
        isLoading: false,
      };
    case SearchAll.FAILURE:
    case SearchResource.FAILURE:
      return {
        ...initialState,  
        search_term: state.search_term,
      };
    case SetResource.REQUEST:
      return {
        ...state,
        selectedTab: (<SetResourceRequest>action).payload.resource
      };
    default:
      return state;
  };
};
