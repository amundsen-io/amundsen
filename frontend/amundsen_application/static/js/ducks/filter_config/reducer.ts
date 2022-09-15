import { ResourceType } from 'interfaces';
import { GetFilterConfig } from './saga';

export type OptionsType = {
  displayName: string;
};

export type TypeFilter = {
  categoryId: string;
  displayName: string;
  helpText: string;
  type: string;
  options?: Array<OptionsType>;
};

export interface ResourceFilterReducerState {
  filterCategories: Array<TypeFilter>;
}

export interface FilterReducerState {
  config: {
    [ResourceType.dashboard]?: ResourceFilterReducerState;
    [ResourceType.table]?: ResourceFilterReducerState;
    [ResourceType.feature]?: ResourceFilterReducerState;
    [ResourceType.service]?: ResourceFilterReducerState;
    [ResourceType.user]?: ResourceFilterReducerState;
  };
  fetching: boolean;
}

export const initialTableFilterState = { filterCategories: [] };
export const initialDashboardFilterState = { filterCategories: [] };
export const initialFeatureFilterState = { filterCategories: [] };
export const initialServiceFilterState = { filterCategories: [] };
export const initialUserFilterState = { filterCategories: [] };

export const initialFilterState: FilterReducerState = {
  config: {
    [ResourceType.dashboard]: initialDashboardFilterState,
    [ResourceType.table]: initialTableFilterState,
    [ResourceType.feature]: initialFeatureFilterState,
    [ResourceType.service]: initialServiceFilterState,
    [ResourceType.user]: initialUserFilterState,
  },
  fetching: false,
};

export function getFilterConfig() {
  return {
    type: GetFilterConfig.REQUEST,
  };
}

export function getFilterConfigSuccess(payload: FilterReducerState) {
  return {
    payload,
    type: GetFilterConfig.SUCCESS,
  };
}

export function getFilterConfigFailure(payload: FilterReducerState) {
  return {
    payload,
    type: GetFilterConfig.FAILED,
  };
}

export default function reducer(
  state: FilterReducerState = initialFilterState,
  action
): FilterReducerState {
  switch (action.type) {
    case GetFilterConfig.SUCCESS:
      return {
        ...state,
        config: {
          ...state.config,
          ...action.payload?.data,
        },
        fetching: false,
      };
    case GetFilterConfig.REQUEST:
      return {
        ...state,
        fetching: true,
      };
    case GetFilterConfig.FAILED:
      return {
        ...state,
        fetching: false,
      };
    default:
      return state;
  }
}
