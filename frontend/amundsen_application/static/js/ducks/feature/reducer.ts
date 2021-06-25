// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import {
  GetFeature,
  GetFeatureRequest,
  GetFeatureResponse,
  GetFeaturePayload,
  GetFeatureCodeRequest,
  GetFeatureCodePayload,
  GetFeatureCode,
  GetFeatureCodeResponse,
} from 'ducks/feature/types';
import { FeatureCode, FeatureMetadata } from 'interfaces/Feature';

/* Actions */

export function getFeature(
  key: string,
  index?: string,
  source?: string
): GetFeatureRequest {
  return {
    payload: {
      key,
      index,
      source,
    },
    type: GetFeature.REQUEST,
  };
}

export function getFeatureSuccess(
  payload: GetFeaturePayload
): GetFeatureResponse {
  return {
    payload,
    type: GetFeature.SUCCESS,
  };
}

export function getFeatureFailure(
  payload: GetFeaturePayload
): GetFeatureResponse {
  return {
    payload,
    type: GetFeature.FAILURE,
  };
}

export function getFeatureCode(key: string): GetFeatureCodeRequest {
  return {
    payload: {
      key,
    },
    type: GetFeatureCode.REQUEST,
  };
}
export function getFeatureCodeSuccess(
  payload: GetFeatureCodePayload
): GetFeatureCodeResponse {
  return {
    payload,
    type: GetFeatureCode.SUCCESS,
  };
}
export function getFeatureCodeFailure(
  payload: GetFeatureCodePayload
): GetFeatureCodeResponse {
  return {
    payload,
    type: GetFeatureCode.FAILURE,
  };
}

/* Reducer */
export interface FeatureCodeState {
  featureCode: FeatureCode;
  isLoading: boolean;
  statusCode: number | null;
}

export interface FeatureReducerState {
  isLoading: boolean;
  statusCode: number | null;
  feature: FeatureMetadata;
  featureCode: FeatureCodeState;
}

export const initialFeatureState: FeatureMetadata = {
  key: '',
  name: '',
  version: '',
  status: '',
  feature_group: '',
  entity: '',
  data_type: '',
  availability: [],
  description: '',
  owners: [],
  badges: [],
  owner_tags: [],
  tags: [],
  programmatic_descriptions: [],
  watermarks: [],
  stats: [],
  last_updated_timestamp: 0,
  created_timestamp: 0,
};

export const emptyFeatureCode: FeatureCode = {
  text: '',
  source: '',
  key: '',
};

export const initialFeatureCodeState: FeatureCodeState = {
  featureCode: emptyFeatureCode,
  isLoading: false,
  statusCode: null,
};

export const initialState: FeatureReducerState = {
  isLoading: true,
  statusCode: null,
  feature: initialFeatureState,
  featureCode: initialFeatureCodeState,
};

export default function reducer(
  state: FeatureReducerState = initialState,
  action
): FeatureReducerState {
  switch (action.type) {
    case GetFeature.REQUEST:
      return {
        ...state,
        statusCode: null,
        isLoading: true,
      };
    case GetFeature.FAILURE:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        feature: initialFeatureState,
      };
    case GetFeature.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        feature: action.payload.feature,
      };
    case GetFeatureCode.REQUEST:
      return {
        ...state,
        featureCode: {
          featureCode: emptyFeatureCode,
          isLoading: true,
          statusCode: null,
        },
      };
    case GetFeatureCode.FAILURE:
      return {
        ...state,
        featureCode: {
          featureCode: emptyFeatureCode,
          isLoading: false,
          statusCode: action.payload.statusCode,
        },
      };
    case GetFeatureCode.SUCCESS:
      return {
        ...state,
        featureCode: {
          featureCode: action.payload.featureCode,
          statusCode: action.payload.statusCode,
          isLoading: false,
        },
      };
    default:
      return state;
  }
}
