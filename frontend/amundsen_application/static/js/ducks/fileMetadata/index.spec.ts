import { testSaga } from 'redux-saga-test-plan';

import {
  FileMetadata,
  Tag,
  User,
} from 'interfaces';

import globalState from 'fixtures/globalState';

import * as API from './api/v0';

import { STATUS_CODES } from '../../constants';

import reducer, {
  getFileData,
  getFileDataFailure,
  getFileDataSuccess,
  getFileDescription,
  getFileDescriptionFailure,
  getFileDescriptionSuccess,
  updateFileDescription,
  initialFileDataState,
  initialState,
  FileMetadataReducerState,
} from './reducer';

import {
  getFileDataWatcher,
  getFileDataWorker,
  getFileDescriptionWatcher,
  getFileDescriptionWorker,
  updateFileDescriptionWatcher,
  updateFileDescriptionWorker,
} from './sagas';

import {
  GetFileData,
  GetFileDescription,
  UpdateFileDescription,
} from './types';

describe('fileMetadata ducks', () => {
  let expectedData: FileMetadata;
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
    expectedData = globalState.fileMetadata.fileData;
    expectedTags = [
      { tag_count: 2, tag_name: 'test' },
      { tag_count: 1, tag_name: 'test2' },
    ];
    expectedStatus = STATUS_CODES.OK;

    mockSuccess = jest.fn().mockImplementation(() => {});
    mockFailure = jest.fn().mockImplementation(() => {});

    testKey = 'fileKey';
    testIndex = '3';
    testSource = 'search';

    newDescription = 'testVal';
  });

  describe('actions', () => {
    it('getFileData - returns the action to get file metadata', () => {
      const action = getFileData(testKey, testIndex, testSource);
      const { payload } = action;

      expect(action.type).toBe(GetFileData.REQUEST);
      expect(payload.key).toBe(testKey);
      expect(payload.searchIndex).toBe(testIndex);
      expect(payload.source).toBe(testSource);
    });

    it('getFileDataFailure - returns the action to process failure', () => {
      const action = getFileDataFailure();
      const { payload } = action;

      expect(action.type).toBe(GetFileData.FAILURE);
      expect(payload.data).toBe(initialFileDataState);
      expect(payload.statusCode).toBe(STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(payload.tags).toEqual([]);
    });

    it('getFileDataSuccess - returns the action to process success', () => {
      const action = getFileDataSuccess(
        expectedData,
        expectedStatus,
        expectedTags
      );
      const { payload } = action;

      expect(action.type).toBe(GetFileData.SUCCESS);
      expect(payload.data).toBe(expectedData);
      expect(payload.statusCode).toBe(expectedStatus);
      expect(payload.tags).toEqual(expectedTags);
    });

    it('getFileDescription - returns the action to get the file description', () => {
      const action = getFileDescription(mockSuccess, mockFailure);
      const { payload } = action;

      expect(action.type).toBe(GetFileDescription.REQUEST);
      expect(payload.onSuccess).toBe(mockSuccess);
      expect(payload.onFailure).toBe(mockFailure);
    });

    it('getFileDescriptionFailure - returns the action to process failure', () => {
      const action = getFileDescriptionFailure(expectedData);
      const { payload } = action;

      expect(action.type).toBe(GetFileDescription.FAILURE);
      expect(payload.fileMetadata).toBe(expectedData);
    });

    it('getFileDescriptionSuccess - returns the action to process success', () => {
      const action = getFileDescriptionSuccess(expectedData);
      const { payload } = action;

      expect(action.type).toBe(GetFileDescription.SUCCESS);
      expect(payload.fileMetadata).toBe(expectedData);
    });

    it('updateFileDescription - returns the action to update the file description', () => {
      const action = updateFileDescription(
        newDescription,
        mockSuccess,
        mockFailure
      );
      const { payload } = action;

      expect(action.type).toBe(UpdateFileDescription.REQUEST);
      expect(payload.newValue).toBe(newDescription);
      expect(payload.onSuccess).toBe(mockSuccess);
      expect(payload.onFailure).toBe(mockFailure);
    });
  });

  /* TODO: Code involving nested reducers is not covered, will need more investigation */
  describe('reducer', () => {
    let testState: FileMetadataReducerState;

    beforeAll(() => {
      testState = initialState;
    });

    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetFileDescription.FAILURE', () => {
      expect(
        reducer(testState, getFileDescriptionFailure(expectedData))
      ).toEqual({
        ...testState,
        fileData: expectedData,
      });
    });

    it('should handle GetFileDescription.SUCCESS', () => {
      expect(
        reducer(testState, getFileDescriptionSuccess(expectedData))
      ).toEqual({
        ...testState,
        fileData: expectedData,
      });
    });
  });

  describe('sagas', () => {
    describe('getFileDataWatcher', () => {
      it('takes every GetFileData.REQUEST with getFileDataWorker', () => {
        testSaga(getFileDataWatcher)
          .next()
          .takeEvery(GetFileData.REQUEST, getFileDataWorker)
          .next()
          .isDone();
      });
    });

    describe('getFileDataWorker', () => {
      it('executes flow for getting file data', () => {
        const mockResult = {
          data: expectedData,
          statusCode: expectedStatus,
          tags: expectedTags,
        };

        testSaga(
          getFileDataWorker,
          getFileData(testKey, testIndex, testSource)
        )
          .next()
          .call(API.getFileData, testKey, testIndex, testSource)
          .next(mockResult)
          .put(
            getFileDataSuccess(
              expectedData,
              expectedStatus,
              expectedTags
            )
          )
          .next()
          .isDone();
      });

      it('handles request error on getFileData', () => {
        testSaga(getFileDataWorker, getFileData(testKey))
          .next()
          .throw(new Error())
          .put(getFileDataFailure())
          .next()
          .isDone();
      });
    });

    describe('getFileDescriptionWatcher', () => {
      it('takes every GetFileDescription.REQUEST with getFileDescriptionWorker', () => {
        testSaga(getFileDescriptionWatcher)
          .next()
          .takeEvery(GetFileDescription.REQUEST, getFileDescriptionWorker)
          .next()
          .isDone();
      });
    });

    describe('getFileDescriptionWorker', () => {
      describe('executes flow for getting file description', () => {
        let sagaTest;

        beforeAll(() => {
          const mockNewFileData: FileMetadata = initialFileDataState;

          sagaTest = (action) =>
            testSaga(getFileDescriptionWorker, action)
              .next()
              .select()
              .next(globalState)
              .call(
                API.getFileDescription,
                globalState.fileMetadata.fileData
              )
              .next(mockNewFileData)
              .put(getFileDescriptionSuccess(mockNewFileData));
        });

        it('without success callback', () => {
          sagaTest(getFileDescription()).next().isDone();
        });

        it('with success callback', () => {
          sagaTest(getFileDescription(mockSuccess, mockFailure))
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
            testSaga(getFileDescriptionWorker, action)
              .next()
              .select()
              .next(globalState)
              .throw(new Error())
              .put(
                getFileDescriptionFailure(globalState.fileMetadata.fileData)
              );
        });

        it('without failure callback', () => {
          sagaTest(getFileDescription()).next().isDone();
        });

        it('with failure callback', () => {
          sagaTest(getFileDescription(mockSuccess, mockFailure))
            .next()
            .call(mockFailure)
            .next()
            .isDone();
        });
      });
    });

    describe('updateFileDescriptionWatcher', () => {
      it('takes every UpdateFileDescription.REQUEST with updateFileDescriptionWorker', () => {
        testSaga(updateFileDescriptionWatcher)
          .next()
          .takeEvery(
            UpdateFileDescription.REQUEST,
            updateFileDescriptionWorker
          )
          .next()
          .isDone();
      });
    });

    describe('updateFileDescriptionWorker', () => {
      describe('executes flow for updating file description', () => {
        let sagaTest;

        beforeAll(() => {
          sagaTest = (mockSuccess) =>
            testSaga(
              updateFileDescriptionWorker,
              updateFileDescription(newDescription, mockSuccess, undefined)
            )
              .next()
              .select()
              .next(globalState)
              .call(
                API.updateFileDescription,
                newDescription,
                globalState.fileMetadata.fileData
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
              updateFileDescriptionWorker,
              updateFileDescription(newDescription, undefined, mockFailure)
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
