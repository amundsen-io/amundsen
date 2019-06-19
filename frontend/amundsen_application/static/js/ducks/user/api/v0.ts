import axios, { AxiosResponse } from 'axios';

import { LoggedInUser, PeopleUser, Resource } from 'interfaces';

export type LoggedInUserResponse = { user: LoggedInUser; msg: string; };
export type UserResponse = { user: PeopleUser; msg: string; };
export type UserOwnResponse = { own: Resource[], msg: string; };
export type UserReadResponse = { read: Resource[], msg: string; };

export function getLoggedInUser() {
  return axios.get(`/api/auth_user`)
    .then((response: AxiosResponse<LoggedInUserResponse>) => {
      return response.data.user;
    });
}

export function getUserById(userId: string) {
  return axios.get(`/api/metadata/v0/user?user_id=${userId}`)
    .then((response: AxiosResponse<UserResponse>) => {
      return response.data.user;
    });
}

export function getUserOwn(userId: string) {
  return axios.get(`/api/metadata/v0/user/own?user_id=${userId}`)
    .then((response: AxiosResponse<UserOwnResponse>) => {
      return response.data
    });
}

export function getUserRead(userId: string) {
  return axios.get(`/api/metadata/v0/user/read?user_id=${userId}`)
    .then((response: AxiosResponse<UserReadResponse>) => {
      return response.data
    });
}
