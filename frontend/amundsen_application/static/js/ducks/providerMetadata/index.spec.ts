import { testSaga } from 'redux-saga-test-plan';

import {
  ProviderMetadata,
  Tag,
  User,
} from 'interfaces';

import { dashboardSummary } from 'fixtures/metadata/dashboard';
import globalState from 'fixtures/globalState';

import * as API from './api/v0';

import { STATUS_CODES } from '../../constants';

import reducer, {
  getProviderData,
  getProviderDataFailure,
  getProviderDataSuccess,
  getProviderDescription,
  getProviderDescriptionFailure,
  getProviderDescriptionSuccess,
  updateProviderDescription,
  initialProviderDataState,
  initialState,
  ProviderMetadataReducerState,
} from './reducer';

import {
  getProviderDataWatcher,
  getProviderDataWorker,
  getProviderDescriptionWatcher,
  getProviderDescriptionWorker,
  updateProviderDescriptionWatcher,
  updateProviderDescriptionWorker,
} from './sagas';

import {
  GetProviderData,
  GetProviderDescription,
  UpdateProviderDescription,
} from './types';

describe('providerMetadata ducks', () => {
  let expectedData: ProviderMetadata;
  let expectedTags: Tag[];
  let expectedStatus: number;
  let mockSuccess;
  let mockFailure;
  let testKey: string;
  let testIndex: string;
  let testSource: string;
  let columnKey: string;
  let newDescription: string;

  beforeAll(() => {
    expectedData = globalState.providerMetadata.providerData;
    expectedTags = [
      { tag_count: 2, tag_name: 'test' },
      { tag_count: 1, tag_name: 'test2' },
    ];
    expectedStatus = STATUS_CODES.OK;

    mockSuccess = jest.fn().mockImplementation(() => {});
    mockFailure = jest.fn().mockImplementation(() => {});

    testKey = 'providerKey';
    testIndex = '3';
    testSource = 'search';

    newDescription = 'testVal';
  });

  describe('actions', () => {
    it('getProviderData - returns the action to get provider metadata', () => {
      const action = getProviderData(testKey, testIndex, testSource);
      const { payload } = action;

      expect(action.type).toBe(GetProviderData.REQUEST);
      expect(payload.key).toBe(testKey);
      expect(payload.searchIndex).toBe(testIndex);
      expect(payload.source).toBe(testSource);
    });

    it('getProviderDataFailure - returns the action to process failure', () => {
      const action = getProviderDataFailure();
      const { payload } = action;

      expect(action.type).toBe(GetProviderData.FAILURE);
      expect(payload.data).toBe(initialProviderDataState);
      expect(payload.statusCode).toBe(STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(payload.tags).toEqual([]);
    });

    it('getProviderDataSuccess - returns the action to process success', () => {
      const action = getProviderDataSuccess(
        expectedData,
        expectedStatus,
        expectedTags
      );
      const { payload } = action;

      expect(action.type).toBe(GetProviderData.SUCCESS);
      expect(payload.data).toBe(expectedData);
      expect(payload.statusCode).toBe(expectedStatus);
      expect(payload.tags).toEqual(expectedTags);
    });

    it('getProviderDescription - returns the action to get the provider description', () => {
      const action = getProviderDescription(mockSuccess, mockFailure);
      const { payload } = action;

      expect(action.type).toBe(GetProviderDescription.REQUEST);
      expect(payload.onSuccess).toBe(mockSuccess);
      expect(payload.onFailure).toBe(mockFailure);
    });

    it('getProviderDescriptionFailure - returns the action to process failure', () => {
      const action = getProviderDescriptionFailure(expectedData);
      const { payload } = action;

      expect(action.type).toBe(GetProviderDescription.FAILURE);
      expect(payload.providerMetadata).toBe(expectedData);
    });

    it('getProviderDescriptionSuccess - returns the action to process success', () => {
      const action = getProviderDescriptionSuccess(expectedData);
      const { payload } = action;

      expect(action.type).toBe(GetProviderDescription.SUCCESS);
      expect(payload.providerMetadata).toBe(expectedData);
    });

    it('updateProviderDescription - returns the action to update the provider description', () => {
      const action = updateProviderDescription(
        newDescription,
        mockSuccess,
        mockFailure
      );
      const { payload } = action;

      expect(action.type).toBe(UpdateProviderDescription.REQUEST);
      expect(payload.newValue).toBe(newDescription);
      expect(payload.onSuccess).toBe(mockSuccess);
      expect(payload.onFailure).toBe(mockFailure);
    });
  });

  /* TODO: Code involving nested reducers is not covered, will need more investigation */
  describe('reducer', () => {
    let testState: ProviderMetadataReducerState;

    beforeAll(() => {
      testState = initialState;
    });

    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetProviderDashboards.RESPONSE', () => {
      const mockDashboards = [dashboardSummary];
      const mockMessage = 'test';

      expect(
        reducer(
          testState,
          getProviderData(testKey, testIndex, testSource)
        )
      ).toEqual({
        ...testState,
        payload: {
          testKey,
          testIndex,
          testSource,
        },
      });
    });

    it('should handle GetProviderDescription.FAILURE', () => {
      expect(
        reducer(testState, getProviderDescriptionFailure(expectedData))
      ).toEqual({
        ...testState,
        providerData: expectedData,
      });
    });

    it('should handle GetProviderDescription.SUCCESS', () => {
      expect(
        reducer(testState, getProviderDescriptionSuccess(expectedData))
      ).toEqual({
        ...testState,
        providerData: expectedData,
      });
    });
  });

  describe('sagas', () => {
    describe('getProviderDataWatcher', () => {
      it('takes every GetProviderData.REQUEST with getProviderDataWorker', () => {
        testSaga(getProviderDataWatcher)
          .next()
          .takeEvery(GetProviderData.REQUEST, getProviderDataWorker)
          .next()
          .isDone();
      });
    });

    describe('getProviderDataWorker', () => {
      it('executes flow for getting provider data', () => {
        const mockResult = {
          data: expectedData,
          statusCode: expectedStatus,
          tags: expectedTags,
        };
        const mockDashboardsResult = {
          dashboards: [dashboardSummary],
        };

        testSaga(
          getProviderDataWorker,
          getProviderData(testKey, testIndex, testSource)
        )
          .next()
          .call(API.getProviderData, testKey, testIndex, testSource)
          .next(mockResult)
          .put(
            getProviderDataSuccess(
              expectedData,
              expectedStatus,
              expectedTags
            )
          )
          .next()
          .isDone();
      });

      it('handles request error on getProviderData', () => {
        testSaga(getProviderDataWorker, getProviderData(testKey))
          .next()
          .throw(new Error())
          .put(getProviderDataFailure())
          .next()
          .isDone();
      });
    });

    describe('getProviderDescriptionWatcher', () => {
      it('takes every GetProviderDescription.REQUEST with getProviderDescriptionWorker', () => {
        testSaga(getProviderDescriptionWatcher)
          .next()
          .takeEvery(GetProviderDescription.REQUEST, getProviderDescriptionWorker)
          .next()
          .isDone();
      });
    });

    describe('getProviderDescriptionWorker', () => {
      describe('executes flow for getting provider description', () => {
        let sagaTest;

        beforeAll(() => {
          const mockNewProviderData: ProviderMetadata = initialProviderDataState;

          sagaTest = (action) =>
            testSaga(getProviderDescriptionWorker, action)
              .next()
              .select()
              .next(globalState)
              .call(
                API.getProviderDescription,
                globalState.providerMetadata.providerData
              )
              .next(mockNewProviderData)
              .put(getProviderDescriptionSuccess(mockNewProviderData));
        });

        it('without success callback', () => {
          sagaTest(getProviderDescription()).next().isDone();
        });

        it('with success callback', () => {
          sagaTest(getProviderDescription(mockSuccess, mockFailure))
            .next()
            .call(mockSuccess)
            .next()
            .isDone();
        });
      });

      describe('handles request error', () => {
        let sagaTest;

        beforeAll(() => {
          sagaTest = (action) =>
            testSaga(getProviderDescriptionWorker, action)
              .next()
              .select()
              .next(globalState)
              .throw(new Error())
              .put(
                getProviderDescriptionFailure(globalState.providerMetadata.providerData)
              );
        });

        it('without failure callback', () => {
          sagaTest(getProviderDescription()).next().isDone();
        });

        it('with failure callback', () => {
          sagaTest(getProviderDescription(mockSuccess, mockFailure))
            .next()
            .call(mockFailure)
            .next()
            .isDone();
        });
      });
    });

    describe('updateProviderDescriptionWatcher', () => {
      it('takes every UpdateProviderDescription.REQUEST with updateProviderDescriptionWorker', () => {
        testSaga(updateProviderDescriptionWatcher)
          .next()
          .takeEvery(
            UpdateProviderDescription.REQUEST,
            updateProviderDescriptionWorker
          )
          .next()
          .isDone();
      });
    });

    describe('updateProviderDescriptionWorker', () => {
      describe('executes flow for updating provider description', () => {
        let sagaTest;

        beforeAll(() => {
          sagaTest = (mockSuccess) =>
            testSaga(
              updateProviderDescriptionWorker,
              updateProviderDescription(newDescription, mockSuccess, undefined)
            )
              .next()
              .select()
              .next(globalState)
              .call(
                API.updateProviderDescription,
                newDescription,
                globalState.providerMetadata.providerData
              );
        });

        it('without success callback', () => {
          sagaTest().next().isDone();
        });

        it('with success callback', () => {
          sagaTest(mockSuccess).next().call(mockSuccess).next().isDone();
        });
      });

      describe('handles request error', () => {
        let sagaTest;

        beforeAll(() => {
          sagaTest = (mockFailure) =>
            testSaga(
              updateProviderDescriptionWorker,
              updateProviderDescription(newDescription, undefined, mockFailure)
            )
              .next()
              .select()
              .next(globalState)
              .throw(new Error());
        });

        it('without failure callback', () => {
          sagaTest().next().isDone();
        });

        it('with failure callback', () => {
          sagaTest(mockFailure).call(mockFailure).next().isDone();
        });
      });
    });
  });
});
