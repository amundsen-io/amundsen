import {
  GetFeature,
  GetFeatureRequest,
  GetFeatureResponse,
  GetFeaturePayload,
} from 'ducks/feature/types';
import { FeatureMetadata } from 'interfaces/Feature';

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

export function getFeatureSuccess(payload: GetFeaturePayload) {
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

/* Reducer */

export interface FeatureReducerState {
  isLoading: boolean;
  statusCode: number | null;
  feature: FeatureMetadata;
}

export const initialFeatureState: FeatureMetadata = {
  key: '',
  name: '',
  version: '',
  status: '',
  feature_group: '',
  entity: [],
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

export const initialState: FeatureReducerState = {
  isLoading: true,
  statusCode: null,
  feature: initialFeatureState,
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
    default:
      return state;
  }
}
