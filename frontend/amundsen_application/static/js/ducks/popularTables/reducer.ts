import { TableResource } from 'interfaces';

import {
  GetPopularTables,
  GetPopularTablesRequest,
  GetPopularTablesResponse,
} from './types';

/* ACTIONS */
export function getPopularTables(): GetPopularTablesRequest {
  return { type: GetPopularTables.REQUEST };
}
export function getPopularTablesFailure(): GetPopularTablesResponse {
  return { type: GetPopularTables.FAILURE, payload: { tables: [] } };
}
export function getPopularTablesSuccess(
  tables: TableResource[]
): GetPopularTablesResponse {
  return { type: GetPopularTables.SUCCESS, payload: { tables } };
}

/* REDUCER */
export interface PopularTablesReducerState {
  popularTables: TableResource[];
  popularTablesIsLoaded: boolean;
}

const initialState: PopularTablesReducerState = {
  popularTables: [],
  popularTablesIsLoaded: false,
};

export default function reducer(
  state: PopularTablesReducerState = initialState,
  action
): PopularTablesReducerState {
  switch (action.type) {
    case GetPopularTables.REQUEST:
      return {
        ...state,
        ...initialState,
      };
    case GetPopularTables.SUCCESS:
    case GetPopularTables.FAILURE:
      return {
        ...state,
        popularTables: (<GetPopularTablesResponse>action).payload.tables,
        popularTablesIsLoaded: true,
      };
    default:
      return state;
  }
}
