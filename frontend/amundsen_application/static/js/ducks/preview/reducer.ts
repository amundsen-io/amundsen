import { PreviewData, PreviewQueryParams } from '../../components/TableDetail/types';

/* getPreviewData */
export enum GetPreviewData {
  ACTION = 'amundsen/preview/GET_PREVIEW_DATA',
  SUCCESS = 'amundsen/preview/GET_PREVIEW_DATA_SUCCESS',
  FAILURE = 'amundsen/preview/GET_PREVIEW_DATA_FAILURE',
}

export interface GetPreviewDataRequest {
  type: GetPreviewData.ACTION;
  queryParams: PreviewQueryParams;
}

interface GetPreviewDataResponse {
  type: GetPreviewData.SUCCESS | GetPreviewData.FAILURE;
  payload: PreviewDataReducerState;
}

export function getPreviewData(queryParams: PreviewQueryParams): GetPreviewDataRequest {
  return { queryParams, type: GetPreviewData.ACTION };
}
/* end getPreviewData */

export type PreviewDataReducerAction = GetPreviewDataRequest | GetPreviewDataResponse;

export type PreviewDataReducerState = {
  previewData: PreviewData;
  status: number;
}

const initialState: PreviewDataReducerState = {
  previewData: {},
  status: null,
};

export default function reducer(state: PreviewDataReducerState = initialState, action: PreviewDataReducerAction): PreviewDataReducerState {
  switch (action.type) {
    case GetPreviewData.SUCCESS:
    case GetPreviewData.FAILURE:
      return action.payload;
    default:
      return state;
  }
}
