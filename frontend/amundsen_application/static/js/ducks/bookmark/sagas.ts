import { call, put, takeEvery } from 'redux-saga/effects';
import { SagaIterator } from 'redux-saga';

 import {
  AddBookmark,
  AddBookmarkRequest,
  GetBookmarks,
  GetBookmarksForUser,
  GetBookmarksForUserRequest,
  GetBookmarksRequest,
  RemoveBookmark,
  RemoveBookmarkRequest
} from "./types";

 import {
  addBookmark,
  removeBookmark,
  getBookmarks,
} from "./api/v0";


 // AddBookmarks
export function* addBookmarkWorker(action: AddBookmarkRequest): SagaIterator {
  let response;
  const { resourceKey, resourceType } = action;

  try {
    yield call(addBookmark, resourceKey, resourceType);

    // TODO - Consider adding the newly bookmarked resource directly to local store. This would save a round trip.
    response = yield call(getBookmarks);
    yield put({ type: AddBookmark.SUCCESS, payload: response.bookmarks });
  } catch(e) {
    yield put({ type: AddBookmark.FAILURE, payload: response });
   }
}
export function* addBookmarkWatcher(): SagaIterator {
  yield takeEvery(AddBookmark.ACTION , addBookmarkWorker)
}


 // RemoveBookmarks
export function* removeBookmarkWorker(action: RemoveBookmarkRequest): SagaIterator {
  let response;
  const { resourceKey, resourceType } = action;
  try {
    response = yield call(removeBookmark, resourceKey, resourceType);
    yield put({ type: RemoveBookmark.SUCCESS, payload: { resourceKey, resourceType }});
  } catch(e) {
    yield put({ type: RemoveBookmark.FAILURE, payload: response });
  }
}
export function* removeBookmarkWatcher(): SagaIterator {
  yield takeEvery(RemoveBookmark.ACTION , removeBookmarkWorker)
}


 // GetBookmarks
export function* getBookmarksWorker(action: GetBookmarksRequest): SagaIterator {
  let response;
  try {
    response = yield call(getBookmarks);
    yield put({ type: GetBookmarks.SUCCESS, payload: response.bookmarks });
  } catch(e) {
    yield put({ type: GetBookmarks.FAILURE, payload: response });
  }
}
export function* getBookmarkskWatcher(): SagaIterator {
  yield takeEvery(GetBookmarks.ACTION, getBookmarksWorker)
}


 // GetBookmarksForUser
export function* getBookmarkForUserWorker(action: GetBookmarksForUserRequest): SagaIterator {
  let response;
  const { userId } = action;

  try {
    response = yield call(getBookmarks, userId);

    yield put({ type: GetBookmarksForUser.SUCCESS, payload: { userId, bookmarks: response.bookmarks } });
  } catch(e) {
    yield put({ type: GetBookmarksForUser.FAILURE, payload: response });
   }
}
export function* getBookmarksForUserWatcher(): SagaIterator {
  yield takeEvery(GetBookmarksForUser.ACTION, getBookmarkForUserWorker)
}
