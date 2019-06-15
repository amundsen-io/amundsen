import { SagaIterator } from 'redux-saga';
import { all, call, put, select, takeEvery } from 'redux-saga/effects';

import {
  GetLastIndexed, GetLastIndexedRequest,
  GetPreviewData, GetPreviewDataRequest,
  GetTableData, GetTableDataRequest,
  GetColumnDescription, GetColumnDescriptionRequest,
  GetTableDescription, GetTableDescriptionRequest,
  UpdateColumnDescription, UpdateColumnDescriptionRequest,
  UpdateTableDescription, UpdateTableDescriptionRequest,
} from './types';

import {
  metadataGetLastIndexed,
  metadataGetPreviewData,
  metadataGetTableData,
  metadataGetColumnDescription,
  metadataGetTableDescription,
  metadataUpdateColumnDescription,
  metadataUpdateTableDescription,
} from './api/v0';

export function* getTableDataWorker(action: GetTableDataRequest): SagaIterator {
  try {
    /* TODO: Pass explicit params into api method and not action */
    const { data, owners, statusCode, tags } = yield call(metadataGetTableData, action);
    yield put({ type: GetTableData.SUCCESS, payload: { data, owners, statusCode, tags } });
  } catch (e) {
    yield put({ type: GetTableData.FAILURE, payload: { data: {}, owners: [], statusCode: 500, tags: [] } });
  }
};
export function* getTableDataWatcher(): SagaIterator {
  yield takeEvery(GetTableData.REQUEST, getTableDataWorker);
};

export function* getTableDescriptionWorker(action: GetTableDescriptionRequest): SagaIterator {
  const state = yield select();
  let tableData;
  try {
    tableData = yield call(metadataGetTableDescription, state.tableMetadata.tableData);
    yield put({ type: GetTableDescription.SUCCESS, payload: { tableMetadata: tableData } });
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    yield put({ type: GetTableDescription.FAILURE, payload: { tableMetadata: tableData } });
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
};
export function* getTableDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetTableDescription.REQUEST, getTableDescriptionWorker);
};

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
};
export function* updateTableDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateTableDescription.REQUEST, updateTableDescriptionWorker);
};

export function* getColumnDescriptionWorker(action: GetColumnDescriptionRequest): SagaIterator {
  const state = yield select();
  let tableData;
  try {
    tableData = yield call(metadataGetColumnDescription, action.columnIndex, state.tableMetadata.tableData);
    yield put({ type: GetColumnDescription.SUCCESS, payload: { tableMetadata: tableData } });
    if (action.onSuccess) {
      yield call(action.onSuccess);
    }
  } catch (e) {
    yield put({ type: GetColumnDescription.FAILURE, payload: { tableMetadata: tableData } });
    if (action.onFailure) {
      yield call(action.onFailure);
    }
  }
};
export function* getColumnDescriptionWatcher(): SagaIterator {
  yield takeEvery(GetColumnDescription.REQUEST, getColumnDescriptionWorker);
};

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
};
export function* updateColumnDescriptionWatcher(): SagaIterator {
  yield takeEvery(UpdateColumnDescription.REQUEST, updateColumnDescriptionWorker);
};

export function* getLastIndexedWorker(action: GetLastIndexedRequest): SagaIterator {
  try {
    const lastIndexed = yield call(metadataGetLastIndexed);
    yield put({ type: GetLastIndexed.SUCCESS, payload: { lastIndexedEpoch: lastIndexed } });
  } catch (e) {
    yield put({ type: GetLastIndexed.FAILURE });
  }
};
export function* getLastIndexedWatcher(): SagaIterator {
  yield takeEvery(GetLastIndexed.REQUEST, getLastIndexedWorker)
};

export function* getPreviewDataWorker(action: GetPreviewDataRequest): SagaIterator {
  try {
    const response = yield call(metadataGetPreviewData, action.queryParams);
    const { data, status } = response;
    yield put({ type: GetPreviewData.SUCCESS, payload: { data, status } });
  } catch (e) {
    const data = e.response ? e.response.data : {};
    const status = e.response ? e.response.status : null;
    yield put({ type: GetPreviewData.FAILURE, payload: { data, status } });
  }
};
export function* getPreviewDataWatcher(): SagaIterator {
  yield takeEvery(GetPreviewData.REQUEST, getPreviewDataWorker);
};
