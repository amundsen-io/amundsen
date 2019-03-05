import { TableResource } from '../../components/common/ResourceListItem/types';
export { TableResource };

/* API */
export type PopularTablesResponse = {
  msg: string;
  results: TableResource[];
}

/* getPopularTables */
export enum GetPopularTables {
  ACTION = 'amundsen/popularTables/GET_POPULAR_TABLES',
  SUCCESS = 'amundsen/popularTables/GET_POPULAR_TABLES_SUCCESS',
  FAILURE = 'amundsen/popularTables/GET_POPULAR_TABLES_FAILURE',
}

export interface GetPopularTablesRequest {
  type: GetPopularTables.ACTION;
}

export interface GetPopularTablesResponse {
  type: GetPopularTables.SUCCESS | GetPopularTables.FAILURE;
  payload: TableResource[];
}
