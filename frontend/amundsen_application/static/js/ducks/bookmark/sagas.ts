import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

 import {
  AddBookmark,
  AddBookmarkRequest,
  GetBookmarks,
  GetBookmarksRequest,
  GetBookmarksForUser,
  GetBookmarksForUserRequest,
  RemoveBookmark,
  RemoveBookmarkRequest
} from './types';

 import {
  addBookmark,
  removeBookmark,
  getBookmarks,
} from './api/v0';

export function* addBookmarkWorker(action: AddBookmarkRequest): SagaIterator {
  let response;
  const { resourceKey, resourceType } = action;

  try {
    yield call(addBookmark, resourceKey, resourceType);

    // TODO - Consider adding the newly bookmarked resource directly to local store. This would save a round trip.
    response = yield call(getBookmarks);
    yield put({ type: AddBookmark.SUCCESS, payload: { bookmarks: response.bookmarks } });
  } catch(e) {
    yield put({ type: AddBookmark.FAILURE, payload: { bookmarks: [] } });
   }
}
export function* addBookmarkWatcher(): SagaIterator {
  yield takeEvery(AddBookmark.REQUEST , addBookmarkWorker)
}


export function* removeBookmarkWorker(action: RemoveBookmarkRequest): SagaIterator {
  let response;
  const { resourceKey, resourceType } = action;
  try {
    response = yield call(removeBookmark, resourceKey, resourceType);
    yield put({ type: RemoveBookmark.SUCCESS, payload: { resourceKey, resourceType }});
  } catch(e) {
    yield put({ type: RemoveBookmark.FAILURE, payload: { resourceKey, resourceType } });
  }
}
export function* removeBookmarkWatcher(): SagaIterator {
  yield takeEvery(RemoveBookmark.REQUEST , removeBookmarkWorker)
}


export function* getBookmarksWorker(action: GetBookmarksRequest): SagaIterator {
  let response;
  try {
    response = yield call(getBookmarks);
    yield put({ type: GetBookmarks.SUCCESS, payload: { bookmarks: response.bookmarks } });
  } catch(e) {
    yield put({ type: GetBookmarks.FAILURE, payload: { bookmarks: [] } });
  }
}
export function* getBookmarksWatcher(): SagaIterator {
  yield takeEvery(GetBookmarks.REQUEST, getBookmarksWorker)
}


export function* getBookmarkForUserWorker(action: GetBookmarksForUserRequest): SagaIterator {
  let response;
  const { userId } = action;

  try {
    response = yield call(getBookmarks, userId);

    yield put({ type: GetBookmarksForUser.SUCCESS, payload: { userId, bookmarks: response.bookmarks } });
  } catch(e) {
    yield put({ type: GetBookmarksForUser.FAILURE, payload: { userId, bookmarks: [] } });
   }
}
export function* getBookmarksForUserWatcher(): SagaIterator {
  yield takeEvery(GetBookmarksForUser.REQUEST, getBookmarkForUserWorker)
}
