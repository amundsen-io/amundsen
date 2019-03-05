import {
  GetTableData, GetTableDataRequest, GetTableDataResponse,
  UpdateTags, UpdateTagsRequest, UpdateTagsResponse,
  UpdateTagData, Tag,
} from '../types';

export type TableTagsReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  UpdateTagsRequest | UpdateTagsResponse;

export interface TableTagsReducerState {
  isLoading: boolean;
  tags: Tag[];
}

export function updateTags(tagArray: UpdateTagData[]): UpdateTagsRequest  {
  return {
    tagArray,
    type: UpdateTags.ACTION,
  };
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
