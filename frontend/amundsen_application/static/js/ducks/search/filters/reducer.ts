import { ResourceType } from 'interfaces';

import { filterFromObj } from 'ducks/utilMethods';

/* ACTION TYPES */
export enum UpdateSearchFilter {
  CLEAR_ALL = 'amundsen/search/filter/CLEAR_ALL',
  CLEAR_CATEGORY = 'amundsen/search/filter/CLEAR_CATEGORY',
  SET_BY_RESOURCE = 'amundsen/search/filter/SET_BY_RESOURCE',
  UPDATE_CATEGORY = 'amundsen/search/filter/UPDATE_CATEGORY',
};

interface ClearAllFiltersRequest {
  type: UpdateSearchFilter.CLEAR_ALL;
};

export interface ClearFilterRequest {
  payload: {
    categoryId: string;
  };
  type: UpdateSearchFilter.CLEAR_CATEGORY;
};

export interface SetSearchInputRequest {
  payload: {
    filters: ResourceFilterReducerState;
    pageIndex?: number;
    resourceType: ResourceType;
    term?: string;
  };
  type: UpdateSearchFilter.SET_BY_RESOURCE;
};

export interface UpdateFilterRequest {
  payload: {
    categoryId: string;
    value: string | FilterOptions;
  };
  type: UpdateSearchFilter.UPDATE_CATEGORY;
};

/* ACTIONS */
export function clearAllFilters(): ClearAllFiltersRequest {
  return {
    type: UpdateSearchFilter.CLEAR_ALL,
  };
};

export function clearFilterByCategory(categoryId: string): ClearFilterRequest {
  return {
    payload: {
      categoryId,
    },
    type: UpdateSearchFilter.CLEAR_CATEGORY,
  };
};

export function setSearchInputByResource(filters: ResourceFilterReducerState,
                                         resourceType: ResourceType,
                                         pageIndex?: number,
                                         term?: string): SetSearchInputRequest {
  return {
    payload: {
      filters,
      pageIndex,
      resourceType,
      term
    },
    type: UpdateSearchFilter.SET_BY_RESOURCE,
  };
};

export function updateFilterByCategory(categoryId: string, value: string | FilterOptions): UpdateFilterRequest {
  return {
    payload: {
      categoryId,
      value
    },
    type: UpdateSearchFilter.UPDATE_CATEGORY,
  };
};

/* REDUCER TYPES */
export type FilterOptions = { [id:string]: boolean };

export interface FilterReducerState {
  [ResourceType.table]: ResourceFilterReducerState;
};

export interface ResourceFilterReducerState {
  [categoryId: string]: string | FilterOptions;
};

/* REDUCER */
export const initialTableFilterState = {};

export const initialFilterState: FilterReducerState = {
  [ResourceType.table]: initialTableFilterState,
};

export default function reducer(state: FilterReducerState = initialFilterState, action, resourceType: ResourceType): FilterReducerState {
  const resourceFilters = state[resourceType];
  const { payload, type } = action;

  switch (type) {
    case UpdateSearchFilter.CLEAR_ALL:
      return initialFilterState;
    case UpdateSearchFilter.CLEAR_CATEGORY:
      return {
        ...state,
        [resourceType]: filterFromObj(resourceFilters, [payload.categoryId])
      };
    case UpdateSearchFilter.SET_BY_RESOURCE:
      return {
        ...state,
        [payload.resourceType]: payload.filters
      };
    case UpdateSearchFilter.UPDATE_CATEGORY:
      return {
        ...state,
        [resourceType]: {
          ...resourceFilters,
          [payload.categoryId]: payload.value
        }
      };
    default:
      return state;
  };
};
