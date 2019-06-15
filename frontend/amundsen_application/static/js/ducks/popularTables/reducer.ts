import { TableResource } from 'interfaces'

import {
  GetPopularTables,
  GetPopularTablesRequest,
  GetPopularTablesResponse,
} from './types';

/* ACTIONS */
export function getPopularTables(): GetPopularTablesRequest {
  return { type: GetPopularTables.REQUEST };
}

/* REDUCER */
export type PopularTablesReducerState = TableResource[];

const initialState: PopularTablesReducerState = [];

export default function reducer(state: PopularTablesReducerState = initialState, action): PopularTablesReducerState {
  switch (action.type) {
    case GetPopularTables.SUCCESS:
    case GetPopularTables.FAILURE:
      return (<GetPopularTablesResponse>action).payload.tables;
    default:
      return state;
  }
}
