import {
  AnalyticsEvent,
  DashboardResource,
  OwnerDict,
  ProviderMetadata,
  UpdateOwnerPayload,
  Tag,
} from 'interfaces';

export enum GetProviderData {
  REQUEST = 'amundsen/providerMetadata/GET_PROVIDER_DATA_REQUEST',
  SUCCESS = 'amundsen/providerMetadata/GET_PROVIDER_DATA_SUCCESS',
  FAILURE = 'amundsen/providerMetadata/GET_PROVIDER_DATA_FAILURE',
}
export interface GetProviderDataRequest {
  type: GetProviderData.REQUEST;
  payload: {
    key: string;
    searchIndex?: string;
    source?: string;
  };
}
export interface GetProviderDataResponse {
  type: GetProviderData.SUCCESS | GetProviderData.FAILURE;
  payload: {
    statusCode: number | null;
    data: ProviderMetadata;
    tags: Tag[];
  };
}

export enum GetProviderDescription {
  REQUEST = 'amundsen/providerMetadata/GET_PROVIDER_DESCRIPTION_REQUEST',
  SUCCESS = 'amundsen/providerMetadata/GET_PROVIDER_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/providerMetadata/GET_PROVIDER_DESCRIPTION_FAILURE',
}
export interface GetProviderDescriptionRequest {
  type: GetProviderDescription.REQUEST;
  payload: {
    onSuccess?: () => any;
    onFailure?: () => any;
  };
}
export interface GetProviderDescriptionResponse {
  type: GetProviderDescription.SUCCESS | GetProviderDescription.FAILURE;
  payload: {
    providerMetadata: ProviderMetadata;
  };
}

export enum UpdateProviderDescription {
  REQUEST = 'amundsen/providerMetadata/UPDATE_PROVIDER_DESCRIPTION_REQUEST',
  SUCCESS = 'amundsen/providerMetadata/UPDATE_PROVIDER_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/providerMetadata/UPDATE_PROVIDER_DESCRIPTION_FAILURE',
}
export interface UpdateProviderDescriptionRequest {
  type: UpdateProviderDescription.REQUEST;
  payload: {
    newValue: string;
    onSuccess?: () => any;
    onFailure?: () => any;
  };
}
export interface UpdateProviderDescriptionResponse {
  type: UpdateProviderDescription.SUCCESS | UpdateProviderDescription.FAILURE;
}
