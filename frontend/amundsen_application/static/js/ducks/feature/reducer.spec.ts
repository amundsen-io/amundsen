import reducer, {
  getFeature,
  getFeatureFailure,
  getFeatureSuccess,
  FeatureReducerState,
  initialFeatureState,
} from 'ducks/feature/reducer';
import { featureMetadata } from '../../fixtures/metadata/feature';

describe('feature reducer', () => {
  let testState: FeatureReducerState;
  beforeEach(() => {
    testState = {
      isLoading: false,
      statusCode: 200,
      feature: initialFeatureState,
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
    });
  });
});
