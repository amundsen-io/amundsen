import {
  SubmitSearchResource,
  SubmitSearchResourceRequest,
} from 'ducks/search/types';
import { ResourceType } from 'interfaces';

/* ACTION TYPES */
export enum UpdateSearchFilter {
  REQUEST = 'amundsen/search/filter/UPDATE_SEARCH_FILTER_REQUEST',
}
export type UpdateFilterPayload = {
  categoryId: string;
  values: string[] | undefined;
  operation: string;
};
export interface UpdateFilterRequest {
  payload: UpdateFilterPayload;
  type: UpdateSearchFilter.REQUEST;
}

/* ACTIONS */
export function updateFilterByCategory({
  categoryId,
  values,
  operation,
}: UpdateFilterPayload): UpdateFilterRequest {
  return {
    payload: {
      categoryId,
      values,
      operation,
    },
    type: UpdateSearchFilter.REQUEST,
  };
}

/* REDUCER TYPES */
export interface FilterState {
  values: string[];
  operation: string;
}


export interface FilterReducerState {
  [categoryId: string]: FilterState; 
}

/* REDUCER */

export const initialFilterState: FilterReducerState = {};

export default function reducer(
  state: FilterReducerState = initialFilterState,
  action
): FilterReducerState {
  switch (action.type) {
    case SubmitSearchResource.REQUEST:
      const { payload } = <SubmitSearchResourceRequest>action;
      if (payload.resourceFilters) {
        return {
          ...state,
          payload.resourceFilters,
        };
      }
      return state;
    default:
      return state;
  }
}
