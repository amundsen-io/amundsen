import {
  SubmitSearchResource,
  SubmitSearchResourceRequest,
} from 'ducks/search/types';
import {
  FilterOperationType,
  ResourceType,
  SearchFilterInput,
} from 'interfaces';
import appConfig from 'config/config';

/* ACTION TYPES */
export enum UpdateSearchFilter {
  REQUEST = 'amundsen/search/filter/UPDATE_SEARCH_FILTER_REQUEST',
}
export type UpdateFilterPayload = {
  searchFilters: SearchFilterInput[];
};
export interface UpdateFilterRequest {
  payload: UpdateFilterPayload;
  type: UpdateSearchFilter.REQUEST;
}

/* ACTIONS */
export function updateFilterByCategory({
  searchFilters,
}: UpdateFilterPayload): UpdateFilterRequest {
  return {
    payload: {
      searchFilters,
    },
    type: UpdateSearchFilter.REQUEST,
  };
}

/* REDUCER TYPES */
export interface FilterReducerState {
  [ResourceType.dashboard]?: ResourceFilterReducerState;
  [ResourceType.table]?: ResourceFilterReducerState;
  [ResourceType.feature]?: ResourceFilterReducerState;
}

export interface ResourceFilterReducerState {
  [categoryId: string]: {
    value: string;
    filterOperation?: FilterOperationType;
  };
}

export function getDefaultFiltersForResource(
  resourceType: ResourceType
): ResourceFilterReducerState {
  const defaultFilters = {};
  const resourceConfig = appConfig.resourceConfig[resourceType];
  resourceConfig.filterCategories.forEach((filter) => {
    const filterDefaultValue: string[] = filter.defaultValue;
    if (filterDefaultValue && filterDefaultValue !== []) {
      defaultFilters[filter.categoryId] = {
        value: filterDefaultValue.join(),
        filterOperation: filter.allowableOperation,
      };
    }
  });
  return defaultFilters;
}

/* REDUCER */
export const initialTableFilterState = getDefaultFiltersForResource(
  ResourceType.table
);
export const initialDashboardFilterState = getDefaultFiltersForResource(
  ResourceType.dashboard
);
export const initialFeatureFilterState = getDefaultFiltersForResource(
  ResourceType.feature
);

export const initialFilterState: FilterReducerState = {
  [ResourceType.dashboard]: initialDashboardFilterState,
  [ResourceType.table]: initialTableFilterState,
  [ResourceType.feature]: initialFeatureFilterState,
};

export default function reducer(
  state: FilterReducerState = initialFilterState,
  action
): FilterReducerState {
  const { payload } = <SubmitSearchResourceRequest>action;
  switch (action.type) {
    case SubmitSearchResource.REQUEST:
      if (payload.resource && payload.resourceFilters) {
        return {
          ...state,
          [payload.resource]: payload.resourceFilters,
        };
      }
      return state;
    default:
      return state;
  }
}
