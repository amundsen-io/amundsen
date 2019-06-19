import axios, { AxiosResponse } from 'axios';

import { LoggedInUser, PeopleUser, Resource } from 'interfaces';

export type LoggedInUserAPI = { user: LoggedInUser; msg: string; };
export type UserAPI = { user: PeopleUser; msg: string; };
export type UserOwnAPI= { own: Resource[], msg: string; };
export type UserReadAPI = { read: Resource[], msg: string; };

export function getLoggedInUser() {
  return axios.get(`/api/auth_user`)
    .then((response: AxiosResponse<LoggedInUserAPI>) => {
      return response.data.user;
    });
}

export function getUserById(userId: string) {
  return axios.get(`/api/metadata/v0/user?user_id=${userId}`)
    .then((response: AxiosResponse<UserAPI>) => {
      return response.data.user;
    });
}

export function getUserOwn(userId: string) {
  return axios.get(`/api/metadata/v0/user/own?user_id=${userId}`)
    .then((response: AxiosResponse<UserOwnAPI>) => {
      return response.data
    });
}

export function getUserRead(userId: string) {
  return axios.get(`/api/metadata/v0/user/read?user_id=${userId}`)
    .then((response: AxiosResponse<UserReadAPI>) => {
      return response.data
    });
}
