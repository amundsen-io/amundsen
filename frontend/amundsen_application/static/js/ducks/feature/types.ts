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

export enum GetFeatureDescription {
  REQUEST = 'amundsen/feature/GET_FEATURE_DESCRIPTION_REQUEST',
  SUCCESS = 'amundsen/feature/GET_FEATURE_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/feature/GET_FEATURE_DESCRIPTION_FAILURE',
}

export interface GetFeatureDescriptionRequest {
  type: GetFeatureDescription.REQUEST;
  payload: {
    onSuccess?: () => any;
    onFailure?: () => any;
  };
}

export interface GetFeatureDescriptionResponse {
  type: GetFeatureDescription.SUCCESS | GetFeatureDescription.FAILURE;
  payload: GetFeatureDescriptionPayload;
}

export interface GetFeatureDescriptionPayload {
  description?: string;
  statusCode?: number;
  statusMessage?: string;
}

export enum UpdateFeatureDescription {
  REQUEST = 'amundsen/feature/UPDATE_FEATURE_DESCRIPTION_REQUEST',
  SUCCESS = 'amundsen/feature/UPDATE_FEATURE_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/feature/UPDATE_FEATURE_DESCRIPTION_FAILURE',
}

export interface UpdateFeatureDescriptionRequest {
  type: UpdateFeatureDescription.REQUEST;
  payload: {
    newValue: string;
    onSuccess?: () => any;
    onFailure?: () => any;
  };
}

export interface UpdateFeatureDescriptionResponse {
  type: UpdateFeatureDescription.SUCCESS | UpdateFeatureDescription.FAILURE;
  payload: UpdateFeatureDescriptionPayload;
}

export interface UpdateFeatureDescriptionPayload {
  description?: string;
  statusCode?: number;
  statusMessage?: string;
}
