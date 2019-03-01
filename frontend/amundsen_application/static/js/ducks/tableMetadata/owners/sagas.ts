import { all, call, put, select, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import { UpdateTableOwner, UpdateTableOwnerRequest } from './reducer';

import { metadataUpdateTableOwner, metadataTableOwners } from '../api/v0';

// updateTableOwner
export function* updateTableOwnerWorker(action: UpdateTableOwnerRequest): SagaIterator {
  const state = yield select();
  const tableData = state.tableMetadata.tableData;
  try {
    yield all(metadataUpdateTableOwner(action, tableData));
    const newOwners = yield call(metadataTableOwners, tableData);
    yield put({ type: UpdateTableOwner.SUCCESS, payload: newOwners });
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    yield put({ type: UpdateTableOwner.FAILURE, payload: state.tableMetadata.tableOwners.owners });
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
}

export function* updateTableOwnerWatcher(): SagaIterator {
  yield takeEvery(UpdateTableOwner.ACTION, updateTableOwnerWorker);
}
