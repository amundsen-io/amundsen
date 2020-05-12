import axios, { AxiosResponse } from 'axios';

import * as qs from 'simple-query-string';

import { DashboardMetadata } from 'interfaces/Dashboard';

export type GetDashboardAPI = {
  msg: string;
  dashboard: DashboardMetadata;
}

const DASHBOARD_BASE = '/api/metadata/v0';

export function getDashboard(uri: string, index?: string, source?: string) {
  const queryParams = qs.stringify({ index, source, uri });
  return axios.get(`${DASHBOARD_BASE}/dashboard?${queryParams}`)
  .then((response: AxiosResponse<GetDashboardAPI>) => {
    const { data, status } = response;
    return {
      dashboard: data.dashboard,
      statusCode: status
    };
  })
  .catch((e) => {
    const response = e.response;
    const statusMessage = response ? (response.data ? response.data.msg : undefined) : undefined;
    const statusCode = response ? (response.status || 500) : 500;
    return Promise.reject({
      statusCode,
      statusMessage,
    })
  });
}
