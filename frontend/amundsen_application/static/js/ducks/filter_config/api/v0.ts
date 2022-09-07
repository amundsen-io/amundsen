import axios, { AxiosResponse, AxiosError } from 'axios';

export const API_PATH = '/api/search/v1';

export type GetFilterConfigAPI = {
  msg: string;
  data: any;
};

export function getFilterConfig() {
  return axios
    .get(`${API_PATH}/filter_config`)
    .then((response: AxiosResponse<GetFilterConfigAPI>) => {
      const { data, status } = response;
      return {
        data: data.data,
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
