import { GetTableData, GetTableDataRequest, GetTableDataResponse } from '../reducer';
import { UpdateTagData, Tag } from '../../../components/Tags/types';

/* updateTags */
export enum UpdateTags {
  ACTION = 'amundsen/tags/UPDATE_TAGS',
  SUCCESS = 'amundsen/tags/UPDATE_TAGS_SUCCESS',
  FAILURE = 'amundsen/tags/UPDATE_TAGS_FAILURE',
}

export interface UpdateTagsRequest {
  type: UpdateTags.ACTION,
  tagArray: UpdateTagData[];
}

export interface UpdateTagsResponse {
  type: UpdateTags.SUCCESS | UpdateTags.FAILURE,
  payload: Tag[];
}

export function updateTags(tagArray: UpdateTagData[]): UpdateTagsRequest  {
  return {
    tagArray,
    type: UpdateTags.ACTION,
  };
}
/* end updateTags */

export type TableTagsReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  UpdateTagsRequest | UpdateTagsResponse;

export interface TableTagsReducerState {
  isLoading: boolean;
  tags: Tag[];
}

export const initialTagsState: TableTagsReducerState = {
  isLoading: true,
  tags: [],
};

export default function reducer(state: TableTagsReducerState = initialTagsState, action: TableTagsReducerAction): TableTagsReducerState {
  switch (action.type) {
    case GetTableData.ACTION:
      return { isLoading: true, tags: [] };
    case GetTableData.FAILURE:
    case GetTableData.SUCCESS:
      return { isLoading: false, tags: action.payload.tags };
    case UpdateTags.FAILURE:
      return { ...state, isLoading: false };
    case UpdateTags.SUCCESS:
      return { isLoading: false, tags: action.payload };
    case UpdateTags.ACTION:
      return { ...state, isLoading: true };
    default:
      return state;
  }
}
