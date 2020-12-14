import axios, { AxiosResponse } from 'axios';

import { TableResource } from 'interfaces';

export type PopularTablesAPI = {
  msg: string;
  results: TableResource[];
};

export function getPopularTables() {
  return axios
    .get('/api/metadata/v0/popular_tables')
    .then((response: AxiosResponse<PopularTablesAPI>) => response.data.results);
}
