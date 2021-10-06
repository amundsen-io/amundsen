import axios, { AxiosResponse } from 'axios';

import { ResourceType } from 'interfaces';

export const API_PATH = '/api/metadata/v0';
// TODO - Consider moving 'Bookmarks' under 'User'
// TODO: Define types for the AxiosResponse data

export function addBookmark(
  resourceKey: string,
  resourceType: ResourceType,
  userId: string
) {
  console.log('userId', userId);
  return axios
    .put(`${API_PATH}/user/bookmark?user_id=${userId}`, {
      type: resourceType,
      key: resourceKey,
    })
    .then((response: AxiosResponse) => response.data);
}

export function removeBookmark(
  resourceKey: string,
  resourceType: ResourceType,
  userId: string
) {
  return axios
    .delete(`${API_PATH}/user/bookmark?user_id=${userId}`, {
      data: { type: resourceType, key: resourceKey },
    })
    .then((response: AxiosResponse) => response.data);
}

export function getBookmarks(userId: any) {
  if (userId.payload) userId = userId.payload.userId;
  return axios
    .get(`${API_PATH}/user/bookmark` + (userId ? `?user_id=${userId}` : ''))
    .then((response: AxiosResponse) => response.data);
}
