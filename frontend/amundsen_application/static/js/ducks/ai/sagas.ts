import { SagaIterator } from 'redux-saga';
import { all, call, put, takeEvery } from 'redux-saga/effects';

import {
  getSnowflakeTableSharesFailure,
  getSnowflakeTableSharesSuccess
} from './reducer';

import * as API from './api/v0';

import { GetGPTResponse, GetGPTResponseRequest } from './types';

export function* getGPTResponseWorker(action: GetGPTResponseRequest): SagaIterator {
  const { prompt } = action.payload;
  try {
    const gptResponse = yield call(API.getGPTResponse, prompt);

    yield put(getSnowflakeTableSharesSuccess(gptResponse));
  } catch (e) {
    yield put(getSnowflakeTableSharesFailure());
  }
}
export function* getGPTReponseWatcher(): SagaIterator {
  yield takeEvery(GetGPTResponse.REQUEST, getGPTResponseWorker);
}
