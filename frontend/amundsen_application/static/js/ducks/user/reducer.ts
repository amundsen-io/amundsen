import { CurrentUser } from './types';

export enum GetCurrentUser {
  ACTION = 'amundsen/user/GET_ACTION',
  SUCCESS = 'amundsen/user/GET_SUCCESS',
  FAILURE = 'amundsen/user/GET_FAILURE',
}

export interface GetCurrentUserRequest {
  type: GetCurrentUser.ACTION;
}

export function getCurrentUser(): GetCurrentUserRequest {
  return { type: GetCurrentUser.ACTION };
}

interface GetCurrentUserResponse {
  type: GetCurrentUser.SUCCESS | GetCurrentUser.FAILURE;
  payload?: CurrentUser;
}
type GetUserAction = GetCurrentUserRequest | GetCurrentUserResponse;

type UserReducerAction = GetUserAction

export interface UserReducerState {
  currentUser: CurrentUser;
}

const initialState: UserReducerState = {
  currentUser: null,
};

export default function reducer(state: UserReducerState = initialState, action: UserReducerAction): UserReducerState {
  switch (action.type) {
    case GetCurrentUser.FAILURE:
      return state;
    case GetCurrentUser.SUCCESS:
      return { ...state, currentUser: action.payload };
    default:
      return state;
  }
}
