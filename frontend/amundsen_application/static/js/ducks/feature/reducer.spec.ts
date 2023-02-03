// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import reducer, {
  getFeature,
  getFeatureFailure,
  getFeatureSuccess,
  FeatureReducerState,
  initialFeatureState,
  initialFeatureCodeState,
  initialPreviewState,
  emptyFeatureCode,
  getFeatureCode,
  getFeatureCodeSuccess,
  getFeatureCodeFailure,
  getFeatureDescriptionSuccess,
  updateFeatureDescriptionSuccess,
  updateFeatureDescriptionFailure,
  initialFeatureLineageState,
  getFeaturePreviewDataSuccess,
  getFeaturePreviewDataFailure,
  getFeaturePreviewData,
} from 'ducks/feature/reducer';
import { featureMetadata } from 'fixtures/metadata/feature';

import { STATUS_CODES } from '../../constants';

describe('feature reducer', () => {
  let testState: FeatureReducerState;

  beforeEach(() => {
    testState = {
      isLoading: false,
      isLoadingOwners: false,
      statusCode: STATUS_CODES.OK,
      feature: initialFeatureState,
      featureCode: initialFeatureCodeState,
      featureLineage: initialFeatureLineageState,
      preview: initialPreviewState,
    };
  });

  it('should return the existing state if action is not handled', () => {
    expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
  });

  it('should handle getFeature.REQUEST', () => {
    expect(reducer(testState, getFeature('testKey'))).toEqual({
      ...testState,
      isLoading: true,
      statusCode: null,
    });
  });

  it('should handle GetFeature.SUCCESS', () => {
    expect(
      reducer(
        testState,
        getFeatureSuccess({
          feature: featureMetadata,
          statusCode: STATUS_CODES.ACCEPTED,
        })
      )
    ).toEqual({
      ...testState,
      isLoading: false,
      statusCode: STATUS_CODES.ACCEPTED,
      feature: featureMetadata,
      featureCode: initialFeatureCodeState,
    });
  });

  it('should handle GetFeature.FAILURE', () => {
    expect(
      reducer(
        testState,
        getFeatureFailure({
          statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
        })
      )
    ).toEqual({
      ...testState,
      isLoading: false,
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
      feature: initialFeatureState,
      featureCode: initialFeatureCodeState,
    });
  });

  it('should handle getFeatureCode.REQUEST', () => {
    expect(reducer(testState, getFeatureCode('testKey'))).toEqual({
      ...testState,
      featureCode: {
        isLoading: true,
        statusCode: null,
        featureCode: emptyFeatureCode,
      },
    });
  });

  it('should handle GetFeatureCode.SUCCESS', () => {
    const response = {
      featureCode: {
        key: 'testKey',
        source: 'testSource',
        text: 'testText',
      },
      statusCode: STATUS_CODES.ACCEPTED,
    };

    expect(reducer(testState, getFeatureCodeSuccess(response))).toEqual({
      ...testState,
      featureCode: {
        featureCode: response.featureCode,
        statusCode: response.statusCode,
        isLoading: false,
      },
    });
  });

  it('should handle GetFeatureCode.FAILURE', () => {
    expect(
      reducer(
        testState,
        getFeatureCodeFailure({
          statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
        })
      )
    ).toEqual({
      ...testState,
      featureCode: {
        featureCode: emptyFeatureCode,
        statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
        isLoading: false,
      },
    });
  });

  it('should handle GetFeaturePreviewData.REQUEST', () => {
    const request = {
      feature_name: 'name',
      feature_group: 'group',
      version: '3',
    };

    expect(reducer(testState, getFeaturePreviewData(request))).toEqual({
      ...testState,
      preview: {
        isLoading: true,
        previewData: {},
        status: null,
      },
    });
  });

  it('should handle GetFeaturePreviewData.SUCCESS', () => {
    const response = {
      previewData: {
        columns: [],
        data: [],
        error_text: '',
      },
      status: STATUS_CODES.ACCEPTED,
    };

    expect(reducer(testState, getFeaturePreviewDataSuccess(response))).toEqual({
      ...testState,
      preview: {
        isLoading: false,
        previewData: response.previewData,
        status: response.status,
      },
    });
  });

  it('should handle GetFeaturePreviewData.FAILURE', () => {
    const response = {
      previewData: {
        error_text: 'error message',
      },
      status: STATUS_CODES.BAD_GATEWAY,
    };

    expect(reducer(testState, getFeaturePreviewDataFailure(response))).toEqual({
      ...testState,
      preview: {
        isLoading: false,
        previewData: response.previewData,
        status: response.status,
      },
    });
  });

  it('should handle GetFeatureDescription.SUCCESS', () => {
    const response = {
      description: 'testDescription',
      statusCode: STATUS_CODES.OK,
    };

    expect(reducer(testState, getFeatureDescriptionSuccess(response))).toEqual({
      ...testState,
      feature: {
        ...testState.feature,
        description: response.description,
      },
    });
  });

  it('should handle GetFeatureDescription.FAILURE', () => {
    const response = {
      description: 'testDescription',
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
    };

    expect(reducer(testState, getFeatureDescriptionSuccess(response))).toEqual({
      ...testState,
      feature: {
        ...testState.feature,
        description: response.description,
      },
    });
  });

  it('should handle UpdateFeatureDescription.SUCCESS', () => {
    const response = {
      description: 'testDescription',
      statusCode: STATUS_CODES.OK,
    };

    expect(
      reducer(testState, updateFeatureDescriptionSuccess(response))
    ).toEqual({
      ...testState,
      feature: {
        ...testState.feature,
        description: response.description,
      },
    });
  });

  it('should handle UpdateFeatureDescription.FAILURE', () => {
    const response = {
      description: 'testDescription',
      statusCode: STATUS_CODES.OK,
    };

    expect(
      reducer(testState, updateFeatureDescriptionFailure(response))
    ).toEqual({
      ...testState,
      feature: {
        ...testState.feature,
        description: response.description,
      },
    });
  });
});
