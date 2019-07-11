import axios, { AxiosResponse } from 'axios';

import { sortTagsAlphabetical } from 'ducks/utilMethods';
import { Tag } from 'interfaces';

export type AllTagsAPI = {
  msg: string;
  tags: Tag[];
};

export function getAllTags() {
  return axios.get('/api/metadata/v0/tags').then((response: AxiosResponse<AllTagsAPI>) => {
    return response.data.tags.sort(sortTagsAlphabetical);
  })
};
