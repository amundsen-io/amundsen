import axios, { AxiosResponse, AxiosError } from 'axios';

import {
  ProviderMetadata,
  DashboardResource,
  User,
  Tag,
  ResourceType,
} from 'interfaces';

/** HELPERS **/
import { indexDashboardsEnabled } from 'config/config-utils';
import {
  getProviderQueryParams,
  getRelatedDashboardSlug,
  getProviderDataFromResponseData,
  shouldSendNotification,
} from './helpers';

const JSONBig = require('json-bigint');

export const API_PATH = '/api/metadata/v0';

type MessageAPI = { msg: string };

export type ProviderData = ProviderMetadata & {
  tags: Tag[];
};
export type DescriptionAPI = { description: string } & MessageAPI;
export type ProviderDataAPI = { providerData: ProviderData } & MessageAPI;
export type RelatedDashboardDataAPI = {
  dashboards: DashboardResource[];
} & MessageAPI;

export function getProviderData(key: string, index?: string, source?: string) {
  const providerQueryParams = getProviderQueryParams({ key, index, source });
  const providerURL = `${API_PATH}/provider?${providerQueryParams}`;
  const providerRequest = axios.get<ProviderDataAPI>(providerURL);

  return providerRequest.then((providerResponse: AxiosResponse<ProviderDataAPI>) => ({
    data: getProviderDataFromResponseData(providerResponse.data),
    tags: providerResponse.data.providerData.tags,
    statusCode: providerResponse.status,
  }));
}

export function getProviderDashboards(providerKey: string) {
  if (!indexDashboardsEnabled()) {
    return Promise.resolve({ dashboards: [] });
  }

  const relatedDashboardsSlug: string = getRelatedDashboardSlug(providerKey);
  const relatedDashboardsURL: string = `${API_PATH}/provider/${relatedDashboardsSlug}/dashboards`;
  const relatedDashboardsRequest =
    axios.get<RelatedDashboardDataAPI>(relatedDashboardsURL);

  return relatedDashboardsRequest
    .then(
      (relatedDashboardsResponse: AxiosResponse<RelatedDashboardDataAPI>) => ({
        dashboards: relatedDashboardsResponse.data.dashboards,
      })
    )
    .catch((e: AxiosError<RelatedDashboardDataAPI>) => {
      const { response } = e;
      const msg = response?.data?.msg || '';

      return Promise.reject({ msg, dashboards: [] });
    });
}

export function getProviderDescription(providerData: ProviderMetadata) {
  const providerParams = getProviderQueryParams({ key: providerData.key });

  return axios
    .get(`${API_PATH}/get_provider_description?${providerParams}`)
    .then((response: AxiosResponse<DescriptionAPI>) => {
      providerData.description = response.data.description;

      return providerData;
    });
}

export function updateProviderDescription(
  description: string,
  providerData: ProviderMetadata
) {
  return axios.put(`${API_PATH}/put_provider_description`, {
    description,
    key: providerData.key,
    source: 'user',
  });
}




