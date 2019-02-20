import { all, call, put, select, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import {
  GetLastIndexedRequest, GetLastIndexed,
  GetPreviewData, GetPreviewDataRequest,
  GetTableData, GetTableDataRequest,
  GetColumnDescription, GetColumnDescriptionRequest,
  GetTableDescription, GetTableDescriptionRequest,
  UpdateColumnDescription, UpdateColumnDescriptionRequest,
  UpdateTableDescription, UpdateTableDescriptionRequest,
  UpdateTableOwner, UpdateTableOwnerRequest,
  UpdateTags, UpdateTagsRequest,
} from './reducer';

import {
  metadataGetLastIndexed,
  metadataGetPreviewData,
  metadataGetTableData,
  metadataGetColumnDescription,
  metadataGetTableDescription,
  metadataUpdateColumnDescription,
  metadataUpdateTableDescription,
  metadataUpdateTableOwner,
  metadataUpdateTableTags,
  metadataTableTags,
} from '../api/metadata/v0';

// getTableData
export function* getTableDataWorker(action: GetTableDataRequest): SagaIterator {
  let tableData;
  try {
    tableData = yield call(metadataGetTableData, action);
    yield put({ type: GetTableData.SUCCESS, payload: tableData });
  } catch (e) {
    yield put({ type: GetTableData.FAILURE, payload: tableData });
  }
}

export function* getTableDataWatcher(): SagaIterator {
  yield takeEvery(GetTableData.ACTION, getTableDataWorker);
}

// getTableDescription
export function* getTableDescriptionWorker(action: GetTableDescriptionRequest): SagaIterator {
  const state = yield select();
  let tableData;
  try {
    tableData = yield call(metadataGetTableDescription, state.tableMetadata.tableData);
    yield put({ type: GetTableDescription.SUCCESS, payload: tableData });
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    yield put({ type: GetTableDescription.FAILURE, payload: tableData });
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
}

export function* getTableDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetTableDescription.ACTION, getTableDescriptionWorker);
}

// updateTableDescription
export function* updateTableDescriptionWorker(action: UpdateTableDescriptionRequest): SagaIterator {
  const state = yield select();
  try {
    yield call(metadataUpdateTableDescription, action.newValue, state.tableMetadata.tableData);
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
}

export function* updateTableDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateTableDescription.ACTION, updateTableDescriptionWorker);
}

// updateTableOwner
export function* updateTableOwnerWorker(action: UpdateTableOwnerRequest): SagaIterator {
  const state = yield select();
  try {
    yield call(metadataUpdateTableOwner, action.value, action.method, state.tableMetadata.tableData);
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
}

export function* updateTableOwnerWatcher(): SagaIterator {
  yield takeEvery(UpdateTableOwner.ACTION, updateTableOwnerWorker);
}

// getColumnDescription
export function* getColumnDescriptionWorker(action: GetColumnDescriptionRequest): SagaIterator {
  const state = yield select();
  let tableData;
  try {
    tableData = yield call(metadataGetColumnDescription, action.columnIndex, state.tableMetadata.tableData);
    yield put({ type: GetColumnDescription.SUCCESS, payload: tableData });
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    yield put({ type: GetColumnDescription.FAILURE, payload: tableData });
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
}

export function* getColumnDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetColumnDescription.ACTION, getColumnDescriptionWorker);
}

// updateColumnDescription
export function* updateColumnDescriptionWorker(action: UpdateColumnDescriptionRequest): SagaIterator {
  const state = yield select();
  try {
    yield call(metadataUpdateColumnDescription, action.newValue, action.columnIndex, state.tableMetadata.tableData);
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
}

export function* updateColumnDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateColumnDescription.ACTION, updateColumnDescriptionWorker);
}

// updateTags
export function* updateTagsWorker(action: UpdateTagsRequest): SagaIterator {
  const state = yield select();
  const tableData = state.tableMetadata.tableData;
  try {
    yield all(metadataUpdateTableTags(action, tableData));
    const newTableData = yield call(metadataTableTags, tableData);
    console.log(newTableData);
    yield put({ type: UpdateTags.SUCCESS, payload: newTableData });
  } catch (e) {
    yield put({ type: UpdateTags.FAILURE, payload: tableData });
  }
}

export function* updateTagsWatcher(): SagaIterator {
  yield takeEvery(UpdateTags.ACTION, updateTagsWorker);
}

// getLastIndexed
export function* getLastIndexedWorker(action: GetLastIndexedRequest): SagaIterator {
  try {
    const lastIndexed = yield call(metadataGetLastIndexed);
    yield put({ type: GetLastIndexed.SUCCESS, payload: lastIndexed });
  } catch (e) {
    yield put({ type: GetLastIndexed.FAILURE });
  }
}

export function* getLastIndexedWatcher(): SagaIterator {
  yield takeEvery(GetLastIndexed.ACTION, getLastIndexedWorker)
}

// getPreviewData
export function* getPreviewDataWorker(action: GetPreviewDataRequest): SagaIterator {
  let response;
  try {
    response = yield call(metadataGetPreviewData, action);
    yield put({ type: GetPreviewData.SUCCESS, payload: response });
  } catch (e) {
    yield put({ type: GetPreviewData.FAILURE, payload: response });
  }
}

export function* getPreviewDataWatcher(): SagaIterator {
  yield takeEvery(GetPreviewData.ACTION, getPreviewDataWorker);
}
