import axios, { AxiosResponse, AxiosError } from 'axios';

import { PopularTablesResponse } from '../types';

export function metadataPopularTables() {
  return axios.get('/api/metadata/v0/popular_tables')
  .then((response: AxiosResponse<PopularTablesResponse>) => {
    return response.data.results;
  })
  .catch((error: AxiosError) => {
    if (error.response) {
      return error.response.data.results;
    }
    return [];
  });
}
