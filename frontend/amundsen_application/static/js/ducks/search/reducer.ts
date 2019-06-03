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
import { ResourceType } from 'components/common/ResourceListItem/types';

export type SearchReducerAction = SearchAllResponse | SearchResourceResponse | SearchAllRequest | SearchResourceRequest;

export interface SearchReducerState {
  search_term: string;
  isLoading: boolean;
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

export default function reducer(state: SearchReducerState = initialState, action: SearchReducerAction): SearchReducerState {
  switch (action.type) {
    // Updates search term to reflect action
    case SearchAll.ACTION:
      return {
        ...state,
        search_term: action.term,
        isLoading: true,
      };
    case SearchResource.ACTION:
      return {
        ...state,
        isLoading: true,
      };
    // SearchAll will reset all resources with search results or the initial state
    case SearchAll.SUCCESS:
      const newState = action.payload;
      return {
        ...initialState,
        ...newState,
        isLoading: false,
      };
    // SearchResource will set only a single resource and preserves search state for other resources
    case SearchResource.SUCCESS:
      const resourceNewState = action.payload;
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
  }
}
