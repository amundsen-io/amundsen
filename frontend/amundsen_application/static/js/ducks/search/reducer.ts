import {
  SearchAll,
  SearchAllOptions,
  SearchAllRequest,
  SearchAllResponse,
  SearchResource,
  SearchResourceRequest,
  SearchResourceResponse,
  DashboardSearchResults,
  TableSearchResults,
  UserSearchResults,
} from './types';
import { ResourceType } from "../../components/common/ResourceListItem/types";

export type SearchReducerAction = SearchAllResponse | SearchResourceResponse;

export interface SearchReducerState {
  search_term: string;
  dashboards: DashboardSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
}

export function searchAll(term: string, options: SearchAllOptions = {}): SearchAllRequest {
  return {
    options,
    term,
    type: SearchAll.ACTION,
  };
}

export function searchResource(resource: ResourceType, term: string, pageIndex: number): SearchResourceRequest {
  return {
    pageIndex,
    term,
    resource,
    type: SearchResource.ACTION,
  };
}

const initialState: SearchReducerState = {
  search_term: '',
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

export default function reducer(state: SearchReducerState = initialState, action: SearchReducerAction): SearchReducerState {
  let newState = action.payload;
  switch (action.type) {
    // SearchAll will reset all resources with search results or the initial state
    case SearchAll.SUCCESS:
      return {
        ...initialState,
        ...newState,
      };
    // SearchResource will set only a single resource and preserves search state for other resources
    case SearchResource.SUCCESS:
      return {
        ...state,
        ...newState,
      };
    case SearchAll.FAILURE:
    case SearchResource.FAILURE:
      return initialState;
    default:
      return state;
  }
}
