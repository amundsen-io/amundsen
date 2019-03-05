import {
  GetAllTags, GetAllTagsRequest, GetAllTagsResponse,
  Tag,
} from './types';

export type AllTagsReducerAction = GetAllTagsRequest | GetAllTagsResponse;

export interface AllTagsReducerState {
  allTags: Tag[];
  isLoading: boolean;
}

export function getAllTags(): GetAllTagsRequest {
  return { type: GetAllTags.ACTION };
}

const initialState: AllTagsReducerState = {
  allTags: [],
  isLoading: false,
};

export default function reducer(state: AllTagsReducerState = initialState, action: AllTagsReducerAction): AllTagsReducerState {
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
