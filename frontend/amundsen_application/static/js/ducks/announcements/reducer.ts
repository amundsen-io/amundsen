import { AnnouncementPost } from '../../components/AnnouncementPage/types';

export enum AnnouncementsGet {
  ACTION = 'amundsen/announcements/GET_ACTION',
  SUCCESS = 'amundsen/announcements/GET_SUCCESS',
  FAILURE = 'amundsen/announcements/GET_FAILURE',
}

// announcementsGet
export interface AnnouncementsGetRequest {
  type: AnnouncementsGet.ACTION;
}

export function announcementsGet(): AnnouncementsGetRequest {
  return { type: AnnouncementsGet.ACTION };
}

interface AnnouncementsGetResponse {
  type: AnnouncementsGet.SUCCESS | AnnouncementsGet.FAILURE;
  payload: AnnouncementPost[];
}

type AnnouncementsGetAction = AnnouncementsGetRequest | AnnouncementsGetResponse;


export type AnnouncementsReducerAction = AnnouncementsGetAction;

export interface AnnouncementsReducerState {
  posts: AnnouncementPost[];
}
const initialState: AnnouncementsReducerState = {
  posts: []
};

export default function reducer(state: AnnouncementsReducerState = initialState, action: AnnouncementsReducerAction): AnnouncementsReducerState {
  switch (action.type) {
    case AnnouncementsGet.ACTION:
      return state;
    case AnnouncementsGet.SUCCESS:
      return { posts: action.payload };
    case AnnouncementsGet.FAILURE:
      return { posts: [] };
    default:
      return state;
  }
}
