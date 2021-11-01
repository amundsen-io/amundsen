import { testSaga } from 'redux-saga-test-plan';

import {
  OwnerDict,
  StewardDict,
  UpdateMethod,
  UpdateStewardPayload,
} from 'interfaces';

import globalState from 'fixtures/globalState';

import * as API from '../api/v0';

import reducer, {
  updateTableSteward,
  updateTableStewardFailure,
  updateTableStewardSuccess,
  initialStewardsState,
  TableStewardReducerState,
} from './reducer';
import {
  getTableData,
  getTableDataFailure,
  getTableDataSuccess,
} from '../reducer';

import { updateTableStewardWorker, updateTableStewardWatcher } from './sagas';

import { UpdateTableSteward } from '../types';

jest.spyOn(API, 'generateStewardUpdateRequests').mockImplementation(() => []);

describe('tableMetadata:stewards ducks', () => {
  let expectedOwners: OwnerDict;
  let expectedStewards: StewardDict;
  let updatePayload: UpdateStewardPayload[];
  let mockSuccess;
  let mockFailure;
  beforeAll(() => {
    expectedStewards = {
      testId: {
        display_name: 'test',
        profile_url: 'test.io',
        email: 'test@test.com',
        user_id: 'testId',
      },
    };
    updatePayload = [{ method: UpdateMethod.PUT, id: 'testId' }];
    mockSuccess = jest.fn();
    mockFailure = jest.fn();
  });

  describe('actions', () => {
    it('updateTableSteward - returns the action to update table stewards', () => {
      const action = updateTableSteward(
        updatePayload,
        mockSuccess,
        mockFailure
      );
      const { payload } = action;
      expect(action.type).toBe(UpdateTableSteward.REQUEST);
      expect(payload.updateArray).toBe(updatePayload);
      expect(payload.onSuccess).toBe(mockSuccess);
      expect(payload.onFailure).toBe(mockFailure);
    });

    it('updateTableStewardFailure - returns the action to process failure', () => {
      const action = updateTableStewardFailure(expectedStewards);
      const { payload } = action;
      expect(action.type).toBe(UpdateTableSteward.FAILURE);
      expect(payload.stewards).toBe(expectedStewards);
    });

    it('updateTableStewardSuccess - returns the action to process success', () => {
      const action = updateTableStewardSuccess(expectedStewards);
      const { payload } = action;
      expect(action.type).toBe(UpdateTableSteward.SUCCESS);
      expect(payload.stewards).toBe(expectedStewards);
    });
  });

  describe('reducer', () => {
    let testState: TableStewardReducerState;
    beforeAll(() => {
      testState = initialStewardsState;
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle UpdateTableSteward.REQUEST', () => {
      expect(
        reducer(
          testState,
          updateTableSteward(updatePayload, mockSuccess, mockFailure)
        )
      ).toEqual({
        ...testState,
        isLoading: true,
      });
    });

    it('should handle UpdateTableSteward.FAILURE', () => {
      expect(
        reducer(testState, updateTableStewardFailure(expectedStewards))
      ).toEqual({
        ...testState,
        isLoading: false,
        stewards: expectedStewards,
      });
    });

    it('should handle UpdateTableSteward.SUCCESS', () => {
      expect(
        reducer(testState, updateTableStewardSuccess(expectedStewards))
      ).toEqual({
        ...testState,
        isLoading: false,
        stewards: expectedStewards,
      });
    });

    it('should handle GetTableData.REQUEST', () => {
      expect(reducer(testState, getTableData('testKey'))).toEqual({
        ...testState,
        isLoading: true,
        stewards: {},
      });
    });

    it('should handle GetTableData.FAILURE', () => {
      const action = getTableDataFailure();
      expect(reducer(testState, action)).toEqual({
        ...testState,
        isLoading: false,
        stewards: action.payload.stewards,
      });
    });

    it('should handle GetTableData.SUCCESS', () => {
      const mockTableData = globalState.tableMetadata.tableData;
      expect(
        reducer(
          testState,
          getTableDataSuccess(
            mockTableData,
            expectedOwners,
            expectedStewards,
            200,
            []
          )
        )
      ).toEqual({
        ...testState,
        isLoading: false,
        stewards: expectedStewards,
      });
    });
  });

  describe('sagas', () => {
    describe('updateTableStewardWatcher', () => {
      it('takes every UpdateTableSteward.REQUEST with updateTableStewardWorker', () => {
        testSaga(updateTableStewardWatcher)
          .next()
          .takeEvery(UpdateTableSteward.REQUEST, updateTableStewardWorker);
      });
    });

    describe('updateTableStewardWorker', () => {
      describe('executes flow for updating stewards and returning up to date steward dict', () => {
        let sagaTest;
        beforeAll(() => {
          sagaTest = (action) =>
            testSaga(updateTableStewardWorker, action)
              .next()
              .select()
              .next(globalState)
              .all(
                API.generateStewardUpdateRequests(
                  updatePayload,
                  globalState.tableMetadata.tableData
                )
              )
              .next()
              .call(
                API.getTableStewards,
                globalState.tableMetadata.tableData.key
              )
              .next(expectedStewards)
              .put(updateTableStewardSuccess(expectedStewards));
        });
        it('without success callback', () => {
          sagaTest(updateTableSteward(updatePayload)).next().isDone();
        });

        it('with success callback', () => {
          sagaTest(updateTableSteward(updatePayload, mockSuccess, mockFailure))
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
            testSaga(updateTableStewardWorker, action)
              .next()
              .select()
              .next(globalState)
              .throw(new Error())
              .put(
                updateTableStewardFailure(
                  globalState.tableMetadata.tableStewards.stewards
                )
              );
        });
        it('without failure callback', () => {
          sagaTest(updateTableSteward(updatePayload)).next().isDone();
        });

        it('with failure callback', () => {
          sagaTest(updateTableSteward(updatePayload, mockSuccess, mockFailure))
            .next()
            .call(mockFailure)
            .next()
            .isDone();
        });
      });
    });
  });
});
