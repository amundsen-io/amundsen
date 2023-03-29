// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import axios, { AxiosError, AxiosResponse } from 'axios';
import { DynamicResourceNoticeType } from 'config/config-types';
import * as qs from 'simple-query-string';

export const API_PATH = '/api/notices/v0';

export type NoticesAPI = { msg: DynamicResourceNoticeType[] };

export function getTableNotices(key: string) {
  const queryParams = qs.stringify({ resource: 'table', key });

  return axios
    .get(`${API_PATH}/get_notices?${queryParams}`)
    .then((response: AxiosResponse<NoticesAPI>) => ({
      data: response.data,
      statusCode: response.status,
    }))
    .catch((e: AxiosError<NoticesAPI>) => {
      const { response } = e;
      const statusMessage = response?.data?.msg;
      const statusCode = response?.status;

      return Promise.reject({ statusCode, statusMessage });
    });
}
