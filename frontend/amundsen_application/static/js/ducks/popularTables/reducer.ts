import { TableResource } from "../../components/common/ResourceListItem/types";

/* getPopularTables */
export enum GetPopularTables {
  ACTION = 'amundsen/popularTables/GET_POPULAR_TABLES',
  SUCCESS = 'amundsen/popularTables/GET_POPULAR_TABLES_SUCCESS',
  FAILURE = 'amundsen/popularTables/GET_POPULAR_TABLES_FAILURE',
}

export interface GetPopularTablesRequest {
  type: GetPopularTables.ACTION;
}

interface GetPopularTablesResponse {
  type: GetPopularTables.SUCCESS | GetPopularTables.FAILURE;
  payload: TableResource[];
}

export function getPopularTables(): GetPopularTablesRequest {
  return { type: GetPopularTables.ACTION };
}
/* end getPopularTables */

export type PopularTablesReducerAction = GetPopularTablesRequest | GetPopularTablesResponse;

export type PopularTablesReducerState = TableResource[];

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
