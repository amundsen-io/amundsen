import { call, put, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

import {
  GetPreviewData,
  GetPreviewDataRequest,
} from './reducer';

import {
  getPreviewData,
} from '../api/preview/v0';


export function* getPreviewDataWorker(action: GetPreviewDataRequest): SagaIterator {
  let response;
  try {
    response = yield call(getPreviewData, action);
    yield put({ type: GetPreviewData.SUCCESS, payload: response });
  } catch (e) {
    yield put({ type: GetPreviewData.FAILURE, payload: response });
  }
}

export function* getPreviewDataWatcher(): SagaIterator {
  yield takeEvery(GetPreviewData.ACTION, getPreviewDataWorker);
}
