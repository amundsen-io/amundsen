// Setting up different types for now so we can iterate faster as shared params change
export interface User {
  email: string;
  employee_type: string;
  display_name: string;
  first_name: string;
  full_name: string;
  github_username: string;
  is_active: boolean;
  last_name: string;
  manager_fullname: string;
  profile_url: string;
  role_name?: string;
  slack_id: string;
  team_name: string;
  user_id: string;
}
export type LoggedInUser = User & {};

export type UserResponse = { user: User; msg: string; };

/* getLoggedInUser */
export enum GetLoggedInUser {
  ACTION = 'amundsen/current_user/GET_ACTION',
  SUCCESS = 'amundsen/current_user/GET_SUCCESS',
  FAILURE = 'amundsen/current_user/GET_FAILURE',
}

export interface GetLoggedInUserRequest {
  type: GetLoggedInUser.ACTION;
}

export interface GetLoggedInUserResponse {
  type: GetLoggedInUser.SUCCESS | GetLoggedInUser.FAILURE;
  payload?: LoggedInUser;
}

/* getUserById */
export enum GetUser {
  ACTION = 'amundsen/user/GET_ACTION',
  SUCCESS = 'amundsen/user/GET_SUCCESS',
  FAILURE = 'amundsen/user/GET_FAILURE',
}

export interface GetUserRequest {
  type: GetUser.ACTION;
  userId: string;
}

export interface GetUserResponse {
  type: GetUser.SUCCESS | GetUser.FAILURE;
  payload?: User;
}
