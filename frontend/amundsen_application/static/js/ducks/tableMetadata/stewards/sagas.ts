import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';

import * as API from '../api/v0';

import {
  updateTableStewardFailure,
  updateTableStewardSuccess,
} from './reducer';

import { UpdateTableSteward, UpdateTableStewardRequest } from '../types';

export function* updateTableStewardWorker(
  action: UpdateTableStewardRequest
): SagaIterator {
  const { payload } = action;
  const state = yield select();
  const { tableData } = state.tableMetadata;
  try {
    const requestList = API.generateStewardUpdateRequests(
      payload.updateArray,
      tableData
    );
    yield all(requestList);
    const newStewards = yield call(API.getTableStewards, tableData.key);
    yield put(updateTableStewardSuccess(newStewards));
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    yield put(
      updateTableStewardFailure(state.tableMetadata.tableStewards.stewards)
    );
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
}
export function* updateTableStewardWatcher(): SagaIterator {
  yield takeEvery(UpdateTableSteward.REQUEST, updateTableStewardWorker);
}
