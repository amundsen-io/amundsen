import {
  AddBookmark,
  AddBookmarkRequest,
  AddBookmarkResponse,
  Bookmark,
  GetBookmarks,
  GetBookmarksForUser,
  GetBookmarksForUserRequest,
  GetBookmarksForUserResponse,
  GetBookmarksRequest,
  GetBookmarksResponse,
  RemoveBookmark,
  RemoveBookmarkRequest,
  RemoveBookmarkResponse,
} from "./types";

export type BookmarkReducerAction =
  AddBookmarkRequest | AddBookmarkResponse |
  GetBookmarksRequest | GetBookmarksResponse |
  GetBookmarksForUserRequest | GetBookmarksForUserResponse |
  RemoveBookmarkRequest | RemoveBookmarkResponse;


export function addBookmark(resourceKey: string, resourceType: string): AddBookmarkRequest {
  return {
    resourceKey,
    resourceType,
    type: AddBookmark.ACTION,
  }
}

export function removeBookmark(resourceKey: string, resourceType: string): RemoveBookmarkRequest {
  return {
    resourceKey,
    resourceType,
    type: RemoveBookmark.ACTION,
  }
}

export function getBookmarks(): GetBookmarksRequest {
  return {
    type: GetBookmarks.ACTION
  }
}

export function getBookmarksForUser(userId: string): GetBookmarksForUserRequest {
  return {
    userId,
    type: GetBookmarksForUser.ACTION,
  }
}

 export interface BookmarkReducerState {
  myBookmarks: Bookmark[];
  myBookmarksIsLoaded: boolean;
  bookmarksForUser: Bookmark[];
}

 const initialState: BookmarkReducerState = {
  myBookmarks: [],
  myBookmarksIsLoaded: false,
  bookmarksForUser: [],
};

 export default function reducer(state: BookmarkReducerState = initialState, action: BookmarkReducerAction): BookmarkReducerState {
  switch(action.type) {
    case RemoveBookmark.SUCCESS:
      const { resourceKey } = action.payload;
      return {
        ...state,
        myBookmarks: state.myBookmarks.filter((bookmark) => bookmark.key !== resourceKey)
      };

    case AddBookmark.SUCCESS:
    case GetBookmarks.SUCCESS:
      return {
        ...state,
        myBookmarks: action.payload,
        myBookmarksIsLoaded: true,
      };
    case AddBookmark.FAILURE:
    case GetBookmarks.FAILURE:
    case GetBookmarksForUser.SUCCESS:
    case GetBookmarksForUser.FAILURE:
    case RemoveBookmark.FAILURE:
    default:
      return state;
  }
}
