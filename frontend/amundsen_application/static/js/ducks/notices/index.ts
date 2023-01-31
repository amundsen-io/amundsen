import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { DynamicResourceNoticeType } from 'config/config-types';

import * as API from './api/v0';

import { GetNotices, GetNoticesRequest, GetNoticesResponse } from './types';

export const initialNoticesState: DynamicResourceNoticeType[] = [];

/* ACTIONS */
export function getNotices(key: string): GetNoticesRequest {
  return {
    type: GetNotices.REQUEST,
    payload: { key },
  };
}

export function getNoticesSuccess(
  data: DynamicResourceNoticeType[],
  statusCode: number
): GetNoticesResponse {
  return {
    type: GetNotices.SUCCESS,
    payload: {
      notices: data,
      statusCode,
    },
  };
}

export function getNoticesFailure(
  statusCode: number,
  statusMessage: string
): GetNoticesResponse {
  return {
    type: GetNotices.FAILURE,
    payload: {
      notices: initialNoticesState,
      statusCode,
      statusMessage,
    },
  };
}

/* SAGAS */
export function* getNoticesWorker(action: GetNoticesRequest): SagaIterator {
  const { key } = action.payload;

  try {
    const response = yield call(API.getTableNotices, key);
    const { data, statusCode } = response;

    yield put(getNoticesSuccess(data, statusCode));
  } catch (error) {
    const { statusCode, statusMessage } = error;

    yield put(getNoticesFailure(statusCode, statusMessage));
  }
}

export function* getNoticesWatcher(): SagaIterator {
  yield takeEvery(GetNotices.REQUEST, getNoticesWorker);
}
