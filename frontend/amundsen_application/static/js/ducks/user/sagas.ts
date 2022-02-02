import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api/v0';

import {
  CreateUser,
  CreateUserRequest,
  ActivateUser,
  ActivateUserRequest,
  GetLoggedInUser,
  GetUser,
  GetUserOwn,
  GetUserOwnRequest,
  GetUserRead,
  GetUserReadRequest,
  GetUserRequest,
} from './types';

import {
  createUserFailure,
  createUserSuccess,
  activateUserFailure,
  activateUserSuccess,
  getLoggedInUserFailure,
  getLoggedInUserSuccess,
  getUserFailure,
  getUserSuccess,
  getUserOwnFailure,
  getUserOwnSuccess,
  getUserReadFailure,
  getUserReadSuccess,
} from './reducer';

export function* getLoggedInUserWorker(): SagaIterator {
  try {
    const user = yield call(API.getLoggedInUser);
    yield put(getLoggedInUserSuccess(user));
  } catch (e) {
    yield put(getLoggedInUserFailure());
  }
}
export function* getLoggedInUserWatcher(): SagaIterator {
  yield takeEvery(GetLoggedInUser.REQUEST, getLoggedInUserWorker);
}

export function* createUserWorker(action: CreateUserRequest): SagaIterator {
  try {
    const { payload } = action;
    const user = yield call(API.createUser, payload.user);
    yield put(createUserSuccess(user));
  } catch (e) {
    yield put(createUserFailure());
  }
}
export function* createUserWatcher(): SagaIterator {
  yield takeEvery(CreateUser.REQUEST, createUserWorker);
}

export function* activateUserWorker(action: ActivateUserRequest): SagaIterator {
  try {
    const { payload } = action;
    const user = yield call(API.activateUser, payload.databricksId);
    yield put(activateUserSuccess(user));
  } catch (e) {
    yield put(activateUserFailure());
  }
}
export function* activateUserWatcher(): SagaIterator {
  yield takeEvery(ActivateUser.REQUEST, activateUserWorker);
}

export function* getUserWorker(action: GetUserRequest): SagaIterator {
  try {
    const { payload } = action;
    const user = yield call(
      API.getUser,
      payload.userId,
      payload.index,
      payload.source
    );
    yield put(getUserSuccess(user));
  } catch (e) {
    yield put(getUserFailure());
  }
}
export function* getUserWatcher(): SagaIterator {
  yield takeEvery(GetUser.REQUEST, getUserWorker);
}

export function* getUserOwnWorker(action: GetUserOwnRequest): SagaIterator {
  try {
    const responseData = yield call(API.getUserOwn, action.payload.userId);
    yield put(getUserOwnSuccess(responseData.own));
  } catch (e) {
    yield put(getUserOwnFailure());
  }
}

export function* getUserOwnWatcher(): SagaIterator {
  yield takeEvery(GetUserOwn.REQUEST, getUserOwnWorker);
}

export function* getUserReadWorker(action: GetUserReadRequest): SagaIterator {
  try {
    const responseData = yield call(API.getUserRead, action.payload.userId);
    yield put(getUserReadSuccess(responseData.read));
  } catch (e) {
    yield put(getUserReadFailure());
  }
}

export function* getUserReadWatcher(): SagaIterator {
  yield takeEvery(GetUserRead.REQUEST, getUserReadWorker);
}
