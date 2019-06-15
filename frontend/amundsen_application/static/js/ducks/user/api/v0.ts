import axios, { AxiosResponse } from 'axios';

import { LoggedInUser, PeopleUser } from 'interfaces';

export type LoggedInUserResponse = { user: LoggedInUser; msg: string; };
export type UserResponse = { user: PeopleUser; msg: string; };

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
