import {
  AnnouncementsGet, AnnouncementsGetRequest, AnnouncementsGetResponse,
  AnnouncementPost,
} from './types';

export type AnnouncementsReducerAction = AnnouncementsGetRequest | AnnouncementsGetResponse;

export interface AnnouncementsReducerState {
  posts: AnnouncementPost[];
}

export function announcementsGet(): AnnouncementsGetRequest {
  return { type: AnnouncementsGet.ACTION };
}

const initialState: AnnouncementsReducerState = {
  posts: [],
};

export default function reducer(state: AnnouncementsReducerState = initialState, action: AnnouncementsReducerAction): AnnouncementsReducerState {
  switch (action.type) {
    case AnnouncementsGet.FAILURE:
    case AnnouncementsGet.SUCCESS:
      return { posts: action.payload };
    default:
      return state;
  }
}
