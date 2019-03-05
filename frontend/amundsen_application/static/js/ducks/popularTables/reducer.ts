import {
  GetPopularTables,
  GetPopularTablesRequest,
  GetPopularTablesResponse,
  TableResource,
} from './types';

export type PopularTablesReducerAction = GetPopularTablesRequest | GetPopularTablesResponse;

export type PopularTablesReducerState = TableResource[];

export function getPopularTables(): GetPopularTablesRequest {
  return { type: GetPopularTables.ACTION };
}

const initialState: PopularTablesReducerState = [];

export default function reducer(state: PopularTablesReducerState = initialState, action: PopularTablesReducerAction): PopularTablesReducerState {
  switch (action.type) {
    case GetPopularTables.SUCCESS:
    case GetPopularTables.FAILURE:
      return action.payload;
    default:
      return state;
  }
}
