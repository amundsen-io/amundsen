import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { GetLoggedInUser, GetUser, GetUserRequest } from './types';
import { getLoggedInUser, getUserById } from './api/v0';

export function* getLoggedInUserWorker(): SagaIterator {
  try {
    const user = yield call(getLoggedInUser);
    yield put({ type: GetLoggedInUser.SUCCESS, payload: { user } });
  } catch (e) {
    yield put({ type: GetLoggedInUser.FAILURE });
  }
};
export function* getLoggedInUserWatcher(): SagaIterator {
  yield takeEvery(GetLoggedInUser.REQUEST, getLoggedInUserWorker);
};

export function* getUserWorker(action: GetUserRequest): SagaIterator {
  try {
    const user = yield call(getUserById, action.userId);
    yield put({ type: GetUser.SUCCESS, payload: { user } });
  } catch (e) {
    yield put({ type: GetUser.FAILURE});
  }
};
export function* getUserWatcher(): SagaIterator {
  yield takeEvery(GetUser.REQUEST, getUserWorker);
};
