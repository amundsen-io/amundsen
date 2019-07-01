import { Bookmark } from 'interfaces';

import {
  AddBookmark,
  AddBookmarkRequest,
  AddBookmarkResponse,
  GetBookmarks,
  GetBookmarksRequest,
  GetBookmarksResponse,
  GetBookmarksForUser,
  GetBookmarksForUserRequest,
  GetBookmarksForUserResponse,
  RemoveBookmark,
  RemoveBookmarkRequest,
  RemoveBookmarkResponse,
} from './types';

/* ACTIONS */
export function addBookmark(resourceKey: string, resourceType: string): AddBookmarkRequest {
  return {
    payload: {
      resourceKey,
      resourceType,
    },
    type: AddBookmark.REQUEST,
  }
}
export function addBookmarkFailure(): AddBookmarkResponse {
  return { type: AddBookmark.FAILURE };
}
export function addBookmarkSuccess(bookmarks: Bookmark[]): AddBookmarkResponse {
  return { type: AddBookmark.SUCCESS, payload: { bookmarks } };
}

export function removeBookmark(resourceKey: string, resourceType: string): RemoveBookmarkRequest {
  return {
    payload: {
      resourceKey,
      resourceType,
    },
    type: RemoveBookmark.REQUEST,
  }
}
export function removeBookmarkFailure(): RemoveBookmarkResponse {
  return { type: RemoveBookmark.FAILURE };
}
export function removeBookmarkSuccess(resourceKey: string, resourceType: string): RemoveBookmarkResponse {
  return { type: RemoveBookmark.SUCCESS, payload: { resourceKey, resourceType } };
}

export function getBookmarks(): GetBookmarksRequest {
  return {
    type: GetBookmarks.REQUEST,
  }
}
export function getBookmarksFailure(): GetBookmarksResponse {
  return { type: GetBookmarks.FAILURE, payload: { bookmarks: [] } };
}
export function getBookmarksSuccess(bookmarks: Bookmark[]): GetBookmarksResponse {
  return { type: GetBookmarks.SUCCESS, payload: { bookmarks } };
}

export function getBookmarksForUser(userId: string): GetBookmarksForUserRequest {
  return {
    payload: {
      userId,
    },
    type: GetBookmarksForUser.REQUEST,
  }
}
export function getBookmarksForUserFailure(): GetBookmarksForUserResponse {
  return { type: GetBookmarksForUser.FAILURE, payload: { bookmarks: [] } };
}
export function getBookmarksForUserSuccess(bookmarks: Bookmark[]): GetBookmarksForUserResponse {
  return { type: GetBookmarksForUser.SUCCESS, payload: { bookmarks } };
}

/* REDUCER */
export interface BookmarkReducerState {
  myBookmarks: Bookmark[];
  myBookmarksIsLoaded: boolean;
  bookmarksForUser: Bookmark[];
}

export const initialState: BookmarkReducerState = {
  myBookmarks: [],
  myBookmarksIsLoaded: false,
  bookmarksForUser: [],
};

export default function reducer(state: BookmarkReducerState = initialState, action): BookmarkReducerState {
  switch(action.type) {
    case AddBookmark.SUCCESS:
    case GetBookmarks.SUCCESS:
      return {
        ...state,
        myBookmarks: (<GetBookmarksResponse>action).payload.bookmarks,
        myBookmarksIsLoaded: true,
      };
    case GetBookmarksForUser.REQUEST:
      return {
        ...state,
        bookmarksForUser: [],
      };
    case GetBookmarksForUser.SUCCESS:
      return {
        ...state,
        bookmarksForUser: (<GetBookmarksForUserResponse>action).payload.bookmarks,
      };
    case RemoveBookmark.SUCCESS:
      const { resourceKey } = (<RemoveBookmarkResponse>action).payload;
      return {
        ...state,
        myBookmarks: state.myBookmarks.filter((bookmark) => bookmark.key !== resourceKey)
      };
    case AddBookmark.FAILURE:
    case GetBookmarks.FAILURE:
    case GetBookmarksForUser.FAILURE:
    case RemoveBookmark.FAILURE:
    default:
      return state;
  }
}
