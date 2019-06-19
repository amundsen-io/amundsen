import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import {
  GetLoggedInUser,
  GetUser,
  GetUserOwn,
  GetUserOwnRequest,
  GetUserRead,
  GetUserReadRequest,
  GetUserRequest
} from './types';
import { getLoggedInUser, getUserById, getUserOwn, getUserRead } from './api/v0';

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
    yield put({ type: GetUser.FAILURE });
  }
};
export function* getUserWatcher(): SagaIterator {
  yield takeEvery(GetUser.REQUEST, getUserWorker);
}

export function* getUserOwnWorker(action: GetUserOwnRequest): SagaIterator {
  try {
    const userOwn = yield call(getUserOwn, action.payload.userId);
    yield put({ type: GetUserOwn.SUCCESS, payload: { own: userOwn.own }});
  } catch (e) {
    yield put({ type: GetUserOwn.FAILURE })
  }
};

export function* getUserOwnWatcher(): SagaIterator {
  yield takeEvery(GetUserOwn.REQUEST, getUserOwnWorker);
};

export function* getUserReadWorker(action: GetUserReadRequest): SagaIterator {
  try {
    const userRead = yield call(getUserRead, action.payload.userId);
    yield put({ type: GetUserRead.SUCCESS, payload: { read: userRead.read }});
  } catch (e) {
    yield put({ type: GetUserRead.FAILURE })
  }
};

export function* getUserReadWatcher(): SagaIterator {
  yield takeEvery(GetUserRead.REQUEST, getUserReadWorker);
};
