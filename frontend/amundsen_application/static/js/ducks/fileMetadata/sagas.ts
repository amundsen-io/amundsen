import { SagaIterator } from 'redux-saga';
import { call, put, select, takeEvery, takeLatest } from 'redux-saga/effects';

import * as API from './api/v0';

import {
  getFileDataFailure,
  getFileDataSuccess,
  getFileDescriptionFailure,
  getFileDescriptionSuccess,
} from './reducer';

import {
  GetFileData,
  GetFileDataRequest,
  GetFileDescription,
  GetFileDescriptionRequest,
  UpdateFileDescription,
  UpdateFileDescriptionRequest,
} from './types';

export function* getFileDataWorker(action: GetFileDataRequest): SagaIterator {
  const { key, searchIndex, source } = action.payload;

  try {
    const { data, statusCode, tags } = yield call(
      API.getFileData,
      key,
      searchIndex,
      source
    );

    yield put(getFileDataSuccess(data, statusCode, tags));

  } catch (e) {
    yield put(getFileDataFailure());
  }
}
export function* getFileDataWatcher(): SagaIterator {
  yield takeEvery(GetFileData.REQUEST, getFileDataWorker);
}

export function* getFileDescriptionWorker(
  action: GetFileDescriptionRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();
  let { fileData } = state.fileMetadata;

  try {
    // TODO - Cleanup this pattern of sending in the file metadata and then modifying it and sending it back.
    // Should just fetch the description and send it back to the reducer.
    fileData = yield call(
      API.getFileDescription,
      state.fileMetadata.fileData
    );
    yield put(getFileDescriptionSuccess(fileData));
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    yield put(getFileDescriptionFailure(fileData));
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
}
export function* getFileDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetFileDescription.REQUEST, getFileDescriptionWorker);
}

export function* updateFileDescriptionWorker(
  action: UpdateFileDescriptionRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();

  try {
    yield call(
      API.updateFileDescription,
      payload.newValue,
      state.fileMetadata.fileData
    );
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
}
export function* updateFileDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateFileDescription.REQUEST, updateFileDescriptionWorker);
}
