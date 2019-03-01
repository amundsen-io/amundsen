import axios, { AxiosResponse, AxiosError } from 'axios';

import { CurrentUser } from '../types';

export function getCurrentUser() {
  return axios.get(`/api/current_user`)
    .then((response: AxiosResponse<CurrentUser>) => {
      return response.data;
    }).catch((error: AxiosError) => {
      console.log(error.response);
    });
}
