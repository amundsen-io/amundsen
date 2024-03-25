import axios, { AxiosResponse } from 'axios';

import { AnnouncementPost } from 'interfaces';

import { STATUS_CODES } from '../../../constants';

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
      const { data, status } = response;

      return {
        posts: data.posts,
        statusCode: status,
      };
    })
    .catch((e) => {
      const { response } = e;
      const statusCode = response
        ? response.status || STATUS_CODES.INTERNAL_SERVER_ERROR
        : STATUS_CODES.INTERNAL_SERVER_ERROR;

      return Promise.reject({
        posts: [],
        statusCode,
      });
    });
}
