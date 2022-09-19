import {
  GetAppEvent,
  GetAppEventRequest,
  GetAppEventResponse,
  GetAppEventPayload,
} from 'ducks/app_event/types';

import { AppEventMetaData } from 'interfaces/AppEvent';

export function getAppEvent(
  key: string,
  index?: string,
  source?: string
): GetAppEventRequest {
  return {
    payload: {
      key,
      index,
      source,
    },
    type: GetAppEvent.REQUEST,
  };
}

export function getAppEventSuccess(
  payload: GetAppEventPayload
): GetAppEventResponse {
  return {
    payload,
    type: GetAppEvent.SUCCESS,
  };
}

export function getAppEventFailure(
  payload: GetAppEventPayload
): GetAppEventResponse {
  return {
    payload,
    type: GetAppEvent.FAILURE,
  };
}

export interface AppEventReducerState {
  isLoading: boolean;
  statusCode: number | null;
  appEvent: AppEventMetaData;
}

export const initialAppEventState: AppEventMetaData = {
  key: '',
  name: '',
  description: '',
  last_updated_timestamp: 0,
  created_timestamp: 0,
  attributes: [],
  owned_by: '',
  label: '',
  category: '',
  source: '',
  vertical: '',
  action: '',
};

export const initialState: AppEventReducerState = {
  isLoading: false,
  statusCode: null,
  appEvent: initialAppEventState,
};

export default function reducer(
  state: AppEventReducerState = initialState,
  action
): AppEventReducerState {
  switch (action.type) {
    case GetAppEvent.REQUEST:
      return {
        ...state,
        statusCode: null,
        isLoading: true,
      };
    case GetAppEvent.FAILURE:
      return {
        ...state,
        isLoading: false,
        appEvent: initialAppEventState,
        statusCode: action.payload.statusCode,
      };
    case GetAppEvent.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        appEvent: action.payload.appEvent,
      };
    default:
      return state;
  }
}
