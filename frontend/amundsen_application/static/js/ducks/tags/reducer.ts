import { Tag } from '../../components/Tags/types';

/* getAllTags */
export enum GetAllTags {
  ACTION = 'amundsen/tags/GET_ALL_TAGS',
  SUCCESS = 'amundsen/tags/GET_ALL_TAGS_SUCCESS',
  FAILURE = 'amundsen/tags/GET_ALL_TAGS_FAILURE',
}

export interface GetAllTagsRequest {
  type: GetAllTags.ACTION;
}
interface GetAllTagsResponse {
  type: GetAllTags.SUCCESS | GetAllTags.FAILURE;
  payload: Tag[];
}
type GetAllTagsAction = GetAllTagsRequest | GetAllTagsResponse;

export function getAllTags(): GetAllTagsRequest {
  return { type: GetAllTags.ACTION };
}
/* end getAllTags */

export type TagReducerAction = GetAllTagsAction;

export interface TagReducerState {
  allTags: Tag[];
  isLoading: boolean;
}

const initialState: TagReducerState = {
  allTags: [],
  isLoading: false,
};

export default function reducer(state: TagReducerState = initialState, action: TagReducerAction): TagReducerState {
  switch (action.type) {
    case GetAllTags.ACTION:
      return { ...state, isLoading: true };
    case GetAllTags.FAILURE:
    case GetAllTags.SUCCESS:
      return { ...state, allTags: action.payload, isLoading: false };
    default:
      return state;
  }
}
