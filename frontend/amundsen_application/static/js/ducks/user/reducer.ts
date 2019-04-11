import {
  GetLoggedInUser,
  GetLoggedInUserRequest,
  GetLoggedInUserResponse,
  GetUser,
  GetUserRequest,
  GetUserResponse,
  LoggedInUser, User
} from './types';

type UserReducerAction =
  GetLoggedInUserRequest | GetLoggedInUserResponse |
  GetUserRequest | GetUserResponse ;

export interface UserReducerState {
  loggedInUser: LoggedInUser;
  profileUser: User;
}

export function getLoggedInUser(): GetLoggedInUserRequest {
  return { type: GetLoggedInUser.ACTION };
}

export function getUserById(userId: string): GetUserRequest {
  return { userId, type: GetUser.ACTION };
}


const defaultUser = {
  user_id: '',
  display_name: '',
};
const initialState: UserReducerState = {
  loggedInUser: defaultUser,
  profileUser: defaultUser,
};

export default function reducer(state: UserReducerState = initialState, action: UserReducerAction): UserReducerState {
  switch (action.type) {
    case GetLoggedInUser.SUCCESS:
      return { ...state, loggedInUser: action.payload };
    case GetUser.ACTION:
    case GetUser.FAILURE:
      return { ...state, profileUser: defaultUser };
    case GetUser.SUCCESS:
      return { ...state, profileUser: action.payload };
    default:
      return state;
  }
}
