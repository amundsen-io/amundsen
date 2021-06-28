// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import axios, { AxiosResponse, AxiosError } from 'axios';
import * as qs from 'simple-query-string';

import {
  FeatureCode,
  FeatureMetadata,
  FeatureSampleQueryParams,
  PreviewData,
} from 'interfaces';

export type GetFeatureAPI = {
  msg: string;
  featureData: FeatureMetadata;
};

type MessageAPI = { msg: string };

export type PreviewDataAPI = { previewData: PreviewData } & MessageAPI;

const FEATURE_BASE = '/api/metadata/v0';

export function getFeature(key: string, index?: string, source?: string) {
  const queryParams = qs.stringify({ key, index, source });
  return axios
    .get(`${FEATURE_BASE}/feature?${queryParams}`)
    .then((response: AxiosResponse<GetFeatureAPI>) => {
      const { data, status } = response;
      return {
        feature: data.featureData,
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

export function getPreviewData(queryParams: FeatureSampleQueryParams) {
  return axios({
    url: '/api/preview/v0/feature_preview',
    method: 'POST',
    data: queryParams,
  })
    .then((response: AxiosResponse<PreviewDataAPI>) => ({
      data: response.data.previewData,
      status: response.status,
    }))
    .catch((e: AxiosError<PreviewDataAPI>) => {
      const { response } = e;
      let data = {};
      if (response && response.data && response.data.previewData) {
        data = response.data.previewData;
      }
      const status = response ? response.status : null;
      return Promise.reject({ data, status });
    });
}

export type GetFeatureCodeAPI = {
  msg: string;
  featureCode: FeatureCode;
};
export function getFeatureCode(key: string) {
  const queryParams = qs.stringify({ key });
  return axios
    .get(`${FEATURE_BASE}/get_feature_generation_code?${queryParams}`)
    .then((response: AxiosResponse<GetFeatureCodeAPI>) => {
      const { data, status } = response;
      return {
        featureCode: data,
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
