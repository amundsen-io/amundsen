import { Bookmark } from 'interfaces';

import {
  AddBookmark,
  AddBookmarkRequest,
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
export function removeBookmark(resourceKey: string, resourceType: string): RemoveBookmarkRequest {
  return {
    payload: {
      resourceKey,
      resourceType,
    },
    type: RemoveBookmark.REQUEST,
  }
}
export function getBookmarks(): GetBookmarksRequest {
  return {
    type: GetBookmarks.REQUEST,
  }
}
export function getBookmarksForUser(userId: string): GetBookmarksForUserRequest {
  return {
    payload: {
      userId,
    },
    type: GetBookmarksForUser.REQUEST,
  }
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
    case RemoveBookmark.SUCCESS:
      const { resourceKey } = (<RemoveBookmarkResponse>action).payload;
      return {
        ...state,
        myBookmarks: state.myBookmarks.filter((bookmark) => bookmark.key !== resourceKey)
      };
    case AddBookmark.SUCCESS:
    case GetBookmarks.SUCCESS:
      return {
        ...state,
        myBookmarks: (<GetBookmarksResponse>action).payload.bookmarks,
        myBookmarksIsLoaded: true,
      };

    case GetBookmarksForUser.SUCCESS:
    case GetBookmarksForUser.FAILURE:
      return {
        ...state,
        bookmarksForUser: (<GetBookmarksForUserResponse>action).payload.bookmarks,
      };

    case AddBookmark.FAILURE:
    case GetBookmarks.FAILURE:
    case RemoveBookmark.FAILURE:
    default:
      return state;
  }
}

