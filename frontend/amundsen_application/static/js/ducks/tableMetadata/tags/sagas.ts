import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';

import * as API from '../api/v0';

import { updateTagsFailure, updateTagsSuccess } from './reducer';

import { UpdateTags, UpdateTagsRequest } from '../types';

export function* updateTableTagsWorker(action: UpdateTagsRequest): SagaIterator {
  const state = yield select();
  const tableData = state.tableMetadata.tableData;
  try {
    yield all(API.updateTableTags(action.payload.tagArray, tableData.key));
    const newTags = yield call(API.getTableTags, tableData.key);
    yield put(updateTagsSuccess(newTags));
  } catch (e) {
    yield put(updateTagsFailure());
  }
};
export function* updateTableTagsWatcher(): SagaIterator {
  yield takeEvery(UpdateTags.REQUEST, updateTableTagsWorker);
};
