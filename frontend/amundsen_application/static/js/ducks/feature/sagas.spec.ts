import { testSaga } from 'redux-saga-test-plan';

import { featureMetadata } from 'fixtures/metadata/feature';
import * as API from './api/v0';
import * as Sagas from './sagas';

import { getFeature, getFeatureFailure, getFeatureSuccess } from './reducer';
import { GetFeature } from './types';

describe('feature sagas', () => {
  describe('getFeatureWatcher', () => {
    it('takes every GetFeature.REQUEST with getFeatureWorker', () => {
      testSaga(Sagas.getFeatureWatcher)
        .next()
        .takeEvery(GetFeature.REQUEST, Sagas.getFeatureWorker)
        .next()
        .isDone();
    });
  });

  describe('getFeatureWorker', () => {
    it('executes flow for successfully getting a feature', () => {
      const mockResponse = {
        feature: featureMetadata,
        statusCode: 200,
      };
      testSaga(Sagas.getFeatureWorker, getFeature('testUri', '0', 'source'))
        .next()
        .call(API.getFeature, 'testUri', '0', 'source')
        .next(mockResponse)
        .put(getFeatureSuccess(mockResponse))
        .next()
        .isDone();
    });

    it('executes flow for a failed request feature', () => {
      const mockResponse = {
        statusCode: 200,
        statusMessage: 'oops',
      };
      testSaga(Sagas.getFeatureWorker, getFeature('testUri', '0', 'source'))
        .next()
        .call(API.getFeature, 'testUri', '0', 'source')
        // @ts-ignore
        .throw(mockResponse)
        .put(getFeatureFailure(mockResponse))
        .next()
        .isDone();
    });
  });
});
