import axios, { AxiosResponse } from 'axios';

import { sortTagsAlphabetical } from 'ducks/utilMethods';
import { ResourceType, Tag } from 'interfaces';
import { API_PATH, TableDataAPI } from 'ducks/tableMetadata/api/v0';
import { GetDashboardAPI } from 'ducks/dashboard/api/v0';

export type AllTagsAPI = {
  msg: string;
  tags: Tag[];
};

export function getAllTags() {
  return axios
    .get('/api/metadata/v0/tags')
    .then((response: AxiosResponse<AllTagsAPI>) => {
      return response.data.tags.sort(sortTagsAlphabetical);
    });
}

export function getResourceTags(resourceType, uriKey: string) {
  if (resourceType === ResourceType.table) {
    return axios
      .get(`${API_PATH}/table?key=${uriKey}`)
      .then((response: AxiosResponse<TableDataAPI>) => {
        return (response.data.tableData.tags || []).sort(sortTagsAlphabetical);
      });
  }
  if (resourceType === ResourceType.dashboard) {
    return axios
      .get(`${API_PATH}/dashboard?uri=${uriKey}`)
      .then((response: AxiosResponse<GetDashboardAPI>) => {
        return (response.data.dashboard.tags || []).sort(sortTagsAlphabetical);
      });
  }
}

/* TODO: Typing this method generates redux-saga related type errors that needs more dedicated debugging */
// TODO - Unify this API and split the logic in the Flask layer.
export function updateTableTag(
  tagObject,
  resourceType: ResourceType,
  uriKey: string
) {
  let url = '';
  if (resourceType === ResourceType.table) {
    url = `${API_PATH}/update_table_tags`;
  } else if (resourceType === ResourceType.dashboard) {
    url = `${API_PATH}/update_dashboard_tags`;
  }
  return axios({
    url,
    method: tagObject.methodName,
    data: {
      key: uriKey,
      tag: tagObject.tagName,
    },
  });
}
