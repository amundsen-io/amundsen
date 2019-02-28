import axios from 'axios';

export function metadataPopularTables() {
  return axios.get('/api/metadata/v0/popular_tables').then((response) => {
    return response.data.results;
  })
  .catch((error) => {
    return error.response.data.results;
  });
}
