import axios, { AxiosResponse, AxiosError } from 'axios';

import { AllTagsResponse } from '../types';

import { sortTagsAlphabetical } from '../../utilMethods';

export function metadataAllTags() {
  return axios.get('/api/metadata/v0/tags').then((response: AxiosResponse<AllTagsResponse>) => {
    return response.data.tags.sort(sortTagsAlphabetical);
  })
  .catch((error: AxiosError) => {
    if (error.response) {
      return error.response.data.tags.sort(sortTagsAlphabetical);
    }
    return [];
  });
}
