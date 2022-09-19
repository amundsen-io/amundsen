import * as qs from 'simple-query-string';
import axios, { AxiosResponse, AxiosError } from 'axios';

import { AppEventMetaData } from 'interfaces';

export const API_PATH = '/api/metadata/v0';

export type GetAppEventAPI = {
  msg: string;
  eventData: AppEventMetaData;
};

export function getAppEvent(key: string, index?: string, source?: string) {
  const queryParams = qs.stringify({ key, index, source });
  return axios
    .get(`${API_PATH}/events?${queryParams}`)
    .then((response: AxiosResponse<GetAppEventAPI>) => {
      const { data, status } = response;
      return {
        appEvent: data.eventData,
        statusCode: status,
      };
    })
    .catch((e) => {
      const { response } = e;
      const statusMessage = response.data?.msg;
      const statusCode = response?.status || 500;
      return Promise.reject({
        statusCode,
        statusMessage,
      });
    });
}
