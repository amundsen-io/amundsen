import {
  GetCurrentUser,
  GetCurrentUserRequest,
  GetCurrentUserResponse,
  CurrentUser
} from './types';

type UserReducerAction = GetCurrentUserRequest | GetCurrentUserResponse;

export interface UserReducerState {
  currentUser: CurrentUser;
}

export function getCurrentUser(): GetCurrentUserRequest {
  return { type: GetCurrentUser.ACTION };
}

const initialState: UserReducerState = {
  currentUser: null,
};

export default function reducer(state: UserReducerState = initialState, action: UserReducerAction): UserReducerState {
  switch (action.type) {
    case GetCurrentUser.SUCCESS:
      return { ...state, currentUser: action.payload };
    default:
      return state;
  }
}
