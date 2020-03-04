import { ResourceType, SearchType} from 'interfaces';

import { Search as UrlSearch } from 'history';

import filterReducer, { initialFilterState, UpdateSearchFilter, FilterReducerState } from './filters/reducer';

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
  InlineSearch,
  InlineSearchRequest,
  InlineSearchResponse,
  InlineSearchResponsePayload,
  InlineSearchUpdatePayload,
  InlineSearchSelect,
  InlineSearchUpdate,
  TableSearchResults,
  UserSearchResults,
  ClearSearch,
  ClearSearchRequest,
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
  inlineResults: {
    isLoading: boolean;
    tables: TableSearchResults;
    users: UserSearchResults;
  },
  filters: FilterReducerState;
};

/* ACTIONS */
export function searchAll(searchType: SearchType, term: string, resource?: ResourceType, pageIndex?: number, useFilters: boolean = false): SearchAllRequest {
  return {
    payload: {
      resource,
      pageIndex,
      term,
      useFilters,
      searchType,
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

export function searchResource(searchType: SearchType, term: string, resource: ResourceType, pageIndex: number): SearchResourceRequest {
  return {
    payload: {
      pageIndex,
      term,
      resource,
      searchType
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

export function getInlineResultsDebounce(term: string): InlineSearchRequest {
  return {
    payload: {
      term,
    },
    type: InlineSearch.REQUEST_DEBOUNCE,
  };
};
export function getInlineResults(term: string): InlineSearchRequest {
  return {
    payload: {
      term,
    },
    type: InlineSearch.REQUEST,
  };
};
export function getInlineResultsSuccess(inlineResults: InlineSearchResponsePayload): InlineSearchResponse {
  return { type: InlineSearch.SUCCESS, payload: inlineResults };
};
export function getInlineResultsFailure(): InlineSearchResponse {
  return { type: InlineSearch.FAILURE };
};
export function selectInlineResult(resourceType: ResourceType, searchTerm: string, updateUrl: boolean = false): InlineSearchSelect {
  return {
    payload: {
      resourceType,
      searchTerm,
      updateUrl,
    },
    type: InlineSearch.SELECT
  };
};
export function updateFromInlineResult(data: InlineSearchUpdatePayload): InlineSearchUpdate {
  return {
    payload: data,
    type: InlineSearch.UPDATE
  };
};

export function searchReset(): SearchAllReset {
  return {
    type: SearchAll.RESET,
  };
};

export function submitSearch(searchTerm: string, useFilters: boolean = false): SubmitSearchRequest {
  return {
    payload: { searchTerm, useFilters },
    type: SubmitSearch.REQUEST,
  };
};

export function clearSearch(): ClearSearchRequest {
  return {
    type: ClearSearch.REQUEST,
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
export const initialInlineResultsState = {
  isLoading: false,
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
}
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
  filters: initialFilterState,
  inlineResults: initialInlineResultsState,
};

export default function reducer(state: SearchReducerState = initialState, action): SearchReducerState {
  switch (action.type) {
    case UpdateSearchFilter.SET_BY_RESOURCE:
      return {
        ...state,
        search_term: action.payload.term,
        filters: filterReducer(state.filters, action, state.selectedTab),
      }
    case UpdateSearchFilter.CLEAR_ALL:
      return {
        ...state,
        filters: filterReducer(state.filters, action, state.selectedTab),
      }
    case UpdateSearchFilter.CLEAR_CATEGORY:
    case UpdateSearchFilter.UPDATE_CATEGORY:
      return {
        ...state,
        isLoading: true,
        filters: filterReducer(state.filters, action, state.selectedTab),
      }
    case SearchAll.RESET:
      return initialState;
    case SearchAll.REQUEST:
      // updates search term to reflect action
      return {
        ...state,
        inlineResults: {
          ...initialInlineResultsState,
        },
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
        filters: state.filters,
        inlineResults: {
          tables: newState.tables,
          users: newState.users,
          isLoading: false,
        },
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
    case InlineSearch.UPDATE:
      const { searchTerm, selectedTab, tables, users } = (<InlineSearchUpdate>action).payload;
      return {
        ...state,
        selectedTab,
        tables,
        users,
        search_term: searchTerm,
        filters: initialFilterState,
      };
    case InlineSearch.SUCCESS:
      const inlineResults = (<InlineSearchResponse>action).payload;
      return {
        ...state,
        inlineResults: {
          tables: inlineResults.tables,
          users: inlineResults.users,
          isLoading: false,
        },
      };
    case InlineSearch.FAILURE:
      return {
        ...state,
        inlineResults: {
          ...initialInlineResultsState,
        },
      };
    case InlineSearch.REQUEST:
    case InlineSearch.REQUEST_DEBOUNCE:
      return {
        ...state,
        inlineResults: {
          ...initialInlineResultsState,
          isLoading: true,
        }
      };
    default:
      return state;
  };
};
