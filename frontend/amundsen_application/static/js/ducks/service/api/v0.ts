import * as qs from 'simple-query-string';
import axios, { AxiosResponse, AxiosError } from 'axios';

import { ServiceMetaData } from 'interfaces';

export const API_PATH = '/api/metadata/v0';

export type GetServiceAPI = {
  msg: string;
  serviceData: ServiceMetaData;
};

export function getService(key: string, index?: string, source?: string) {
  const queryParams = qs.stringify({ key, index, source });
  return axios
    .get(`${API_PATH}/service?${queryParams}`)
    .then((response: AxiosResponse<GetServiceAPI>) => {
      const { data, status } = response;
      return {
        service: data.serviceData,
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
