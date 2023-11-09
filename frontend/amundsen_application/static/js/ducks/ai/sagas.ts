import { SagaIterator } from 'redux-saga';
import { all, call, put, takeEvery } from 'redux-saga/effects';

import {
  getGPTResponseFailure,
  getGPTResponseSuccess
} from './reducer';

import * as API from './api/v0';

import { GetGPTResponse, GetGPTResponseRequest } from './types';

export function* getGPTResponseWorker(action: GetGPTResponseRequest): SagaIterator {
  const { payload } = action;

  try {
    const gptResponse = yield call(API.getGPTResponse, payload.prompt);

    if (payload.onSuccess) {
      yield call(payload.onSuccess, getGPTResponseSuccess(gptResponse));
    }
  } catch (e) {
    if (payload.onFailure) {
      yield call(payload.onFailure, getGPTResponseFailure());
    }
  }
}
export function* getGPTReponseWatcher(): SagaIterator {
  yield takeEvery(GetGPTResponse.REQUEST, getGPTResponseWorker);
}
