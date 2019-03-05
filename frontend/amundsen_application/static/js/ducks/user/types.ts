export interface CurrentUser {
  display_name: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_url: string;
}

export enum GetCurrentUser {
  ACTION = 'amundsen/user/GET_ACTION',
  SUCCESS = 'amundsen/user/GET_SUCCESS',
  FAILURE = 'amundsen/user/GET_FAILURE',
}

export interface GetCurrentUserRequest {
  type: GetCurrentUser.ACTION;
}

export interface GetCurrentUserResponse {
  type: GetCurrentUser.SUCCESS | GetCurrentUser.FAILURE;
  payload?: CurrentUser;
}
