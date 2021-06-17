import { FeatureMetadata } from 'interfaces/Feature';

export enum GetFeature {
  REQUEST = 'amundsen/feature/GET_FEATURE_REQUEST',
  SUCCESS = 'amundsen/feature/GET_FEATURE_SUCCESS',
  FAILURE = 'amundsen/feature/GET_FEATURE_FAILURE',
}

export interface GetFeatureRequest {
  type: GetFeature.REQUEST;
  payload: {
    key: string;
    index?: string;
    source?: string;
  };
}

export interface GetFeatureResponse {
  type: GetFeature.SUCCESS | GetFeature.FAILURE;
  payload: GetFeaturePayload;
}

export interface GetFeaturePayload {
  feature?: FeatureMetadata;
  statusCode?: number;
  statusMessage?: string;
}
