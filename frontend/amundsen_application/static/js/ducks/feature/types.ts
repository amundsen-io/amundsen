import { FeatureCode, FeatureMetadata } from 'interfaces/Feature';

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

export enum GetFeatureCode {
  REQUEST = 'amundsen/feature/GET_FEATURE_CODE_REQUEST',
  SUCCESS = 'amundsen/feature/GET_FEATURE_CODE_SUCCESS',
  FAILURE = 'amundsen/feature/GET_FEATURE_CODE_FAILURE',
}

export interface GetFeatureCodeRequest {
  type: GetFeatureCode.REQUEST;
  payload: {
    key: string;
  };
}

export interface GetFeatureCodeResponse {
  type: GetFeatureCode.SUCCESS | GetFeatureCode.FAILURE;
  payload: GetFeatureCodePayload;
}

export interface GetFeatureCodePayload {
  featureCode?: FeatureCode;
  statusCode?: number;
  statusMessage?: string;
}
