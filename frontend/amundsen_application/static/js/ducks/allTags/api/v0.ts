import axios from 'axios';

import { sortTagsAlphabetical } from '../../utilMethods';

export function metadataAllTags() {
  return axios.get('/api/metadata/v0/tags').then((response) => {
    return response.data.tags.sort(sortTagsAlphabetical);
  })
  .catch((error) => {
    return error.response.data.tags.sort(sortTagsAlphabetical);
  });
}
