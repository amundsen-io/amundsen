import {
  FileMetadata,
  Tag,
} from 'interfaces';

import {
  GetFileData,
  GetFileDataRequest,
  GetFileDataResponse,
  GetFileDescription,
  GetFileDescriptionRequest,
  GetFileDescriptionResponse,
  UpdateFileDescription,
  UpdateFileDescriptionRequest,
} from './types';

import { STATUS_CODES } from '../../constants';

export const initialPreviewState = {
  data: {},
  status: null,
};

export const initialFileDataState: FileMetadata = {
  badges: [],
  key: '',
  name: '',
  description: '',
};

export const initialState: FileMetadataReducerState = {
  isLoading: true,
  statusCode: null,
  fileData: initialFileDataState,
};

/* ACTIONS */
export function getFileData(
  key: string,
  searchIndex?: string,
  source?: string
): GetFileDataRequest {
  return {
    payload: {
      key,
      searchIndex,
      source,
    },
    type: GetFileData.REQUEST,
  };
}
export function getFileDataFailure(): GetFileDataResponse {
  return {
    type: GetFileData.FAILURE,
    payload: {
      data: initialFileDataState,
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
      tags: [],
    },
  };
}
export function getFileDataSuccess(
  data: FileMetadata,
  statusCode: number,
  tags: Tag[]
): GetFileDataResponse {
  return {
    type: GetFileData.SUCCESS,
    payload: {
      data,
      statusCode,
      tags,
    },
  };
}

export function getFileDescription(
  onSuccess?: () => any,
  onFailure?: () => any
): GetFileDescriptionRequest {
  return {
    payload: {
      onSuccess,
      onFailure,
    },
    type: GetFileDescription.REQUEST,
  };
}
export function getFileDescriptionFailure(
  fileMetadata: FileMetadata
): GetFileDescriptionResponse {
  return {
    type: GetFileDescription.FAILURE,
    payload: {
      fileMetadata,
    },
  };
}
export function getFileDescriptionSuccess(
  fileMetadata: FileMetadata
): GetFileDescriptionResponse {
  return {
    type: GetFileDescription.SUCCESS,
    payload: {
      fileMetadata,
    },
  };
}

export function updateFileDescription(
  newValue: string,
  onSuccess?: () => any,
  onFailure?: () => any
): UpdateFileDescriptionRequest {
  return {
    payload: {
      newValue,
      onSuccess,
      onFailure,
    },
    type: UpdateFileDescription.REQUEST,
  };
}

/* REDUCER */
export interface FileMetadataReducerState {
  dashboards?: {
    isLoading: boolean;
    errorMessage?: string;
  };
  isLoading: boolean;
  statusCode: number | null;
  fileData: FileMetadata;
}

export default function reducer(
  state: FileMetadataReducerState = initialState,
  action
): FileMetadataReducerState {
  switch (action.type) {
    case GetFileData.REQUEST:
      return initialState;
    case GetFileData.FAILURE:
      return {
        ...state,
        isLoading: false,
        statusCode: (<GetFileDataResponse>action).payload.statusCode,
        fileData: initialFileDataState,
      };
    case GetFileData.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: (<GetFileDataResponse>action).payload.statusCode,
        fileData: (<GetFileDataResponse>action).payload.data,
      };
    case GetFileDescription.FAILURE:
    case GetFileDescription.SUCCESS:
      return {
        ...state,
        fileData: (<GetFileDescriptionResponse>action).payload.fileMetadata,
      };
    default:
      return state;
  }
}
