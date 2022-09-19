import { AppEventMetaData } from 'interfaces/AppEvent';

export enum GetAppEvent {
  REQUEST = 'amundsen/events/GET_APP_EVENT_REQUEST',
  SUCCESS = 'amundsen/events/GET_APP_EVENT_SUCCESS',
  FAILURE = 'amundsen/events/GET_APP_EVENT_FAILURE',
}
export interface GetAppEventRequest {
  type: GetAppEvent.REQUEST;
  payload: {
    key: string;
    index?: string;
    source?: string;
  };
}

export interface GetAppEventPayload {
  events?: AppEventMetaData;
  statusCode?: number;
  statusMessage?: string;
}

export interface GetAppEventResponse {
  type: GetAppEvent.SUCCESS | GetAppEvent.FAILURE;
  payload: GetAppEventPayload;
}
