import { AnnouncementPost } from '../../components/AnnouncementPage/types';
export { AnnouncementPost }

/* API */
export type AnnouncementsResponse = {
  msg: string;
  posts: AnnouncementPost[];
}

/* getAnnouncements */
export enum AnnouncementsGet {
  ACTION = 'amundsen/announcements/GET_ACTION',
  SUCCESS = 'amundsen/announcements/GET_SUCCESS',
  FAILURE = 'amundsen/announcements/GET_FAILURE',
}
export interface AnnouncementsGetRequest {
  type: AnnouncementsGet.ACTION;
}
export interface AnnouncementsGetResponse {
  type: AnnouncementsGet.SUCCESS | AnnouncementsGet.FAILURE;
  payload: AnnouncementPost[];
}
