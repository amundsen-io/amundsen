import { expectSaga, testSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import { throwError } from 'redux-saga-test-plan/providers';

import { Bookmark, ResourceType } from 'interfaces';

import { addBookmark as addBkmrk, getBookmarks as getBkmrks, removeBookmark as removeBkmrk } from '../api/v0';
import reducer, { addBookmark, getBookmarks, getBookmarksForUser, removeBookmark, initialState, BookmarkReducerState } from '../reducer';
import {
  addBookmarkWatcher, addBookmarkWorker,
  getBookmarksWatcher, getBookmarksWorker,
  getBookmarksForUserWatcher, getBookmarkForUserWorker,
  removeBookmarkWatcher, removeBookmarkWorker,
} from '../sagas';
import {
  AddBookmark, AddBookmarkRequest,
  GetBookmarks,
  GetBookmarksForUser, GetBookmarksForUserRequest,
  RemoveBookmark, RemoveBookmarkRequest,
} from '../types';

describe('bookmark ducks', () => {
  let testResourceKey;
  let testResourceType;
  let testUserId;
  beforeAll(() => {
    testResourceKey = 'key';
    testResourceType = ResourceType.table;
    testUserId = 'userId';
  });
  describe('actions', () => {
    describe('addBookmark', () => {
      it('should return action of type AddBookmarkRequest', () => {
        expect(addBookmark(testResourceKey, testResourceType)).toEqual({ type: AddBookmark.REQUEST, resourceKey: testResourceKey, resourceType: testResourceType });
      });
    });

    describe('getBookmarks', () => {
      it('should return action of type GetBookmarksRequest', () => {
        expect(getBookmarks()).toEqual({ type: GetBookmarks.REQUEST });
      });
    });

    describe('getBookmarksForUser', () => {
      it('should return action of type GetBookmarksForUserRequest', () => {
        expect(getBookmarksForUser(testUserId)).toEqual({ type: GetBookmarksForUser.REQUEST, userId: testUserId });
      });
    });

    describe('removeBookmark', () => {
      it('should return action of type RemoveBookmarkRequest', () => {
        expect(removeBookmark(testResourceKey, testResourceType)).toEqual({ type: RemoveBookmark.REQUEST, resourceKey: testResourceKey, resourceType: testResourceType });
      });
    });
  });

  describe('reducer', () => {
    let testState: BookmarkReducerState;
    let bookmarkList: Bookmark[];
    beforeAll(() => {
      bookmarkList = [
        {
          key: 'bookmarked_key',
          type: ResourceType.table,
          cluster: 'cluster',
          database: 'database',
          description: 'description',
          name: 'name',
          schema_name: 'schema_name',
        },
      ];
      testState = {
        myBookmarks: bookmarkList,
        myBookmarksIsLoaded: false,
        bookmarksForUser: [],
      };
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
      expect(reducer(testState, { type: AddBookmark.FAILURE })).toEqual(testState);
      expect(reducer(testState, { type: GetBookmarks.FAILURE })).toEqual(testState);
      expect(reducer(testState, { type: RemoveBookmark.FAILURE })).toEqual(testState);
    });

    it('should handle RemoveBookmark.SUCCESS', () => {
      expect(reducer(testState, { type: RemoveBookmark.SUCCESS, payload: { resourceType: ResourceType.table, resourceKey: 'bookmarked_key' }})).toEqual({
        ...testState,
        myBookmarks: [],
      });
    });

    it('should handle AddBookmark.SUCCESS', () => {
      expect(reducer(initialState, { type: AddBookmark.SUCCESS, payload: { bookmarks: bookmarkList } })).toEqual({
        ...initialState,
        myBookmarks: bookmarkList,
        myBookmarksIsLoaded: true,
      });
    });

    it('should handle GetBookmarks.SUCCESS', () => {
      expect(reducer(initialState, { type: GetBookmarks.SUCCESS, payload: { bookmarks: bookmarkList } })).toEqual({
        ...initialState,
        myBookmarks: bookmarkList,
        myBookmarksIsLoaded: true,
      });
    });
  });

describe('sagas', () => {
    describe('addBookmarkWatcher', () => {
      it('takes AddBookmark.REQUEST with addBookmarkWorker', () => {
        testSaga(addBookmarkWatcher)
          .next()
          .takeEveryEffect(AddBookmark.REQUEST, addBookmarkWorker);
      });
    });

    describe('addBookmarkWorker', () => {
      let action: AddBookmarkRequest;
      let testResourceKey;
      let testResourceType;
      beforeAll(() => {
        testResourceKey = 'bookmarked_key';
        testResourceType = ResourceType.table;
        action = addBookmark(testResourceKey, testResourceType);
      })

      it('adds a bookmark', () => {
        const bookmarks = [
          {
            key: testResourceKey,
            type: testResourceType,
            cluster: 'cluster',
            database: 'database',
            description: 'description',
            name: 'name',
            schema_name: 'schema_name',
          },
        ];
        return expectSaga(addBookmarkWorker, action)
          .provide([
            [matchers.call.fn(addBkmrk), {}],
            [matchers.call.fn(getBkmrks), { bookmarks }],
          ])
          .put({
            type: AddBookmark.SUCCESS,
            payload: { bookmarks }
          })
          .run();
      });

      it('handles request error', () => {
        return expectSaga(addBookmarkWorker, action)
          .provide([
            [matchers.call.fn(addBkmrk), throwError(new Error())],
            [matchers.call.fn(getBkmrks), throwError(new Error())],
          ])
          .put({
            type: AddBookmark.FAILURE,
            payload: { bookmarks: [] }
          })
          .run();
      });
    });

    describe('getBookmarksWatcher', () => {
      it('takes GetBookmark.REQUEST with getBookmarksWorker', () => {
        testSaga(getBookmarksWatcher)
          .next()
          .takeEveryEffect(GetBookmarks.REQUEST, getBookmarksWorker);
      });
    });

    describe('getBookmarksWorker', () => {
      it('gets bookmarks', () => {
        const bookmarks = [
          {
            key: testResourceKey,
            type: testResourceType,
            cluster: 'cluster',
            database: 'database',
            description: 'description',
            name: 'name',
            schema_name: 'schema_name',
          },
        ];
        return expectSaga(getBookmarksWorker)
          .provide([
            [matchers.call.fn(getBkmrks), { bookmarks }],
          ])
          .put({
            type: GetBookmarks.SUCCESS,
            payload: { bookmarks }
          })
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getBookmarksWorker)
          .provide([
            [matchers.call.fn(getBkmrks), throwError(new Error())],
          ])
          .put({
            type: GetBookmarks.FAILURE,
            payload: { bookmarks: [] }
          })
          .run();
      });
    });

    describe('getBookmarksForUserWatcher', () => {
      it('takes GetBookmarksForUser.REQUEST with getBookmarkForUserWorker', () => {
        testSaga(getBookmarksForUserWatcher)
          .next()
          .takeEveryEffect(GetBookmarksForUser.REQUEST, getBookmarkForUserWorker);
      });
    });

    describe('getBookmarkForUserWorker', () => {
      let action: GetBookmarksForUserRequest;
      let testUserId;
      beforeAll(() => {
        testUserId = 'userId';
        action = getBookmarksForUser(testUserId);
      });

      it('adds a bookmark', () => {
        const bookmarks = [
          {
            key: testResourceKey,
            type: testResourceType,
            cluster: 'cluster',
            database: 'database',
            description: 'description',
            name: 'name',
            schema_name: 'schema_name',
          },
        ];
        return expectSaga(getBookmarkForUserWorker, action)
          .provide([
            [matchers.call.fn(getBkmrks), { bookmarks, userId: action.userId }],
          ])
          .put({
            type: GetBookmarksForUser.SUCCESS,
            payload: { bookmarks, userId: action.userId }
          })
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getBookmarkForUserWorker, action)
          .provide([
            [matchers.call.fn(getBkmrks), throwError(new Error())],
          ])
          .put({
            type: GetBookmarksForUser.FAILURE,
            payload: { bookmarks: [], userId: action.userId }
          })
          .run();
      });
    });

    describe('removeBookmarkWatcher', () => {
      it('takes RemoveBookmark.REQUEST with removeBookmarkWorker', () => {
        testSaga(removeBookmarkWatcher)
          .next()
          .takeEveryEffect(RemoveBookmark.REQUEST, removeBookmarkWorker);
      });
    });

    describe('removeBookmarkWorker', () => {
      let action: RemoveBookmarkRequest;
      let testResourceKey;
      let testResourceType;
      beforeAll(() => {
        testResourceKey = 'bookmarked_key';
        testResourceType = ResourceType.table;
        action = removeBookmark(testResourceKey, testResourceType);
      });

      it('removes a bookmark', () => {
        return expectSaga(removeBookmarkWorker, action)
          .provide([
            [matchers.call.fn(removeBkmrk), {}],
          ])
          .put({
            type: RemoveBookmark.SUCCESS,
            payload: { resourceKey: action.resourceKey, resourceType: action.resourceType }
          })
          .run();
      });

      it('handles request error', () => {
        return expectSaga(removeBookmarkWorker, action)
          .provide([
            [matchers.call.fn(removeBkmrk), throwError(new Error())],
          ])
          .put({
            type: RemoveBookmark.FAILURE,
            payload: { resourceKey: action.resourceKey, resourceType: action.resourceType }
          })
          .run();
      });
    });
  });
});
