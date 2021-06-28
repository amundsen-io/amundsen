// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import reducer, {
  getFeature,
  getFeatureFailure,
  getFeatureSuccess,
  FeatureReducerState,
  initialFeatureState,
  initialFeatureCodeState,
  emptyFeatureCode,
  getFeatureCode,
  getFeatureCodeSuccess,
  getFeatureCodeFailure,
} from 'ducks/feature/reducer';
import { featureMetadata } from '../../fixtures/metadata/feature';

describe('feature reducer', () => {
  let testState: FeatureReducerState;
  beforeEach(() => {
    testState = {
      isLoading: false,
      statusCode: null,
      feature: initialFeatureState,
      featureCode: initialFeatureCodeState,
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
          statusCode: 202,
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: 202,
      feature: featureMetadata,
      featureCode: initialFeatureCodeState,
    });
  });

  it('should handle GetFeature.FAILURE', () => {
    expect(
      reducer(
        testState,
        getFeatureFailure({
          statusCode: 500,
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: 500,
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
      statusCode: 202,
    };

    expect(reducer(testState, getFeatureCodeSuccess(response))).toEqual({
      isLoading: false,
      statusCode: null,
      feature: initialFeatureState,
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
          statusCode: 500,
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: null,
      feature: initialFeatureState,
      featureCode: {
        featureCode: emptyFeatureCode,
        statusCode: 500,
        isLoading: false,
      },
    });
  });
});
