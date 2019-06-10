import axios, { AxiosResponse } from 'axios';

import { sortTagsAlphabetical } from 'ducks/utilMethods';
import { Tag } from 'interfaces';

export type AllTagsResponseAPI = {
  msg: string;
  tags: Tag[];
};

export function metadataAllTags() {
  return axios.get('/api/metadata/v0/tags').then((response: AxiosResponse<AllTagsResponseAPI>) => {
    return response.data.tags.sort(sortTagsAlphabetical);
  })
};
