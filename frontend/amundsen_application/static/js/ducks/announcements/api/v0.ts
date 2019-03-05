import axios, { AxiosResponse, AxiosError } from 'axios';

import { AnnouncementsResponse } from '../types';

export function announcementsGet() {
  return axios({
      method: 'get',
      url: '/api/announcements/v0/',
    })
    .then((response: AxiosResponse<AnnouncementsResponse>) => {
      return response.data.posts;
    })
    .catch((error: AxiosError) => {
      return [];
    });
}
