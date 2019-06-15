import axios, { AxiosResponse } from 'axios';

import { TableResource } from 'interfaces';

export type PopularTablesResponse = {
  msg: string;
  results: TableResource[];
}

export function metadataPopularTables() {
  return axios.get('/api/metadata/v0/popular_tables')
  .then((response: AxiosResponse<PopularTablesResponse>) => {
    return response.data.results;
  });
}
