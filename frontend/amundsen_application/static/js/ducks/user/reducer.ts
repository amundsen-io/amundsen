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
  display_name: '',
  email: '',
  employee_type: '',
  first_name: '',
  full_name: '',
  github_username: '',
  is_active: true,
  last_name: '',
  manager_fullname: '',
  profile_url: '',
  role_name: '',
  slack_id: '',
  team_name: '',
  user_id: '',
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
