import axios, { AxiosResponse } from 'axios';

import { AnnouncementPost } from 'interfaces';

export type AnnouncementsResponseAPI = {
  msg: string;
  posts: AnnouncementPost[];
};

export function announcementsGet() {
  return axios({
      method: 'get',
      url: '/api/announcements/v0/',
    })
    .then((response: AxiosResponse<AnnouncementsResponseAPI>) => {
      return response.data.posts;
    })
};
