import { ResourceType, SearchAllOptions } from 'interfaces';

import {
  SearchResponsePayload,
  SearchAll,
  SearchAllRequest,
  SearchAllReset,
  SearchAllResponse,
  SearchResource,
  SearchResourceRequest,
  SearchResourceResponse,
  DashboardSearchResults,
  TableSearchResults,
  UserSearchResults,
} from './types';

export interface SearchReducerState {
  search_term: string;
  isLoading: boolean;
  dashboards: DashboardSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
};

/* ACTIONS */
export function searchAll(term: string, options: SearchAllOptions): SearchAllRequest {
  return {
    payload: {
      options,
      term,
    },
    type: SearchAll.REQUEST,
  };
};
export function searchAllSuccess(searchResults: SearchResponsePayload): SearchAllResponse {
  return { type: SearchAll.SUCCESS, payload: searchResults };
};
export function searchAllFailure(): SearchAllResponse {
  return { type: SearchAll.FAILURE };
};

export function searchResource(resource: ResourceType, term: string, pageIndex: number): SearchResourceRequest {
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

/* REDUCER */
export const initialState: SearchReducerState = {
  search_term: '',
  isLoading: false,
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
        isLoading: false,
      };
    default:
      return state;
  };
};
