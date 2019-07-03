import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { loggedInUser, userById, userOwn, userRead } from './api/v0';

import {
  GetLoggedInUser,
  GetUser,
  GetUserOwn,
  GetUserOwnRequest,
  GetUserRead,
  GetUserReadRequest,
  GetUserRequest
} from './types';

import {
  getLoggedInUserFailure, getLoggedInUserSuccess,
  getUserFailure, getUserSuccess,
  getUserOwnFailure, getUserOwnSuccess,
  getUserReadFailure, getUserReadSuccess,
} from './reducer';

export function* getLoggedInUserWorker(): SagaIterator {
  try {
    const user = yield call(loggedInUser);
    yield put(getLoggedInUserSuccess(user));
  } catch (e) {
    yield put(getLoggedInUserFailure());
  }
};
export function* getLoggedInUserWatcher(): SagaIterator {
  yield takeEvery(GetLoggedInUser.REQUEST, getLoggedInUserWorker);
};

export function* getUserWorker(action: GetUserRequest): SagaIterator {
  try {
    const user = yield call(userById, action.payload.userId);
    yield put(getUserSuccess(user));
  } catch (e) {
    yield put(getUserFailure());
  }
};
export function* getUserWatcher(): SagaIterator {
  yield takeEvery(GetUser.REQUEST, getUserWorker);
}

export function* getUserOwnWorker(action: GetUserOwnRequest): SagaIterator {
  try {
    const responseData = yield call(userOwn, action.payload.userId);
    yield put(getUserOwnSuccess(responseData.own));
  } catch (e) {
    yield put(getUserOwnFailure())
  }
};

export function* getUserOwnWatcher(): SagaIterator {
  yield takeEvery(GetUserOwn.REQUEST, getUserOwnWorker);
};

export function* getUserReadWorker(action: GetUserReadRequest): SagaIterator {
  try {
    const responseData = yield call(userRead, action.payload.userId);
    yield put(getUserReadSuccess(responseData.read));
  } catch (e) {
    yield put(getUserReadFailure())
  }
};

export function* getUserReadWatcher(): SagaIterator {
  yield takeEvery(GetUserRead.REQUEST, getUserReadWorker);
};
