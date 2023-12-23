import {
  DashboardResource,
  ProviderMetadata,
  Tag,
} from 'interfaces';

import {
  GetProviderDashboards,
  GetProviderDashboardsResponse,
  GetProviderData,
  GetProviderDataRequest,
  GetProviderDataResponse,
  GetProviderDescription,
  GetProviderDescriptionRequest,
  GetProviderDescriptionResponse,
  UpdateProviderDescription,
  UpdateProviderDescriptionRequest,
} from './types';

import { STATUS_CODES } from '../../constants';

export const initialPreviewState = {
  data: {},
  status: null,
};

export const initialProviderDataState: ProviderMetadata = {
  badges: [],
  key: '',
  name: '',
  description: '',
  is_editable: true,
  programmatic_descriptions: {},  
};

export const initialState: ProviderMetadataReducerState = {
  isLoading: true,
  statusCode: null,
  providerData: initialProviderDataState,
};

/* ACTIONS */
export function getProviderData(
  key: string,
  searchIndex?: string,
  source?: string
): GetProviderDataRequest {
  return {
    payload: {
      key,
      searchIndex,
      source,
    },
    type: GetProviderData.REQUEST,
  };
}
export function getProviderDataFailure(): GetProviderDataResponse {
  return {
    type: GetProviderData.FAILURE,
    payload: {
      data: initialProviderDataState,
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
      tags: [],
    },
  };
}
export function getProviderDataSuccess(
  data: ProviderMetadata,
  statusCode: number,
  tags: Tag[]
): GetProviderDataResponse {
  return {
    type: GetProviderData.SUCCESS,
    payload: {
      data,
      statusCode,
      tags,
    },
  };
}

export function getProviderDashboardsResponse(
  dashboards: DashboardResource[],
  errorMessage: string = ''
): GetProviderDashboardsResponse {
  return {
    type: GetProviderDashboards.RESPONSE,
    payload: {
      dashboards,
      errorMessage,
    },
  };
}

export function getProviderDescription(
  onSuccess?: () => any,
  onFailure?: () => any
): GetProviderDescriptionRequest {
  return {
    payload: {
      onSuccess,
      onFailure,
    },
    type: GetProviderDescription.REQUEST,
  };
}
export function getProviderDescriptionFailure(
  providerMetadata: ProviderMetadata
): GetProviderDescriptionResponse {
  return {
    type: GetProviderDescription.FAILURE,
    payload: {
      providerMetadata,
    },
  };
}
export function getProviderDescriptionSuccess(
  providerMetadata: ProviderMetadata
): GetProviderDescriptionResponse {
  return {
    type: GetProviderDescription.SUCCESS,
    payload: {
      providerMetadata,
    },
  };
}

export function updateProviderDescription(
  newValue: string,
  onSuccess?: () => any,
  onFailure?: () => any
): UpdateProviderDescriptionRequest {
  return {
    payload: {
      newValue,
      onSuccess,
      onFailure,
    },
    type: UpdateProviderDescription.REQUEST,
  };
}

/* REDUCER */
export interface ProviderMetadataReducerState {
  dashboards?: {
    isLoading: boolean;
    dashboards: DashboardResource[];
    errorMessage?: string;
  };
  isLoading: boolean;
  statusCode: number | null;
  providerData: ProviderMetadata;
}

export default function reducer(
  state: ProviderMetadataReducerState = initialState,
  action
): ProviderMetadataReducerState {
  switch (action.type) {
    case GetProviderDashboards.RESPONSE:
      return {
        ...state,
        dashboards: {
          isLoading: false,
          dashboards: action.payload.dashboards,
          errorMessage: action.payload.errorMessage,
        },
      };
    case GetProviderData.REQUEST:
      return initialState;
    case GetProviderData.FAILURE:
      return {
        ...state,
        isLoading: false,
        statusCode: (<GetProviderDataResponse>action).payload.statusCode,
        providerData: initialProviderDataState,
      };
    case GetProviderData.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: (<GetProviderDataResponse>action).payload.statusCode,
        providerData: (<GetProviderDataResponse>action).payload.data,
      };
    case GetProviderDescription.FAILURE:
    case GetProviderDescription.SUCCESS:
      return {
        ...state,
        providerData: (<GetProviderDescriptionResponse>action).payload.providerMetadata,
      };
    default:
      return state;
  }
}
