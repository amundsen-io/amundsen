import { ServiceMetaData } from 'interfaces/Service';

export enum GetService {
  REQUEST = 'amundsen/service/GET_SERVICE_REQUEST',
  SUCCESS = 'amundsen/service/GET_SERVICE_SUCCESS',
  FAILURE = 'amundsen/service/GET_SERVICE_FAILURE',
}
export interface GetServiceRequest {
  type: GetService.REQUEST;
  payload: {
    key: string;
    index?: string;
    source?: string;
  };
}

export interface GetServicePayload {
  service?: ServiceMetaData;
  statusCode?: number;
  statusMessage?: string;
}

export interface GetServiceResponse {
  type: GetService.SUCCESS | GetService.FAILURE;
  payload: GetServicePayload;
}
