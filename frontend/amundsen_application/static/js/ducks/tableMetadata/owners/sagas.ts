import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';

import { UpdateTableOwner, UpdateTableOwnerRequest } from '../types';

import { metadataUpdateTableOwner, metadataTableOwners } from '../api/v0';

export function* updateTableOwnerWorker(action: UpdateTableOwnerRequest): SagaIterator {
  const state = yield select();
  const tableData = state.tableMetadata.tableData;
  try {
    /* TODO: Pass explicit params into api method and not action */
    yield all(metadataUpdateTableOwner(action, tableData));
    const newOwners = yield call(metadataTableOwners, tableData);
    yield put({ type: UpdateTableOwner.SUCCESS, payload: { owners: newOwners } });
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    yield put({ type: UpdateTableOwner.FAILURE, payload: { owners: state.tableMetadata.tableOwners.owners } });
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
};
export function* updateTableOwnerWatcher(): SagaIterator {
  yield takeEvery(UpdateTableOwner.REQUEST, updateTableOwnerWorker);
};
