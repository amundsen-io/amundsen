import { Tag } from '../../components/Tags/types';
export { Tag };

/* API */
export type AllTagsResponse = {
  msg: string;
  tags: Tag[];
}

/* getAllTags */
export enum GetAllTags {
  ACTION = 'amundsen/allTags/GET_ALL_TAGS',
  SUCCESS = 'amundsen/allTags/GET_ALL_TAGS_SUCCESS',
  FAILURE = 'amundsen/allTags/GET_ALL_TAGS_FAILURE',
}
export interface GetAllTagsRequest {
  type: GetAllTags.ACTION;
}
export interface GetAllTagsResponse {
  type: GetAllTags.SUCCESS | GetAllTags.FAILURE;
  payload: Tag[];
}
