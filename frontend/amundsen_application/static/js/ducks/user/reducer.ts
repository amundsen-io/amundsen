import { LoggedInUser, PeopleUser } from 'interfaces';

import {
  GetLoggedInUser,
  GetLoggedInUserRequest,
  GetLoggedInUserResponse,
  GetUser,
  GetUserRequest,
  GetUserResponse,
} from './types';

/* ACTIONS */
export function getLoggedInUser(): GetLoggedInUserRequest {
  return { type: GetLoggedInUser.REQUEST };
};
export function getUserById(userId: string): GetUserRequest {
  return { userId, type: GetUser.REQUEST };
};

/* REDUCER */
export interface UserReducerState {
  loggedInUser: LoggedInUser;
  profileUser: PeopleUser;
};

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

export default function reducer(state: UserReducerState = initialState, action): UserReducerState {
  switch (action.type) {
    case GetLoggedInUser.SUCCESS:
      return { ...state, loggedInUser: (<GetLoggedInUserResponse>action).payload.user };
    case GetUser.REQUEST:
    case GetUser.FAILURE:
      return { ...state, profileUser: defaultUser };
    case GetUser.SUCCESS:
      return { ...state, profileUser: (<GetUserResponse>action).payload.user };
    default:
      return state;
  }
}
