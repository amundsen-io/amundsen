import {
  GetService,
  GetServiceRequest,
  GetServiceResponse,
  GetServicePayload,
} from 'ducks/service/types';

import { ServiceMetaData } from 'interfaces/Service';

export function getService(
  key: string,
  index?: string,
  source?: string
): GetServiceRequest {
  return {
    payload: {
      key,
      index,
      source,
    },
    type: GetService.REQUEST,
  };
}

export function getServiceSuccess(
  payload: GetServicePayload
): GetServiceResponse {
  return {
    payload,
    type: GetService.SUCCESS,
  };
}

export function getServiceFailure(
  payload: GetServicePayload
): GetServiceResponse {
  return {
    payload,
    type: GetService.FAILURE,
  };
}

export interface ServiceReducerState {
  isLoading: boolean;
  statusCode: number | null;
  service: ServiceMetaData;
}

export const initialServiceState: ServiceMetaData = {
  key: '',
  name: '',
  description: '',
  criticality: '',
  last_updated_timestamp:0,
  owned_by : '',
  stack:'',
  tags : [],
  type : 'service',
  created_timestamp : 0,
  attributes : []
};

export const initialState: ServiceReducerState = {
  isLoading: false,
  statusCode: null,
  service: initialServiceState,
};

export default function reducer(
  state: ServiceReducerState = initialState,
  action
): ServiceReducerState {
  switch (action.type) {
    case GetService.REQUEST:
      return {
        ...state,
        statusCode: null,
        isLoading: true,
      };
    case GetService.FAILURE:
      return {
        ...state,
        isLoading: false,
        service: initialServiceState,
        statusCode: action.payload.statusCode,
      };
    case GetService.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        service: action.payload.service,
      };
    default:
      return state;
  }
}
