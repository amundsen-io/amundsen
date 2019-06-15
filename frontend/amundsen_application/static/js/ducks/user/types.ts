import { LoggedInUser, PeopleUser } from 'interfaces';

export enum GetLoggedInUser {
  REQUEST = 'amundsen/current_user/GET_REQUEST',
  SUCCESS = 'amundsen/current_user/GET_SUCCESS',
  FAILURE = 'amundsen/current_user/GET_FAILURE',
};
export interface GetLoggedInUserRequest {
  type: GetLoggedInUser.REQUEST;
};
export interface GetLoggedInUserResponse {
  type: GetLoggedInUser.SUCCESS | GetLoggedInUser.FAILURE;
  payload?: {
    user: LoggedInUser;
  };
};

export enum GetUser {
  REQUEST = 'amundsen/user/GET_REQUEST',
  SUCCESS = 'amundsen/user/GET_SUCCESS',
  FAILURE = 'amundsen/user/GET_FAILURE',
};
export interface GetUserRequest {
  type: GetUser.REQUEST;
  userId: string;
};
export interface GetUserResponse {
  type: GetUser.SUCCESS | GetUser.FAILURE;
  payload?: {
    user: PeopleUser;
  };
};
