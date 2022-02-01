import axios, { AxiosResponse } from 'axios';

import { PopularResource, ResourceDict, ResourceType } from 'interfaces';
import { indexDashboardsEnabled } from 'config/config-utils';

export type PopularTablesAPI = {
  msg: string;
  results: ResourceDict<PopularResource[]>;
};

export function getPopularResources(userId: string) {
  console.log('getPopularResources', userId);
  let resourceType = `${ResourceType.table}`;

  if (indexDashboardsEnabled()) {
    resourceType += `,${ResourceType.dashboard}`;
  }
  return axios
    .get(
      `/api/metadata/v0/popular_resources?user_id=${userId}&types=${resourceType}`
    )
    .then((response: AxiosResponse<PopularTablesAPI>) => response.data.results);
}
