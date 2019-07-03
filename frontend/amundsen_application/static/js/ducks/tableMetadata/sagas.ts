import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';

import {
  metadataGetLastIndexed,
  metadataGetPreviewData,
  metadataGetTableData,
  metadataGetColumnDescription,
  metadataGetTableDescription,
  metadataUpdateColumnDescription,
  metadataUpdateTableDescription,
} from './api/v0';

import {
  getTableDataFailure, getTableDataSuccess,
  getTableDescriptionFailure, getTableDescriptionSuccess,
  getColumnDescriptionFailure, getColumnDescriptionSuccess,
  getLastIndexedFailure, getLastIndexedSuccess,
  getPreviewDataFailure, getPreviewDataSuccess,
} from './reducer';

import {
  GetLastIndexed, GetLastIndexedRequest,
  GetPreviewData, GetPreviewDataRequest,
  GetTableData, GetTableDataRequest,
  GetColumnDescription, GetColumnDescriptionRequest,
  GetTableDescription, GetTableDescriptionRequest,
  UpdateColumnDescription, UpdateColumnDescriptionRequest,
  UpdateTableDescription, UpdateTableDescriptionRequest,
} from './types';

export function* getTableDataWorker(action: GetTableDataRequest): SagaIterator {
  try {
    const { key, searchIndex, source } = action.payload;
    const { data, owners, statusCode, tags } = yield call(metadataGetTableData, key, searchIndex, source);
    yield put(getTableDataSuccess(data, owners, statusCode, tags));
  } catch (e) {
    yield put(getTableDataFailure());
  }
};
export function* getTableDataWatcher(): SagaIterator {
  yield takeEvery(GetTableData.REQUEST, getTableDataWorker);
};

export function* getTableDescriptionWorker(action: GetTableDescriptionRequest): SagaIterator {
  const { payload } = action;
  const state = yield select();
  let tableData = state.tableMetadata.tableData;
  try {
    tableData = yield call(metadataGetTableDescription, state.tableMetadata.tableData);
    yield put(getTableDescriptionSuccess(tableData));
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    yield put(getTableDescriptionFailure(tableData));
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
};
export function* getTableDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetTableDescription.REQUEST, getTableDescriptionWorker);
};

export function* updateTableDescriptionWorker(action: UpdateTableDescriptionRequest): SagaIterator {
  const { payload } = action;
  const state = yield select();
  try {
    yield call(metadataUpdateTableDescription, payload.newValue, state.tableMetadata.tableData);
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
};
export function* updateTableDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateTableDescription.REQUEST, updateTableDescriptionWorker);
};

export function* getColumnDescriptionWorker(action: GetColumnDescriptionRequest): SagaIterator {
  const { payload } = action;
  const state = yield select();
  let tableData = state.tableMetadata.tableData;
  try {
    tableData = yield call(metadataGetColumnDescription, payload.columnIndex, state.tableMetadata.tableData);
    yield put(getColumnDescriptionSuccess(tableData));
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    yield put(getColumnDescriptionFailure(tableData));
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
};
export function* getColumnDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetColumnDescription.REQUEST, getColumnDescriptionWorker);
};

export function* updateColumnDescriptionWorker(action: UpdateColumnDescriptionRequest): SagaIterator {
  const { payload } = action;
  const state = yield select();
  try {
    yield call(metadataUpdateColumnDescription, payload.newValue, payload.columnIndex, state.tableMetadata.tableData);
    if (payload.onSuccess) {
      yield call(payload.onSuccess);
    }
  } catch (e) {
    if (payload.onFailure) {
      yield call(payload.onFailure);
    }
  }
};
export function* updateColumnDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateColumnDescription.REQUEST, updateColumnDescriptionWorker);
};

export function* getLastIndexedWorker(action: GetLastIndexedRequest): SagaIterator {
  try {
    const lastIndexed = yield call(metadataGetLastIndexed);
    yield put(getLastIndexedSuccess(lastIndexed));
  } catch (e) {
    yield put(getLastIndexedFailure());
  }
};
export function* getLastIndexedWatcher(): SagaIterator {
  yield takeEvery(GetLastIndexed.REQUEST, getLastIndexedWorker)
};

export function* getPreviewDataWorker(action: GetPreviewDataRequest): SagaIterator {
  try {
    const response = yield call(metadataGetPreviewData, action.payload.queryParams);
    const { data, status } = response;
    yield put(getPreviewDataSuccess(data, status));
  } catch (e) {
    const data = e.response ? e.response.data : {};
    const status = e.response ? e.response.status : null;
    yield put(getPreviewDataFailure(data, status));
  }
};
export function* getPreviewDataWatcher(): SagaIterator {
  yield takeEvery(GetPreviewData.REQUEST, getPreviewDataWorker);
};
