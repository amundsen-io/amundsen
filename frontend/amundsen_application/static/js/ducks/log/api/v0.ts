import axios, { AxiosResponse, AxiosError } from 'axios';

export interface ActionLogParams {
  command?: string;
  target_id?: string;
  target_type?: string;
  label?: string;
  location?: string;
  value?: string;
}

const BASE_URL = '/api/log/v0/log_event';


export function postActionLog(params: ActionLogParams) {
  axios.post(BASE_URL, params)
  .then((response: AxiosResponse) => {
    return response.data;
  })
  .catch((error: AxiosError) => {
    if (error.response) {
      return error.response.data;
    }
  });
}
