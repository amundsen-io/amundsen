import axios, { AxiosResponse } from 'axios';
import * as qs from 'simple-query-string';

import { FeatureMetadata } from 'interfaces/Feature';

export type GetFeatureAPI = {
  msg: string;
  feature: FeatureMetadata;
};

const FEATURE_BASE = '/api/metadata/v0';

export function getFeature(key: string, index?: string, source?: string) {
  const queryParams = qs.stringify({ key, index, source });
  return axios
    .get(`${FEATURE_BASE}/feature?${queryParams}`)
    .then((response: AxiosResponse<GetFeatureAPI>) => {
      const { data, status } = response;
      return {
        feature: data.feature,
        statusCode: status,
      };
    })
    .catch((e) => {
      const { response } = e;
      const statusMessage = response.data?.msg;
      const statusCode = response ? response.status || 500 : 500;
      return Promise.reject({
        statusCode,
        statusMessage,
      });
    });
}
