import axios, { AxiosResponse } from 'axios';

import { AnnouncementPost } from 'interfaces';

export type AnnouncementsAPI = {
  msg: string;
  posts: AnnouncementPost[];
};

export function getAnnouncements() {
  return axios({
      method: 'get',
      url: '/api/announcements/v0/',
    })
    .then((response: AxiosResponse<AnnouncementsAPI>) => {
      return response.data.posts;
    })
};
