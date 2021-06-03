import { TableResource } from 'interfaces';

export enum GetPopularTables {
  REQUEST = 'amundsen/popularTables/GET_POPULAR_TABLES_REQUEST',
  SUCCESS = 'amundsen/popularTables/GET_POPULAR_TABLES_SUCCESS',
  FAILURE = 'amundsen/popularTables/GET_POPULAR_TABLES_FAILURE',
}
export interface GetPopularTablesRequest {
  type: GetPopularTables.REQUEST;
}
export interface GetPopularTablesResponse {
  type: GetPopularTables.SUCCESS | GetPopularTables.FAILURE;
  payload: {
    tables: TableResource[];
  };
}
