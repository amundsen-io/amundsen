import { Tag } from 'interfaces';

export enum GetAllTags {
  REQUEST = 'amundsen/allTags/GET_REQUEST',
  SUCCESS = 'amundsen/allTags/GET_SUCCESS',
  FAILURE = 'amundsen/allTags/GET_FAILURE',
}
export interface GetAllTagsRequest {
  type: GetAllTags.REQUEST;
}
export interface GetAllTagsResponse {
  type: GetAllTags.SUCCESS | GetAllTags.FAILURE;
  payload: {
    allTags: Tag[];
  };
}
